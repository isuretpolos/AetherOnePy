# AetherOnyPy Main Application
# Copyright Isuret Polos 2025
# Support me on https://www.patreon.com/aetherone
import io, os, sys, multiprocessing
import asyncio
import argparse
from datetime import datetime

import qrcode
import socket
import re
import json
import logging
import urllib.request

from py.services.planetaryInfluence import PlanetaryRulershipCalendarAPI, zodiac_monthly, daily_rulerships

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ['FLASK_ENV'] = 'development'

from flask import Flask, jsonify, request, send_from_directory, send_file, Response
from flask_cors import CORS
from flask_socketio import SocketIO, emit
from PIL import ImageDraw, ImageFont
from dateutil import parser
import importlib

from services.rateCard import RadionicChart
from services.databaseService import get_case_dao
from services.updateRadionicsRates import update_or_clone_repo
from services.rateImporter import RateImporter
from services.hotbitsService import HotbitsService, HotbitsSource
from services.analyzeService import analyze as analyzeService, transformAnalyzeListToDict, checkGeneralVitality
from domains.aetherOneDomains import Analysis, Session, Case, BroadCastData, AnalysisRate
from services.broadcastService import BroadcastService, BroadcastTask


# Start the hotbits service in a separate process
def start_hotbits_service():
    PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    aetherOneDB = get_case_dao(os.path.join(PROJECT_ROOT, 'data/aetherone.db'))
    hotbits = HotbitsService(HotbitsSource.WEBCAM, os.path.join(PROJECT_ROOT, "hotbits"),aetherOneDB,None)
    hotbits.initHotbits()


