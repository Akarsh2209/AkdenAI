import os
import json
from flask import Flask, request, render_template, redirect, url_for, jsonify
from werkzeug.utils import secure_filename
from flask_uploads import UploadSet, configure_uploads, IMAGES

app = Flask(__name__)
app.config['UPLOADED_IMAGES_DEST'] = 'uploads'

images = UploadSet('images', IMAGES)
configure_uploads(app, images)

PASSWORD = "akarshAIkaiden"
DEFINITIONS_FILE = 'definitions.json'

def create_pixel_name(color, location):
    color_str = f"{color[0]}_{color[1]}_{color[2]}"
    location_str = f"{location[0]}x{location[1]}"
    pixel_name = f"{color_str}__{location_str}"
    return pixel_name

def store_definition(pixel_data, definition, password):
    if password != PASSWORD:
        return {"error": "Invalid password"}

    try:
        with open(DEFINITIONS_FILE, 'r') as file:
            definitions = json.load(file)
    except FileNotFoundError:
        definitions = {}

    definitions[str(pixel_data)] = definition

    with open(DEFINITIONS_FILE, 'w') as file:
        json.dump(definitions, file, indent=4)

    return {"message": "Definition stored successfully"}

def retrieve_definitions(password):
    if password != PASSWORD:
        return {"error": "Invalid password"}

    try:
        with open(DEFINITIONS_FILE, 'r') as file:
            definitions = json.load(file)
    except FileNotFoundError:
        definitions = {}

    return {k: v for k, v in definitions.items()}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
    password = request.form['password']
    if password != PASSWORD:
        return jsonify({"error": "Invalid password"}), 403

    image = request.files['image']
    definition = request.form['definition']

    if image and definition:
        filename = images.save(image)
        definitions = retrieve_definitions(PASSWORD)
        definitions[filename] = definition
        store_definition(definitions, definition, PASSWORD)
        return redirect(url_for('index'))
    else:
        return jsonify({"error": "Missing image or definition"}), 400

@app.route('/definitions', methods=['GET'])
def get_definitions():
    password = request.args.get('password')
    if password != PASSWORD:
        return jsonify({"error": "Invalid password"}), 403

    definitions = retrieve_definitions(PASSWORD)
    return jsonify(definitions)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')