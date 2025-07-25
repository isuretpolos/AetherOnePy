# AetherOnyPy Main Application
# Copyright Isuret Polos 2025
# Support me on https://www.patreon.com/aetherone
import io, os, sys, multiprocessing, subprocess
import asyncio
import argparse
import platform as sys_platform
import qrcode
import socket
import re
import json
import logging
import urllib.request
import psutil
from flasgger import Swagger

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ['FLASK_ENV'] = 'development'

from flask import Flask, jsonify, request, send_from_directory, send_file, Response, abort
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
from services.planetaryInfluence import PlanetaryRulershipCalendarAPI
from openai import OpenAI
from setup import check_and_install_packages


# Start the hotbits service in a separate process
def start_hotbits_service():
    PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    aetherOneDB = get_case_dao(os.path.join(PROJECT_ROOT, 'data/aetherone.db'))
    hotbits = HotbitsService(HotbitsSource.WEBCAM, os.path.join(PROJECT_ROOT, "hotbits"),aetherOneDB,None)
    hotbits.initHotbits()


class AetherOnePy:
    def __init__(self):
        self.PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
        self.raspberryPi = self.is_raspberry_pi()
        if self.raspberryPi:
            print("This system is a Raspberry Pi.")
        self.setup_directories()
        self.aetherOneDB = get_case_dao(os.path.join(self.PROJECT_ROOT, 'data/aetherone.db'))
        self.hotbits = HotbitsService(HotbitsSource.WEBCAM, os.path.join(self.PROJECT_ROOT, "hotbits"), self.aetherOneDB, self, self.raspberryPi)
        process = multiprocessing.Process(target=start_hotbits_service) # Start the hotbits service in a separate process
        process.daemon = True
        process.start()
        self.app = Flask(__name__)
        self.app.case_dao = self.aetherOneDB 
        Swagger(self.app)
        self.socketio = SocketIO(self.app, cors_allowed_origins="*", ping_interval=10, ping_timeout=300, debug=False)
        self.port = 80
        CORS(self.app)
        self.setup_logging()
        self.load_plugins()
        self.setup_routes()
        self.cleanup_broadcast_folder()
        self.planetaryInfoApi = PlanetaryRulershipCalendarAPI()


    def is_raspberry_pi(self):
        """Check if the computer is a Raspberry Pi."""
        try:
            # Check the platform
            if sys_platform.system() != "Linux":
                return False

            # Check for the presence of Raspberry Pi-specific files
            if os.path.exists('/sys/firmware/devicetree/base/model'):
                with open('/sys/firmware/devicetree/base/model', 'r') as model_file:
                    model_info = model_file.read().lower()
                    print(model_info)
                    if 'raspberry pi' in model_info:
                        return True

            # Check the CPU information for Raspberry Pi specific hardware
            with open('/proc/cpuinfo', 'r') as cpuinfo:
                for line in cpuinfo:
                    print(line)
                    if 'Hardware' in line and 'BCM' in line:
                        return True
                    if 'Model' in line and 'Raspberry Pi' in line:
                        return True
        except Exception as e:
            print(f"Error while checking Raspberry Pi: {e}")
        return False

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
        try:
            self.socketio.emit(event, {'message': text})
        except Exception as e:
            logging.error(f"Error emitting message: {e}")

    def setup_routes(self):
        # Serving the Angular UI
        @self.app.route('/')
        def index():
            return send_from_directory('../ui/dist/ui/browser/', 'index.html')

        # Health check, you make a ping and get a pong
        @self.app.route('/ping', methods=['GET'])
        def ping():

            system_info = {
                'system': sys_platform.system(),
                'release': sys_platform.release(),
                'version': sys_platform.version(),
                'architecture': sys_platform.architecture(),
                'processor': sys_platform.processor(),
                'cpu_count': psutil.cpu_count(logical=True),
                'memory': psutil.virtual_memory().total,
                'disk': psutil.disk_usage('/').total,
                'raspberryPi': self.raspberryPi,
                'esp32available': False,
                'arduinoavailable': False,
            }
            return jsonify(system_info)

        # Serving static files, like images, css, js, etc.
        @self.app.route('/<path:path>')
        def static_files(path):
            if path.startswith('socket.io'):
                abort(404)
            return send_from_directory('../ui/dist/ui/browser/', path)

        # Reacting to the websockets connect event, in order to get the UI know you are connected
        @self.socketio.on('connect')
        def handle_connect():
            emit('server_update', {'message': 'Server connected to websockets!'}, broadcast=True)
            emit('broadcast_info', {'message': 'Broadcast messaging ready!'}, broadcast=True)

        @self.socketio.on('ping')
        def handle_ping():
            logging.info('Received ping event')
            emit('pong')

        # Restart application
        # First get the new code from the repository
        # Second check and install the required packages
        # Finally restart the application
        @self.app.route('/restart', methods=['POST'])
        def restart():
            subprocess.run(["git", "pull"])
            check_and_install_packages()
            python = sys.executable
            os.execl(python, python, * sys.argv)
            return jsonify({'message': 'Restarting server ...'}), 200

        @self.app.route('/shutdown', methods=['POST'])
        def shutdown():
            print("Shutting down server ...")
            try:
                self.aetherOneDB.close()
                os._exit(0)
                os.kill(os.getpid(), 9)
            except Exception as e:
                print(e)
                logging.error(f"Error shutting down server: {e}")


            return jsonify({'message': 'Shutting down server ...'}), 200

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

            myip = (([ip for ip in socket.gethostbyname_ex(socket.gethostname())[2] if not ip.startswith("127.")] or [[(s.connect(("8.8.8.8", 53)), s.getsockname()[0], s.close()) for s in [socket.socket(socket.AF_INET, socket.SOCK_DGRAM)]][0][1]]) + ["no IP found"])[0]
            data = f"http://{myip}:{self.port}"
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

            if request.method == 'DELETE':
                self.aetherOneDB.delete_case(int(request.args.get('id')))
                return jsonify({'message': 'Case deleted successfully'}), 200

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
                    if analysis is None:
                        return jsonify({"error": "Analysis not found"}), 404
                    response_data = json.dumps(analysis.to_dict(), ensure_ascii=False)
                    return Response(response_data, content_type='application/json; charset=utf-8')
                elif request.args.get('last') is not None:
                    analysis = self.aetherOneDB.get_last_analysis(int(request.args.get('session_id')))
                    if analysis is None:
                        return jsonify({"error": "Analysis not found"}), 404
                    response_data = json.dumps(analysis.to_dict(), ensure_ascii=False)
                    return Response(response_data, content_type='application/json; charset=utf-8')
                else:
                    analysisList = []
                    for analysis in self.aetherOneDB.list_analysis(int(request.args.get('session_id'))):
                        analysisList.append(analysis.to_dict())
                    response_data = json.dumps(analysisList, ensure_ascii=False)
                    return Response(response_data, content_type='application/json; charset=utf-8')

            if request.method == 'POST':
                # Create a new analysis object, which later will be analyzed by the method analyze()
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
                if analysis is None:
                    return jsonify({"error": "Analysis not found"}), 404
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
                    enhanced_rate = AnalysisRate(rate.signature, rate.description, rate.catalog_id, analysis_id, rate.energetic_value, rate.gv, rate.level, rate.potency_type, rate.potency, rate.note)
                    enhanced_rate.id = rate.id
                    enhanced_rates.append(enhanced_rate)
                return jsonify(transformAnalyzeListToDict(enhanced_rates)), 200
            if request.method == 'POST':
                analyzeRequest = request.json
                analysis = self.aetherOneDB.get_analysis(int(analyzeRequest['analysis_id']))
                print(f"[DEBUG] analyzeRequest: {analyzeRequest}")
                print(f"[DEBUG] analysis: {analysis}")
                rates_list = self.aetherOneDB.list_rates_from_catalog(analyzeRequest["catalog_id"])
                print(f"[DEBUG] rates_list: {rates_list}")
                enhanced_rates = analyzeService(analysis.id, rates_list, self.hotbits, self.aetherOneDB.get_setting('analysisAlwaysCheckGV'), self.aetherOneDB.get_setting('analysisAdvanced'))
                print(f"[DEBUG] enhanced_rates: {enhanced_rates}")
                self.aetherOneDB.insert_rates_for_analysis(enhanced_rates)
                print(f"[DEBUG] enhanced_rates: {enhanced_rates}")
                analyzeList = transformAnalyzeListToDict(enhanced_rates)
                print(f"[DEBUG] analyzeList: {analyzeList}")
                return jsonify(analyzeList), 200

            return "NOT IMPLEMENTED"

        @self.app.route('/checkGV', methods=['GET', 'POST'])
        def checkGV():
            # Single check
            if request.method == 'GET':
                gv = checkGeneralVitality(self.hotbits)
                return jsonify({'gv': gv}), 200

            # Check and update entire analysis
            if request.method == 'POST':
                analysis:Analysis = self.aetherOneDB.get_analysis(int(request.json['id']))
                rates_list = self.aetherOneDB.list_rates_for_analysis(analysis.id)
                analysis.target_gv = checkGeneralVitality(self.hotbits)
                analysis = self.aetherOneDB.insert_analysis(analysis)
                enhanced_rates = []
                for rate in rates_list:
                    enhanced_rates.append(AnalysisRate(rate.signature, rate.description, rate.catalog_id, analysis.id, rate.energetic_value, checkGeneralVitality(self.hotbits), rate.level, rate.potency_type, rate.potency, rate.note))
                self.aetherOneDB.insert_rates_for_analysis(enhanced_rates)
                response_data = json.dumps(analysis.to_dict(), ensure_ascii=False)
                return Response(response_data, content_type='application/json; charset=utf-8')
            return "NOT IMPLEMENTED"

        @self.app.route('/openAiModels', methods=['GET'])
        def openAiModels():
            openAiKey = self.aetherOneDB.get_setting('openAiKey')
            if openAiKey is None:
                return jsonify({'error': 'No OpenAI key found'}), 500
            client = OpenAI(api_key=openAiKey)
            try:
                models = client.models.list()
                print(models)
                model_names = [model.id for model in models.data]
                return jsonify(model_names)
            except Exception as e:
                return jsonify({"error": str(e)}), 500

        @self.app.route('/openAiInterpretation', methods=['POST'])
        def openAiInterpretation():
            openAiKey = self.aetherOneDB.get_setting('openAiKey')
            if openAiKey is None:
                return jsonify({'error': 'No OpenAI key found'}), 500
            client = OpenAI(api_key=openAiKey)
            data = request.get_json()
            userContent = self.aetherOneDB.get_setting('openAiSystemContent')
            user_prompt = f"{userContent}\n\n{data}"

            try:
                print(user_prompt)
                response = client.chat.completions.create(
                    model="chatgpt-4o-latest",
                    messages=[
                        {"role": "system", "content": self.aetherOneDB.get_setting('openAiSystemContent')},
                        {"role": "user", "content": user_prompt}
                    ],
                    temperature=0.5
                )
                print(response)
                # Structure a detailed response
                detailed_output = {
                    "id": response.id,
                    "model": response.model,
                    "usage": {
                        "prompt_tokens": response.usage.prompt_tokens,
                        "completion_tokens": response.usage.completion_tokens,
                        "total_tokens": response.usage.total_tokens
                    },
                    "message": response.choices[0].message.content
                }

                return jsonify(detailed_output)

            except Exception as e:
                return jsonify({"error": str(e)}), 500


        # Trigger broadcast of a rate
        @self.app.route('/broadcast', methods=['GET', 'POST', 'PUT', 'DELETE'])
        def broadcast():
            if request.method == 'GET':
                tasks = self.broadcastService.get_tasks()
                current_task = self.broadcastService.get_current_task()
                if current_task:
                    tasks.insert(0,current_task)
                return jsonify(tasks), 200
            if request.method == 'POST':
                broadcast_data = request.json
                print(broadcast_data)
                if (broadcast_data['analysis_id']):
                    analysis = self.aetherOneDB.get_analysis(int(broadcast_data['analysis_id']))
                    rateObject = self.aetherOneDB.get_rate(int(broadcast_data['rate_id']))
                    broadcastData = BroadCastData(False, '', rateObject.signature, 0, 0, broadcast_data['analysis_id'], None,None,broadcast_data['sessionID'],None)
                    broadcastTask = BroadcastTask(broadcastData, analysis)
                else:
                    broadcastData = BroadCastData(False, broadcast_data['intention'], broadcast_data['signature'], 0, 0)
                    broadcastTask = BroadcastTask(broadcastData)
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
            return jsonify(self.planetaryInfoApi.planetary_info().to_dict())

        @self.app.route("/planetary_calendar/<int:year>", methods=["GET"])
        def planetary_calendar(year):
            calendar_data = self.planetaryInfoApi.generate_calendar(year).to_dict()
            return jsonify(calendar_data)

        @self.app.route('/sqlSelect', methods=['POST'])
        def sqlSelect():
            sql = request.json['sql']
            result = self.aetherOneDB.sqlSelect(sql)
            return jsonify(result), 200

        @self.app.route('/plugins', methods=['GET'])
        def list_plugins():
            """
            List all available plugins in the plugins directory.
            """
            plugins_dir = os.path.join(os.path.dirname(__file__), 'plugins')
            try:
                plugins = [
                    name for name in os.listdir(plugins_dir)
                    if os.path.isdir(os.path.join(plugins_dir, name)) and not name.startswith('__')
                ]
                return jsonify({"status": "success", "plugins": plugins})
            except Exception as e:
                return jsonify({"status": "error", "message": str(e)}), 500


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
    #cpuCount = multiprocessing.cpu_count() --> on Ubuntu Windows Subsystem it produces an endless loop of stupidity
    #print("CPU Count: ", cpuCount)
    print(f"Click here http://localhost:{args['port']} or open the URL in your favorite browser\nSupport me on Patreon https://www.patreon.com/aetherone")
    aetherOnePy = AetherOnePy()
    aetherOnePy.run(args)

    

    
