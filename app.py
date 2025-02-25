from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import os
import uuid
import json  # Added missing import
import cv2
import numpy as np
from model import NoiseRemovalModel

def create_directories():
    os.makedirs('static/uploads', exist_ok=True)
    os.makedirs('static/processed', exist_ok=True)

app = Flask(__name__, static_folder='static')
CORS(app)

UPLOAD_FOLDER = 'static/uploads'
PROCESSED_FOLDER = 'static/processed'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

create_directories()
noise_removal_model = NoiseRemovalModel()

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def home():
    return render_template('index.html')  # Ensure this file exists in templates folder

@app.route('/process_image', methods=['POST'])
def process_image():
    if 'image' not in request.files:
        return jsonify({'error': 'No image provided'}), 400

    file = request.files['image']
    if file.filename == '' or not allowed_file(file.filename):
        return jsonify({'error': 'Invalid file format'}), 400

    filename = str(uuid.uuid4()) + os.path.splitext(file.filename)[1]
    file_path = os.path.join(UPLOAD_FOLDER, filename)
    file.save(file_path)

    area = request.form.get('area', 'full')
    selection_rect = json.loads(request.form.get('selectionRect', '{}')) if area == 'custom' else None
    
    processed_image = process_with_ai(file_path, area, selection_rect)
    processed_filename = 'processed_' + filename
    processed_path = os.path.join(PROCESSED_FOLDER, processed_filename)
    cv2.imwrite(processed_path, processed_image)

    return jsonify({'processed_image_url': f'/static/processed/{processed_filename}'})

@app.route('/apply_filter', methods=['GET'])
def apply_filter():
    image_url = request.args.get('image_url')
    filter_name = request.args.get('filter')
    
    if not image_url or not filter_name:
        return jsonify({'error': 'Image URL and filter name are required'}), 400
    
    filename = os.path.basename(image_url)
    image_path = os.path.join(PROCESSED_FOLDER, filename)
    
    if not os.path.exists(image_path):
        return jsonify({'error': 'Image not found'}), 404
    
    filtered_image = apply_image_filter(image_path, filter_name)
    filtered_filename = f"{filter_name}_{filename}"
    filtered_path = os.path.join(PROCESSED_FOLDER, filtered_filename)
    cv2.imwrite(filtered_path, filtered_image)
    
    return jsonify({'filtered_image_url': f'/static/processed/{filtered_filename}'})

def process_with_ai(image_path, area='full', selection_rect=None):
    image = cv2.imread(image_path)
    if area == 'full':
        return noise_removal_model.remove_noise(image)
    elif area == 'background':
        return noise_removal_model.remove_background_noise(image)
    elif area == 'custom' and selection_rect:
        x, y, width, height = selection_rect.values()
        roi = image[y:y+height, x:x+width]
        processed_roi = noise_removal_model.remove_noise(roi)
        result = image.copy()
        result[y:y+height, x:x+width] = processed_roi
        return result
    return noise_removal_model.remove_noise(image)

def apply_image_filter(image_path, filter_name):
    image = cv2.imread(image_path)
    if filter_name == 'aftereffects':
        blue_channel = image[:, :, 2]
        image[:, :, 2] = np.clip(blue_channel * 1.2, 0, 255)
    elif filter_name == 'afterglow':
        red_channel = image[:, :, 0]
        green_channel = image[:, :, 1]
        image[:, :, 0] = np.clip(red_channel * 1.2, 0, 255)
        image[:, :, 1] = np.clip(green_channel * 1.1, 0, 255)
    elif filter_name == 'cinematic':
        image = cv2.convertScaleAbs(image, alpha=1.3, beta=10)
    return image

if __name__ == '__main__':
    app.run(debug=True)
