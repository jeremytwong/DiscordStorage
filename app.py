from flask import Flask, request, render_template, send_file
import requests
import io
from concurrent.futures import ThreadPoolExecutor


executor = ThreadPoolExecutor(max_workers=5)
app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    file = request.files['file']
    file_in_memory = io.BytesIO(file.read())
    file_in_memory.name = file.filename
    requests.post('http://localhost:5001/send_file', files={'file': file_in_memory})
    return 'File uploaded and sent to Discord successfully'

@app.route('/download', methods=['GET'])
def download_file():
    filename = request.args.get('filename')  # get the filename from the query parameters
    if filename is None:
        return 'No filename provided', 400

    response = requests.get(f'http://localhost:5001/retrieve_file?filename={filename}')

    if response.status_code == 404:
        return 'File not found', 404

    return response.content

if __name__ == '__main__':
    app.run(port=5000, debug=True)