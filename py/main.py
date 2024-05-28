# AetherOnyPy Main Application
# Copyright Isuret Polos 2024
import subprocess
import sys
import webbrowser
import time
import requests
import multiprocessing

required_packages = [
    'Flask',
    'flask-cors',
    'waitress'
]

def install_package(package):
    subprocess.check_call([sys.executable, '-m', 'pip', 'install', package])

def check_and_install_packages():
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            install_package(package)

from waitress import serve
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Sample data
books = [
    {"id": 1, "title": "Python Programming", "author": "John Smith"},
    {"id": 2, "title": "Web Development with Flask", "author": "Jane Doe"}
]

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

# GET method to retrieve a specific book by ID
@app.route('/books/<int:id>', methods=['GET'])
def get_book(id):
    book = next((book for book in books if book['id'] == id), None)
    if book:
        return jsonify(book)
    else:
        return jsonify({"error": "Book not found"}), 404

# POST method to add a new book
@app.route('/books', methods=['POST'])
def add_book():
    data = request.json
    books.append(data)
    return jsonify({"message": "Book added successfully"}), 201

# PUT method to update an existing book
@app.route('/books/<int:id>', methods=['PUT'])
def update_book(id):
    data = request.json
    book = next((book for book in books if book['id'] == id), None)
    if book:
        book.update(data)
        return jsonify({"message": "Book updated successfully"})
    else:
        return jsonify({"error": "Book not found"}), 404

# DELETE method to delete a book by ID
@app.route('/books/<int:id>', methods=['DELETE'])
def delete_book(id):
    global books
    books = [book for book in books if book['id'] != id]
    return jsonify({"message": "Book deleted successfully"})



def start_server():
    serve(app, host='0.0.0.0', port=80)

def wait_for_server():
    url = "http://localhost"
    while True:
        try:
            response = requests.get(url)
            if response.status_code == 200:
                break
        except requests.ConnectionError:
            pass
        time.sleep(1)

if __name__ == '__main__':
    check_and_install_packages()
    server_process = multiprocessing.Process(target=start_server)
    server_process.start()
    print("Starting webBrowser ...")
    wait_for_server()
    webbrowser.open("http://localhost")
    server_process.join() #keep it alive
