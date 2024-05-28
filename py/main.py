# AetherOnyPy Main Application
# Copyright Isuret Polos 2024
# Support me on https://www.patreon.com/aetherone
import webbrowser
import time
import requests
import multiprocessing
import argparse

from waitress import serve
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS

app = Flask(__name__)
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

def start_server(port):
    serve(app, host='0.0.0.0', port=port)

def wait_for_server(port):
    url = f"http://localhost:{port}"
    while True:
        try:
            response = requests.get(url)
            if response.status_code == 200:
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
    wait_for_server(port)
    webbrowser.open(f"http://localhost:{port}")
    server_process.join() #keep it alive
