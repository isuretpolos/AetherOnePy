# AetherOnyPy Main Application
# Copyright Isuret Polos 2024
# Support me on https://www.patreon.com/aetherone
import io,os,sys
import time
import requests
import multiprocessing, asyncio
import argparse
import qrcode
import socket
import re
import json

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ['FLASK_ENV'] = 'development'

from waitress import serve
from flask import Flask, jsonify, request, send_from_directory, send_file, Response
from flask_cors import CORS
from flask_socketio import SocketIO, emit
from PIL import ImageDraw, ImageFont
from dateutil import parser

from services.rateCard import RadionicChart
from services.databaseService import get_case_dao, Case
from services.updateRadionicsRates import update_or_clone_repo
from services.rateImporter import RateImporter
from services.hotbitsService import HotbitsService, HotbitsSource
from services.analyzeService import analyze as analyzeService, transformAnalyzeListToDict, checkGeneralVitality
from domains.aetherOneDomains import Analysis, Session

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")
port = 80
CORS(app)
if not os.path.isdir("../data"):
    os.makedirs("../data")
if not os.path.isdir("../data/private"):
    os.makedirs("../data/private")
if not os.path.isdir("../hotbits"):
    os.makedirs("../hotbits")
aetherOneDB = get_case_dao('../data/aetherone.db')
aetherOneDB.get_setting('')
hotbits = HotbitsService(HotbitsSource.WEBCAM, "../hotbits")


# Angular UI, serving static files
# --------------------------------
@app.route('/')
def index():
    return send_from_directory('../ui/dist/ui/', 'index.html')


@socketio.on('connect')
def handle_connect():
    emit('server_update', {'message': 'Welcome!'}, broadcast=True)


@app.route('/<path:path>')
def static_files(path):
    return send_from_directory('../ui/dist/ui/', path)


# --------------------------------

# API of AetherOnePy
# HEALTH CHECKs
@app.route('/ping', methods=['GET'])
def ping():
    return "pong"


@app.route('/qrcode', methods=['GET'])
def get_qrcode():
    data = f"http://{get_local_ip()}:{port}"
    print(data)
    socketio.emit('server_update', {'message': data})

    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(data)
    qr.make(fit=True)

    img = qr.make_image(fill="black", back_color="white")
    draw = ImageDraw.Draw(img)

    # Add text to the image
    text = "AetherOnePy"
    font = ImageFont.truetype("arial.ttf", 16)
    text_width = font.getbbox(text)[2]
    text_height = font.getbbox(text)[3]
    text_position = ((img.size[0] - text_width) // 2, img.size[1] - text_height - 10)
    draw.text(text_position, text, fill='black', font=font)

    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format='PNG')
    img_byte_arr.seek(0)

    return send_file(img_byte_arr, mimetype='image/png')


@app.route('/case', methods=['GET', 'POST', 'PUT', 'DELETE'])
def case():
    if request.method == 'POST':
        case_data = request.json

        # Convert received JSON data into a Case object
        new_case = Case(
            name=case_data["name"],
            email=case_data["email"],
            color=case_data["color"],
            description=case_data["description"],
            created=parser.isoparse(case_data["created"]),
            last_change=parser.isoparse(case_data["lastChange"])
        )

        # Insert the Case object into the database using aetherOneDB
        aetherOneDB.insert_case(new_case)

        response_data = json.dumps(case_data, ensure_ascii=False)
        return Response(response_data, content_type='application/json; charset=utf-8')

    if request.method == 'GET':
        allCases = []
        for caseObj in aetherOneDB.list_cases():
            allCases.append(caseObj.to_dict())
        response_data = json.dumps(allCases, ensure_ascii=False)
        return Response(response_data, content_type='application/json; charset=utf-8')

    return "NOT IMPLEMENTED"


