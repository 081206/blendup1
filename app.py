from flask import Flask, send_from_directory
import os

app = Flask(__name__, static_folder='frontend')

@app.route('/')
def serve_index():
    return send_from_directory('frontend', 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    if os.path.exists(os.path.join('frontend', path)):
        return send_from_directory('frontend', path)
    return send_from_directory('frontend', 'index.html')

if __name__ == '__main__':
    app.run(debug=True, host='localhost', port=5000)