class AetherOnePy:
    def __init__(self):
        self.PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
        self.app = Flask(__name__)
        self.socketio = SocketIO(self.app, cors_allowed_origins="*", ping_interval=25, ping_timeout=300)
        self.port = 80
        CORS(self.app)
        self.aetherOneDB = get_case_dao(os.path.join(self.PROJECT_ROOT, 'data/aetherone.db'))
        self.hotbits = HotbitsService(HotbitsSource.WEBCAM, os.path.join(self.PROJECT_ROOT, "hotbits"), self.aetherOneDB, self)
        process = multiprocessing.Process(target=start_hotbits_service) # Start the hotbits service in a separate process
        process.daemon = True
        process.start()
        self.setup_logging()
        self.setup_directories()
        self.load_plugins()
        self.setup_routes()
        self.cleanup_broadcast_folder()
        self.planetaryInfoApi = PlanetaryRulershipCalendarAPI()

    def cleanup_broadcast_folder(self):
        broadcast_folder = os.path.join(self.PROJECT_ROOT, "broadcasts")
        for filename in os.listdir(broadcast_folder):
            if filename.endswith(".png") or filename.endswith(".wav"):
                file_path = os.path.join(broadcast_folder, filename)
                try:
                    os.remove(file_path)
                except Exception as e:
                    print(f"Error deleting file {file_path}: {e}")

    def setup_logging(self):
        log = logging.getLogger('werkzeug')
        log.setLevel(logging.ERROR)

    def setup_directories(self):
        if not os.path.isdir(os.path.join(self.PROJECT_ROOT, "data")):
            os.makedirs(os.path.join(self.PROJECT_ROOT, "data"))
        if not os.path.isdir(os.path.join(self.PROJECT_ROOT, "data/private")):
            os.makedirs(os.path.join(self.PROJECT_ROOT, "data/private"))
        if not os.path.isdir(os.path.join(self.PROJECT_ROOT, "hotbits")):
            os.makedirs(os.path.join(self.PROJECT_ROOT, "hotbits"))
        if not os.path.isdir(os.path.join(self.PROJECT_ROOT, "broadcasts")):
            os.makedirs(os.path.join(self.PROJECT_ROOT, "broadcasts"))

    def load_plugins(self):
        PLUGINS_DIR = os.path.join(os.path.dirname(__file__), 'plugins')
        if os.path.exists(PLUGINS_DIR) and os.path.isdir(PLUGINS_DIR):
            plugin_directories = [d for d in os.listdir(PLUGINS_DIR) if os.path.isdir(os.path.join(PLUGINS_DIR, d))]
            for plugin_name in plugin_directories:
                plugin_path = os.path.join(PLUGINS_DIR, plugin_name)
                routes_module_name = f"plugins.{plugin_name}.routes"
                try:
                    routes_module = importlib.import_module(routes_module_name)
                    if hasattr(routes_module, 'create_blueprint'):
                        plugin_blueprint = routes_module.create_blueprint()
                        self.app.register_blueprint(plugin_blueprint, url_prefix=f"/{plugin_name.lower()}")
                        print(f"Plugin '{plugin_name}' routes loaded and registered with prefix '/{plugin_name.lower()}'")
                    else:
                        print(f"Plugin '{plugin_name}' routes module (routes.py) missing 'create_blueprint' function.")
                except ImportError as e:
                    print(f"Error importing routes for plugin '{plugin_name}': {e}")
                except Exception as e:
                    print(f"Error registering blueprint for plugin '{plugin_name}': {e}")
        else:
            print(f"Plugins directory '{PLUGINS_DIR}' not found or is not a directory. Skipping plugin loading.")

    def emitMessage(self, event: str, text: str):
        print(f"EMIT: {event} - {text}")
        try:
            self.socketio.emit(event, {'message': text})
        except Exception as e:
            logging.error(f"Error emitting message: {e}")

    def setup_routes(self):
        # Serving the Angular UI
        @self.app.route('/')
        def index():
            return send_from_directory('../ui/dist/ui/', 'index.html')

        # Serving static files, like images, css, js, etc.
        @self.app.route('/<path:path>')
        def static_files(path):
            return send_from_directory('../ui/dist/ui/', path)

        # Reacting to the websockets connect event, in order to get the UI know you are connected
        @self.socketio.on('connect')
        def handle_connect():
            emit('server_update', {'message': 'Server connected to websockets!'}, broadcast=True)
            emit('broadcast_info', {'message': 'Broadcast messaging ready!'}, broadcast=True)

        # Health check, you make a ping and get a pong
        @self.app.route('/ping', methods=['GET'])
        def ping():
            return "pong"

        # CPU count, in order to know how many CPUs are available and how good is the performance
        @self.app.route('/cpuCount', methods=['GET'])
        def cpuCount():
            return str(multiprocessing.cpu_count())

        # Version, in order to know which version of the software is running
        @self.app.route('/version', methods=['GET'])
        def version():
            try:
                with open(os.path.join(self.PROJECT_ROOT, 'py/version.txt'), "r") as f:
                    return f.read().strip()
            except FileNotFoundError:
                logging.error("Version file not found")
                return "0.0.0"
            except Exception as e:
                logging.error(f"Error reading version file: {e}")
                return "0.0.0"

        # Remote version, in order to know which version of the software is available on the remote repository
        @self.app.route('/remoteVersion', methods=['GET'])
        def remoteVersion():
            try:
                return urllib.request.urlopen("https://raw.githubusercontent.com/isuretpolos/AetherOnePy/refs/heads/main/py/version.txt").read()
            except FileNotFoundError:
                return "0.0.0"

        # QR code, in order to get the QR code for the current IP address and use it to connect to the server with a
        # smartphone or tablet
        @self.app.route('/qrcode', methods=['GET'])
        def get_qrcode():

            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(('8.8.8.8', 1))  # connect() for UDP doesn't send packets
            for ip in s.getsockname():
                print(ip)

            myip = (([ip for ip in socket.gethostbyname_ex(socket.gethostname())[2] if not ip.startswith("127.")] or [[(s.connect(("8.8.8.8", 53)), s.getsockname()[0], s.close()) for s in [socket.socket(socket.AF_INET, socket.SOCK_DGRAM)]][0][1]]) + ["no IP found"])[0]
            data = f"http://{myip}:{self.port}"
            print(data)
            self.socketio.emit('server_update', {'message': data})

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

            text = "AetherOnePy"
            font = ImageFont.truetype("arial.ttf", 16)
            text_width = font.getbbox(text)[2]
            text_height = font.getbbox(text)[3]
            text_position = ((img.size[0] - text_width) // 2, img.size[1] - text_height - 15)
            draw.text(text_position, text, fill='black', font=font)

            font = ImageFont.truetype("arial.ttf", 16)
            text_width = font.getbbox(data)[2]
            text_height = font.getbbox(data)[3]
            text_position = ((img.size[0] - text_width) // 2, img.size[1] - text_height)
            draw.text(text_position, data, fill='black', font=font)

            img_byte_arr = io.BytesIO()
            img.save(img_byte_arr, format='PNG')
            img_byte_arr.seek(0)

            return send_file(img_byte_arr, mimetype='image/png')

        # CRUD operations for cases
        @self.app.route('/case', methods=['GET', 'POST', 'PUT', 'DELETE'])
        def case():
            if request.method == 'POST':
                case_data = request.json
                new_case = Case(
                    name=case_data["name"],
                    email=case_data["email"],
                    color=case_data["color"],
                    description=case_data["description"],
                    created=parser.isoparse(case_data["created"]),
                    last_change=parser.isoparse(case_data["lastChange"])
                )
                user_id = self.aetherOneDB.insert_case(new_case)
                case_data["id"] = user_id
                response_data = json.dumps(case_data, ensure_ascii=False)
                return Response(response_data, content_type='application/json; charset=utf-8')

            if request.method == 'GET':
                allCases = []
                for caseObj in self.aetherOneDB.list_cases():
                    allCases.append(caseObj.to_dict())
                response_data = json.dumps(allCases, ensure_ascii=False)
                return Response(response_data, content_type='application/json; charset=utf-8')

            return "NOT IMPLEMENTED"

        # CRUD operations for sessions
        @self.app.route('/session', methods=['GET', 'POST', 'PUT', 'DELETE'])
        def session():
            if request.method == 'POST':
                new_session = Session.from_dict(request.json)
                if new_session is None:
                    return jsonify({'error': 'No active session found'}), 404
                session_id = self.aetherOneDB.insert_session(new_session)
                session_data = new_session.to_dict()
                session_data['session_id'] = session_id
                response_data = json.dumps(new_session.to_dict(), ensure_ascii=False)
                return Response(response_data, content_type='application/json; charset=utf-8')

            if request.method == 'GET':
                if request.args.get('id') is not None:
                    session = self.aetherOneDB.get_session(int(request.args.get('id')))
                    if session is None:
                        return jsonify({'error': 'No last session found'}), 404
                    response_data = json.dumps(session.to_dict(), ensure_ascii=False)
                    return Response(response_data, content_type='application/json; charset=utf-8')
                if request.args.get('last') is not None:
                    session = self.aetherOneDB.get_last_session(int(request.args.get('caseId')))
                    if session is None:
                        return jsonify({'error': 'No last session found'}), 404
                    response_data = json.dumps(session.to_dict(), ensure_ascii=False)
                    return Response(response_data, content_type='application/json; charset=utf-8')
                else:
                    allSessions = []
                    for session in self.aetherOneDB.list_sessions(int(request.args.get('caseId'))):
                        allSessions.append(session.to_dict())
                    response_data = json.dumps(allSessions, ensure_ascii=False)
                    return Response(response_data, content_type='application/json; charset=utf-8')

            if request.method == 'DELETE':
                self.aetherOneDB.delete_session(int(request.args.get('id')))
                return jsonify({'message': 'Session deleted successfully'}), 200

            return "NOT IMPLEMENTED"

        # CRUD operations for settings
        @self.app.route('/settings', methods=['GET', 'POST'])
        def settings():
            json_file_path = os.path.join(self.PROJECT_ROOT, 'data', 'settings.json')

            if request.method == 'POST':
                settings = request.json
                self.aetherOneDB.ensure_settings_defaults(settings)
                with open(json_file_path, 'w') as f:
                    json.dump(settings, f, indent=4)
                return jsonify(settings), 200

            if request.method == 'GET':
                return self.aetherOneDB.loadSettings(), 200

        # CRUD operations for rates
        @self.app.route('/catalog', methods=['GET', 'POST', 'PUT', 'DELETE'])
        def catalog():
            if request.method == 'GET':
                if request.args.get('id') is not None:
                    catalog = self.aetherOneDB.get_catalog(int(request.args.get('id')))
                    response_data = json.dumps(catalog.to_dict(), ensure_ascii=False)
                    return Response(response_data, content_type='application/json; charset=utf-8')
                else:
                    allCatalogs = []
                    for catalog in self.aetherOneDB.list_catalogs():
                        allCatalogs.append(catalog.to_dict())
                    response_data = json.dumps(allCatalogs, ensure_ascii=False)
                    return Response(response_data, content_type='application/json; charset=utf-8')

            return "NOT IMPLEMENTED"

        # Service operations for rates import from local files
        @self.app.route('/filesToImport', methods=['GET', 'POST'])
        def filesToImport():
            rateImporter = RateImporter(self.aetherOneDB)

            if request.method == 'GET':
                json_result = rateImporter.generate_folder_file_json(os.path.join(self.PROJECT_ROOT, 'data/radionics-rates'))
                return Response(json_result, content_type='application/json; charset=utf-8')

            if request.method == 'POST':
                rateImporter.import_file(os.path.join(self.PROJECT_ROOT, 'data/radionics-rates'), request.args.get('file'))
                json_result = rateImporter.generate_folder_file_json(os.path.join(self.PROJECT_ROOT, 'data/radionics-rates'))
                return Response(json_result, content_type='application/json; charset=utf-8')

            return "NOT IMPLEMENTED"

        # Upload a file with rates
        @self.app.route('/upload', methods=['POST'])
        def upload_file():
            if 'file' not in request.files:
                return jsonify({'error': 'No file part in the request'}), 400

            file = request.files['file']
            if file.filename == '':
                return jsonify({'error': 'No selected file'}), 400

            file.save(os.path.join(self.PROJECT_ROOT, 'data/private', file.filename))
            rateImporter = RateImporter(self.aetherOneDB)
            rateImporter.import_file(os.path.join(self.PROJECT_ROOT, 'data/private'), file.filename)
            return jsonify({'message': 'File uploaded successfully'}), 200

        # Count hotbits, which means the hotbits_<timestamp>.json files in the hotbits folder
        @self.app.route('/countHotbits', methods=['GET'])
        def countHotbits():
            count = self.hotbits.countHotbits()
            return jsonify({'count': count}), 200

        # Trigger collection or generating of hotbits
        @self.app.route('/collectHotBits', methods=['POST'])
        def collectHotbits():
            asyncio.run(self.hotbits.collectHotBits())
            return jsonify({'message': 'collecting hotbits started'}), 200

        # Collect hotbits from the webcam
        @self.app.route('/collectWebCamHotBits', methods=['GET', 'POST'])
        def collectWebCamHotBits():
            if request.method == 'GET':
                return jsonify({'running': self.hotbits.running}), 200
            if request.method == 'POST':
                if self.hotbits.collectWebCamHotBits():
                    return jsonify({'message': 'collecting hotbits with webCam started'}), 200
                else:
                    return jsonify({'message': 'collecting hotbits with webCam failed'}), 500
            return "NOT IMPLEMENTED"

        # Stop collecting hotbits (which means stop the webcam as well)
        @self.app.route('/collectHotBits', methods=['DELETE'])
        def stopCollectingHotbits():
            self.hotbits.stopCollectingHotbits()
            return jsonify({'message': 'collecting hotbits stopped'}), 200

        @self.app.route('/hotbits', methods=['GET'])
        def hotbits():
            hotbits = self.hotbits.getHotbits()
            return jsonify({'hotbits': hotbits}), 200

        # CRUD operations for analysis
        @self.app.route('/analysis', methods=['GET', 'POST', 'PUT', 'DELETE'])
        def analysis():
            if request.method == 'GET':
                if request.args.get('id') is not None:
                    analysis = self.aetherOneDB.get_analysis(int(request.args.get('id')))
                    response_data = json.dumps(analysis.to_dict(), ensure_ascii=False)
                    return Response(response_data, content_type='application/json; charset=utf-8')
                elif request.args.get('last') is not None:
                    analysis = self.aetherOneDB.get_last_analysis(int(request.args.get('session_id')))
                    response_data = json.dumps(analysis.to_dict(), ensure_ascii=False)
                    return Response(response_data, content_type='application/json; charset=utf-8')
                else:
                    analysisList = []
                    for analysis in self.aetherOneDB.list_analysis(int(request.args.get('session_id'))):
                        analysisList.append(analysis.to_dict())
                    response_data = json.dumps(analysisList, ensure_ascii=False)
                    return Response(response_data, content_type='application/json; charset=utf-8')

            if request.method == 'POST':
                analyzeRequest = request.json
                print(analyzeRequest)
                analysis = Analysis(analyzeRequest['note'], analyzeRequest['sessionID'])
                analysis.catalogId = analyzeRequest['catalogId']
                if self.aetherOneDB.get_setting('analysisAlwaysCheckGV'):
                    analysis.target_gv = checkGeneralVitality(self.hotbits)
                analysis = self.aetherOneDB.insert_analysis(analysis)
                response_data = json.dumps(analysis.to_dict(), ensure_ascii=False)
                return Response(response_data, content_type='application/json; charset=utf-8')

            if request.method == 'PUT':
                analyzeRequest = request.json
                analysis = self.aetherOneDB.get_analysis(int(analyzeRequest['id']))
                analysis.note = analyzeRequest['note']
                self.aetherOneDB.update_analysis(analysis)
                response_data = json.dumps(analysis.to_dict(), ensure_ascii=False)
                return Response(response_data, content_type='application/json; charset=utf-8')

            if request.method == 'DELETE':
                self.aetherOneDB.delete_analysis(int(request.args.get('id')))
                return jsonify({'message': 'Analysis deleted successfully'}), 200

            return "NOT IMPLEMENTED"

        # Trigger analysis using the rates from the catalog
        @self.app.route('/analyze', methods=['GET', 'POST'])
        def analyze():
            if request.method == 'GET':
                analysis_id = int(request.args.get('analysis_id'))
                rates_list = self.aetherOneDB.list_rates_for_analysis(analysis_id)
                enhanced_rates = []
                for rate in rates_list:
                    enhanced_rates.append(AnalysisRate(rate.signature, rate.description, rate.catalog_id, analysis_id, rate.energetic_value, rate.gv, rate.level, rate.potency_type, rate.potency, rate.note))
                return jsonify(transformAnalyzeListToDict(enhanced_rates)), 200
            if request.method == 'POST':
                analyzeRequest = request.json
                analysis = self.aetherOneDB.get_analysis(int(analyzeRequest['analysis_id']))
                rates_list = self.aetherOneDB.list_rates_from_catalog(analyzeRequest["catalog_id"])
                enhanced_rates = analyzeService(analysis.id, rates_list, self.hotbits, self.aetherOneDB.get_setting('analysisAlwaysCheckGV'), self.aetherOneDB.get_setting('analysisAdvanced'))
                self.aetherOneDB.insert_rates_for_analysis(enhanced_rates)
                analyzeList = transformAnalyzeListToDict(enhanced_rates)
                return jsonify(analyzeList), 200

            return "NOT IMPLEMENTED"

        # Check the general vitality
        @self.app.route('/checkGV', methods=['GET'])
        def checkGV():
            gv = checkGeneralVitality(self.hotbits)
            return jsonify({'gv': gv}), 200

        # Trigger broadcast of a rate
        @self.app.route('/broadcast', methods=['GET', 'POST', 'PUT', 'DELETE'])
        def broadcast():
            if request.method == 'GET':
                tasks = self.broadcastService.get_tasks()
                return jsonify(tasks), 200
            if request.method == 'POST':
                broadcast_data = request.json
                analysis = self.aetherOneDB.get_analysis(int(broadcast_data['analysis_id']))
                rateObject = self.aetherOneDB.get_rate(int(broadcast_data['rate_id']))
                broadcastData = BroadCastData(False,None, rateObject.signature, 0, 0, broadcast_data['analysis_id'], None,None,broadcast_data['sessionID'],None)
                broadcastTask = BroadcastTask(broadcastData, analysis)
                self.broadcastService.add_task(broadcastTask)
                return jsonify({'message': 'in queue'}), 200
            if request.method == 'DELETE':
                self.broadcastService.stop()
                self.emitMessage("broadcast_info", "All broadcasts stopped")
                return jsonify({'message': 'all broadcasts stopped'}), 200

            return "NOT IMPLEMENTED"

        # Generate a rate card image
        @self.app.route('/rateCard', methods=['GET'])
        def rateCard():
            input_string = request.args.get('rates')
            rates = RadionicChart.parse_input(input_string)
            chart = RadionicChart(request.args.get('rateName'), request.args.get('base'))
            image = chart.draw_chart(rates)
            buffer = io.BytesIO()
            image.save(buffer, format='PNG')
            buffer.seek(0)
            return send_file(buffer, mimetype='image/png')

        @self.app.route("/planetary_info", methods=["GET"])
        def planetary_info():
            now = datetime.now()
            month_name = now.strftime("%B")
            day_name = now.strftime("%A")
            season_data = self.planetaryInfoApi.get_season(now)
            planetary_hour_data = self.planetaryInfoApi.get_planetary_hour(now)

            data = {
                "SEASON": season_data,
                "MONTH": {
                    "month": month_name,
                    "days": (datetime(now.year, now.month % 12 + 1, 1) - datetime(now.year, now.month, 1)).days,
                    "currentDay": now.day,
                    "zodiac": zodiac_monthly[month_name][0],
                    "planet": zodiac_monthly[month_name][1]
                },
                "DAY": {
                    "day": day_name,
                    "planet": daily_rulerships[day_name]
                },
                "HOUR": planetary_hour_data
            }
            return jsonify(data)

        @self.app.route("/planetary_calendar/<int:year>", methods=["GET"])
        def planetary_calendar(year):
            calendar_data = self.planetaryInfoApi.generate_calendar(year)
            return jsonify(calendar_data)

        @self.app.route('/sqlSelect', methods=['POST'])
        def sqlSelect():
            sql = request.json['sql']
            print(sql)
            result = self.aetherOneDB.sqlSelect(sql)
            return jsonify(result), 200


    def sanitize_filename(self, filename: str) -> str:
        safe_characters = re.compile(r'[^a-zA-Z0-9_\-\.]')
        sanitized = safe_characters.sub('_', filename)
        sanitized = sanitized.strip('.')
        return sanitized[:255]

    def run(self, args):
        asyncio.run(update_or_clone_repo(os.path.join(self.PROJECT_ROOT, "data", "radionics-rates"),
                 "https://github.com/isuretpolos/radionics-rates.git"))
        self.broadcastService = BroadcastService(self.hotbits, self)
        try:
            port = args['port']
            self.socketio.run(self.app, host='0.0.0.0', port=port, debug=False)
        except KeyboardInterrupt:
            print("\nStopping AetherOnePy server ...")
            self.aetherOneDB.close()
            sys.exit(0)


if __name__ == '__main__':
    """
    Main application, starts the webserver and provides services for digital radionics
    """
    multiprocessing.set_start_method("spawn")  # Ensures compatibility on Windows
    port = 80
    argParser = argparse.ArgumentParser(
        prog='AetherOnePy',
        description='Open Source Digital Radionics'
    )
    argParser.add_argument('-p', '--port', default='80')
    argParser.print_help()
    args = vars(argParser.parse_args())
    
    print("Starting AetherOnePy server ...")
    cpuCount = multiprocessing.cpu_count()
    print("CPU Count: ", cpuCount)
    print(f"Click here http://localhost:{args['port']} or open the URL in your favorite browser\nSupport me on Patreon https://www.patreon.com/aetherone")
    aetherOnePy = AetherOnePy()
    aetherOnePy.run(args)

    

    