@app.route('/session', methods=['GET', 'POST', 'PUT', 'DELETE'])
def session():
    if request.method == 'POST':
        new_session = Session.from_dict(request.json)
        # Insert the Session object into the database using aetherOneDB
        aetherOneDB.insert_session(new_session)

        response_data = json.dumps(new_session.to_dict(), ensure_ascii=False)
        return Response(response_data, content_type='application/json; charset=utf-8')

    if request.method == 'GET':
        if request.args.get('id') is not None:
            session = aetherOneDB.get_session(int(request.args.get('id')))
            if session is None:
                return jsonify({'error': 'No last session found'}), 404
            response_data = json.dumps(session.to_dict(), ensure_ascii=False)
            return Response(response_data, content_type='application/json; charset=utf-8')
        if request.args.get('last') is not None:
            session = aetherOneDB.get_last_session(int(request.args.get('caseId')))
            if session is None:
                return jsonify({'error': 'No last session found'}), 404
            response_data = json.dumps(session.to_dict(), ensure_ascii=False)
            return Response(response_data, content_type='application/json; charset=utf-8')
        else:
            allSessions = []
            for session in aetherOneDB.list_sessions(int(request.args.get('caseId'))):
                allSessions.append(session.to_dict())
            response_data = json.dumps(allSessions, ensure_ascii=False)
            return Response(response_data, content_type='application/json; charset=utf-8')

    if request.method == 'DELETE':
        aetherOneDB.delete_session(int(request.args.get('id')))
        return jsonify({'message': 'Session deleted successfully'}), 200

    return "NOT IMPLEMENTED"


@app.route('/settings', methods=['GET', 'POST'])
def settings():
    json_file_path = os.path.join('..', 'data', 'settings.json')

    if request.method == 'POST':
        settings = request.json
        aetherOneDB.ensure_settings_defaults(settings)
        with open(json_file_path, 'w') as f:
            json.dump(settings, f, indent=4)
        return jsonify(settings), 200

    if request.method == 'GET':
        return aetherOneDB.loadSettings(), 200


@app.route('/catalog', methods=['GET', 'POST', 'PUT', 'DELETE'])
def catalog():
    if request.method == 'GET':
        allCatalogs = []
        for catalog in aetherOneDB.list_catalogs():
            allCatalogs.append(catalog.to_dict())
        response_data = json.dumps(allCatalogs, ensure_ascii=False)
        return Response(response_data, content_type='application/json; charset=utf-8')

    return "NOT IMPLEMENTED"


@app.route('/filesToImport', methods=['GET', 'POST'])
def filesToImport():
    rateImporter = RateImporter(aetherOneDB)

    if request.method == 'GET':
        json_result = rateImporter.generate_folder_file_json('../data/radionics-rates')
        return Response(json_result, content_type='application/json; charset=utf-8')

    if request.method == 'POST':
        rateImporter.import_file('../data/radionics-rates', request.args.get('file'))
        json_result = rateImporter.generate_folder_file_json('../data/radionics-rates')
        return Response(json_result, content_type='application/json; charset=utf-8')

    return "NOT IMPLEMENTED"


@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part in the request'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    # Save the file
    file.save(os.path.join('../data/private', file.filename))
    rateImporter = RateImporter(aetherOneDB)
    rateImporter.import_file('../data/private', file.filename)
    return jsonify({'message': 'File uploaded successfully'}), 200


@app.route('/countHotbits', methods=['GET'])
def countHotbits():
    count = hotbits.countHotbits()
    return jsonify({'count': count}), 200


@app.route('/collectHotBits', methods=['POST'])
def collectHotbits():
    asyncio.run(hotbits.collectHotBits())
    return jsonify({'message': 'collecting hotbits started'}), 200


@app.route('/collectHotBits', methods=['DELETE'])
def stopCollectingHotbits():
    hotbits.stopCollectingHotbits()
    return jsonify({'message': 'collecting hotbits stopped'}), 200


@app.route('/analysis', methods=['GET', 'POST', 'PUT', 'DELETE'])
def analysis():
    if request.method == 'GET':
        if request.args.get('id') is not None:
            analysis = aetherOneDB.get_analysis(int(request.args.get('id')))
            response_data = json.dumps(analysis.to_dict(), ensure_ascii=False)
            return Response(response_data, content_type='application/json; charset=utf-8')
        elif request.args.get('last') is not None:
            analysis = aetherOneDB.get_last_analysis(int(request.args.get('sessionId')))
            response_data = json.dumps(analysis.to_dict(), ensure_ascii=False)
            return Response(response_data, content_type='application/json; charset=utf-8')
        else:
            analysisList = []
            for analysis in aetherOneDB.list_analysis(int(request.args.get('session_id'))):
                analysisList.append(analysis.to_dict())
            response_data = json.dumps(analysisList, ensure_ascii=False)
            return Response(response_data, content_type='application/json; charset=utf-8')

    if request.method == 'POST':
        analyzeRequest = request.json
        analysis = Analysis(analyzeRequest['note'],analyzeRequest['sessionID'])
        analysis.catalogId = analyzeRequest['catalogId']
        if aetherOneDB.get_setting('analysisAlwaysCheckGV'):
            analysis.target_gv = checkGeneralVitality(hotbits)
        analysis = aetherOneDB.insert_analysis(analysis)
        response_data = json.dumps(analysis.to_dict(), ensure_ascii=False)
        return Response(response_data, content_type='application/json; charset=utf-8')

    if request.method == 'PUT':
        analyzeRequest = request.json
        analysis = aetherOneDB.get_analysis(int(analyzeRequest['id']))
        analysis.note = analyzeRequest['note']
        aetherOneDB.update_analysis(analysis)
        response_data = json.dumps(analysis.to_dict(), ensure_ascii=False)
        return Response(response_data, content_type='application/json; charset=utf-8')

    if request.method == 'DELETE':
        aetherOneDB.delete_analysis(int(request.args.get('id')))
        return jsonify({'message': 'Analysis deleted successfully'}), 200

    return "NOT IMPLEMENTED"


