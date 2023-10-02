from flask import Flask, request, render_template, redirect, url_for
import os
import yaml
from azure.storage.blob import ContainerClient

app = Flask(__name__)

def load_config():
    dir_root = os.path.dirname(os.path.abspath(__file__))
    with open(dir_root + "/config.yaml", "r") as yamlfile:
        return yaml.load(yamlfile, Loader=yaml.FullLoader)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
    config = load_config()
    container_client = ContainerClient.from_connection_string(config["azure_storage_connectionstring"], config["images_container_name"])

    if 'image' not in request.files:
        return redirect(request.url)

    image = request.files['image']

    if image.filename == '':
        return redirect(request.url)

    blob_name = image.filename
    blob_client = container_client.get_blob_client(blob_name)

    if not blob_client.exists():
        blob_client.upload_blob(image)

        return "Image uploaded successfully."
    else:
        return "Image already exists in the container. Skipping upload."

if __name__ == '__main__':
    app.run(debug=True)
