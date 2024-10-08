# AetherOnyPy Main Application
# Copyright Isuret Polos 2024
# Support me on https://www.patreon.com/aetherone
import webbrowser
import time
import requests
import multiprocessing
import argparse
import qrcode
import io
import socket

from waitress import serve
from flask import Flask, jsonify, request, send_from_directory, send_file
from flask_cors import CORS
from PIL import Image, ImageDraw, ImageFont

app = Flask(__name__)
port = 80
CORS(app)

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

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        prog='AetherOnePy',
        description='Open Source Digital Radionics',
        epilog='Support me on Patreon https://www.patreon.com/aetherone')
    parser.add_argument('-p', '--port', default='80')
    parser.print_help()
    args = vars(parser.parse_args())
    port = args['port']
    print("Starting AetherOnePy server ...")
    server_process = multiprocessing.Process(target=start_server, args=(port,))
    server_process.start()
    wait_for_server_and_open(port)
    server_process.join() #keep it alive