@app.route('/analyze', methods=['GET', 'POST'])
def analyze():
    if request.method == 'GET':
        rates_list = aetherOneDB.list_rates_for_analysis(int(request.args.get('analysis_id')))
        analyzeList = transformAnalyzeListToDict(rates_list)
        return jsonify(analyzeList), 200
    if request.method == 'POST':
        analyzeRequest = request.json
        analysis = aetherOneDB.get_analysis(int(analyzeRequest['analysis_id']))
        rates_list = aetherOneDB.list_rates_from_catalog(analyzeRequest["catalog_id"])
        enhanced_rates = analyzeService(analysis.id, rates_list, hotbits, True)
        aetherOneDB.insert_rates_for_analysis(enhanced_rates)
        analyzeList = transformAnalyzeListToDict(enhanced_rates)
        return jsonify(analyzeList), 200

    return "NOT IMPLEMENTED"


@app.route('/checkGV', methods=['GET'])
def checkGV():
    gv = checkGeneralVitality(hotbits)
    return jsonify({'gv': gv}), 200


@app.route('/rateCard', methods=['GET'])
def rateCard():
    input_string = request.args.get('rates')
    rates = RadionicChart.parse_input(input_string)
    chart = RadionicChart(request.args.get('rateName'), request.args.get('base'))
    image = chart.draw_chart(rates)
    buffer = io.BytesIO()
    image.save(buffer, format='PNG')
    buffer.seek(0)
    return send_file(buffer, mimetype='image/png')


def get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # doesn't even have to be reachable
        s.connect(('10.254.254.254', 1))
        local_ip = s.getsockname()[0]
    except Exception:
        local_ip = '127.0.0.1'
    finally:
        s.close()
    return local_ip


def start_server(port):
    serve(app, host='0.0.0.0', port=port)


def wait_for_server_and_open(port):
    url = f"http://localhost:{port}"
    while True:
        try:
            response = requests.get(url)
            if response.status_code == 200:
                print(f"Click here http://localhost:{port} or open the URL in your favorite browser")
                # webbrowser.open(f"http://localhost:{port}")
                break
        except requests.ConnectionError:
            pass
        time.sleep(1)


def sanitize_filename(filename: str) -> str:
    """
    Sanitize a given filename to make it safe for saving as a file.
    Removes or replaces characters that are not allowed in filenames.
    """
    # Define a set of safe characters (alphanumeric, dash, underscore, dot)
    safe_characters = re.compile(r'[^a-zA-Z0-9_\-\.]')

    # Replace any unsafe characters with an underscore
    sanitized = safe_characters.sub('_', filename)

    # Ensure the filename does not start or end with a dot
    sanitized = sanitized.strip('.')

    # Truncate the filename to a reasonable length (e.g., 255 characters)
    return sanitized[:255]


if __name__ == '__main__':

    update_or_clone_repo(os.path.join("../data", "radionics-rates"),
                         "https://github.com/isuretpolos/radionics-rates.git")

    argParser = argparse.ArgumentParser(
        prog='AetherOnePy',
        description='Open Source Digital Radionics',
        epilog='Support me on Patreon https://www.patreon.com/aetherone'
    )
    argParser.add_argument('-p', '--port', default='80')
    argParser.print_help()
    args = vars(argParser.parse_args())
    port = args['port']

    print("Starting AetherOnePy server ...")

    try:
        server_process = multiprocessing.Process(target=start_server, args=(port,))
        server_process.start()
        wait_for_server_and_open(port)
        server_process.join()  # keep it alive
    except KeyboardInterrupt:
        print("\nStopping AetherOnePy server ...")
        server_process.terminate()  # Ensure server stops properly
        server_process.join()
        aetherOneDB.close()
        sys.exit(0)
