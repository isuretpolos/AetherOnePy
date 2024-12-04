# AetherOnyPy Main Application
# Copyright Isuret Polos 2024
# Support me on https://www.patreon.com/aetherone
import os
import webbrowser
import time
import requests
import multiprocessing
import argparse
import qrcode
import io
import socket
import re
import json
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ['FLASK_ENV'] = 'development'

from waitress import serve
from flask import Flask, jsonify, request, send_from_directory, send_file,Response
from flask_cors import CORS
from PIL import Image, ImageDraw, ImageFont
from pprint import pprint
from dateutil import parser

from services.databaseService import get_case_dao, Case

app = Flask(__name__)
port = 80
CORS(app)
if not os.path.isdir("../data"):
    os.makedirs("../data")
caseDAO = get_case_dao('../data/cases.db')

# Angular UI, serving static files
# --------------------------------
@app.route('/')
def index():
    return send_from_directory('../ui/dist/ui/', 'index.html')

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

# @app.route('/case', methods=['GET','POST','PUT','DELETE'])
# def case():
#     if request.method == 'POST':
#         case = request.json
#         pprint(case)
#         if not os.path.exists("data"):
#             os.mkdir("data")
#         fileName = f"data/{sanitize_filename(case["name"])}.json"
#         with open(fileName, "w", encoding='utf-8') as json_file:
#             json.dump(case, json_file, ensure_ascii=False, indent=4)
#         response_data = json.dumps(case, ensure_ascii=False)
#         return Response(response_data, content_type='application/json; charset=utf-8')
#     return "OK"

@app.route('/case', methods=['GET', 'POST', 'PUT', 'DELETE'])
def case():
    if request.method == 'POST':
        case_data = request.json
        pprint(case_data)

        # Convert received JSON data into a Case object
        print("\n\n")
        print(case_data["created"])
        new_case = Case(
            name=case_data["name"],
            email=case_data["email"],
            color=case_data["color"],
            description=case_data["description"],
            created=parser.isoparse(case_data["created"]),
            last_change=parser.isoparse(case_data["lastChange"])
        )

        # Insert the Case object into the database using caseDAO
        caseDAO.insert_case(new_case)

        response_data = json.dumps(case_data, ensure_ascii=False)
        return Response(response_data, content_type='application/json; charset=utf-8')

    if request.method == 'GET':
        allCases = caseDAO.get_all_cases()
        print(allCases)
        response_data = json.dumps(allCases, ensure_ascii=False)
        return Response(response_data, content_type='application/json; charset=utf-8')

    return "OK"


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
                print(f"If your browser does not open automatically, click here http://localhost:{port}")
                webbrowser.open(f"http://localhost:{port}")
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
        caseDAO.close()
        sys.exit(0)
