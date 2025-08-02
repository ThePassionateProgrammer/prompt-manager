#!/usr/bin/env python3
"""
Simple test to verify Flask routes are working.
"""

from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/')
def index():
    return "Hello World!"

@app.route('/export')
def export():
    return jsonify({"message": "Export route working!"})

@app.route('/test')
def test():
    return "Test route working!"

if __name__ == '__main__':
    app.run(debug=True, port=8001) 