from flask import Flask, send_from_directory
import os

app = Flask(__name__)

WEB_DIR = os.path.dirname(os.path.abspath(__file__))

@app.route('/')
def index():
    return send_from_directory(WEB_DIR, 'home.html')

@app.route('/<path:filename>')
def serve_static(filename):
    return send_from_directory(WEB_DIR, filename)

if __name__ == '__main__':
    app.run(host='localhost', port=8080, debug=True)
