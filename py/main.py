# AetherOnyPy Main Application
# Copyright Isuret Polos 2024
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

if __name__ == '__main__':
    serve(app, host='0.0.0.0', port=80)
