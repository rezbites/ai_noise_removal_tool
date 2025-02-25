from flask import Flask, request, jsonify, send_from_directory, render_template
from flask_cors import CORS
import os
import uuid
import cv2
import numpy as np
import json
from model import NoiseRemovalModel

app = Flask(__name__, template_folder='../templates')  # Point to the templates folder
CORS(app)  # Enable CORS for cross-origin requests

# Configure upload and results directories
UPLOAD_FOLDER = 'static/uploads'
PROCESSED_FOLDER = 'static/processed'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

# Create directories if they don't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(PROCESSED_FOLDER, exist_ok=True)

# Initialize the AI model
noise_removal_model = NoiseRemovalModel()

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def home():
    return render_template('index.html')  # Serve the frontend

@app.route('/process_image', methods=['POST'])
def process_image():
    if 'image' not in request.files:
        return jsonify({'error': 'No image provided'}), 400
        
    file = request.files['image']
    if file.filename == '':
        return jsonify({'error': 'No image selected'}), 400
        
    if file and allowed_file(file.filename):
        # Generate unique filename
        filename = str(uuid.uuid4()) + os.path.splitext(file.filename)[1]
        file_path = os.path.join(UPLOAD_FOLDER, filename)
        file.save(file_path)
        
        # Get processing area
        area = request.form.get('area', 'full')
        selection_rect = None
        
        if area == 'custom' and 'selectionRect' in request.form:
            selection_rect = json.loads(request.form['selectionRect'])
        
        # Process the image using our AI model
        processed_image = process_with_ai(file_path, area, selection_rect)
        
        # Save processed image
        processed_filename = 'processed_' + filename
        processed_path = os.path.join(PROCESSED_FOLDER, processed_filename)
        cv2.imwrite(processed_path, processed_image)
        
        # Return the URL to access the processed image
        return jsonify({
            'processed_image_url': f'/static/processed/{processed_filename}'
        })
    
    return jsonify({'error': 'Invalid file format'}), 400

@app.route('/apply_filter', methods=['GET'])
def apply_filter():
    image_url = request.args.get('image_url')
    filter_name = request.args.get('filter')
    
    if not image_url or not filter_name:
        return jsonify({'error': 'Image URL and filter name are required'}), 400
    
    # Extract the filename from the URL
    filename = os.path.basename(image_url)
    image_path = os.path.join(PROCESSED_FOLDER, filename)
    
    if not os.path.exists(image_path):
        return jsonify({'error': 'Image not found'}), 404
    
    # Apply the selected filter
    filtered_image = apply_image_filter(image_path, filter_name)
    
    # Save filtered image
    filtered_filename = f"{filter_name}_{filename}"
    filtered_path = os.path.join(PROCESSED_FOLDER, filtered_filename)
    cv2.imwrite(filtered_path, filtered_image)
    
    # Return the URL to access the filtered image
    return jsonify({
        'filtered_image_url': f'/static/processed/{filtered_filename}'
    })

def process_with_ai(image_path, area='full', selection_rect=None):
    # Load the image
    image = cv2.imread(image_path)
    
    if area == 'full':
        # Process the entire image
        return noise_removal_model.remove_noise(image)
    
    elif area == 'background':
        # Use segmentation to identify foreground/background
        return noise_removal_model.remove_background_noise(image)
    
    elif area == 'custom' and selection_rect:
        # Process only the selected area
        x, y, width, height = selection_rect['x'], selection_rect['y'], selection_rect['width'], selection_rect['height']
        
        # Ensure coordinates are positive
        if width < 0:
            x += width
            width = abs(width)
        if height < 0:
            y += height
            height = abs(height)
            
        # Extract region of interest
        roi = image[y:y+height, x:x+width]
        
        # Process only the ROI
        processed_roi = noise_removal_model.remove_noise(roi)
        
        # Copy processed ROI back to the original image
        result = image.copy()
        result[y:y+height, x:x+width] = processed_roi
        
        return result
    
    # Default: process the entire image
    return noise_removal_model.remove_noise(image)

def apply_image_filter(image_path, filter_name):
    image = cv2.imread(image_path)
    
    if filter_name == 'aftereffects':
        # Apply After Effects filter (blue tint)
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        blue_channel = image[:, :, 2]
        image[:, :, 2] = np.clip(blue_channel * 1.2, 0, 255)
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
        
    elif filter_name == 'afterglow':
        # Apply Afterglow filter (warm tones)
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        red_channel = image[:, :, 0]
        green_channel = image[:, :, 1]
        image[:, :, 0] = np.clip(red_channel * 1.2, 0, 255)
        image[:, :, 1] = np.clip(green_channel * 1.1, 0, 255)
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
        
    elif filter_name == 'cinematic':
        # Apply Cinematic filter (contrast boost with letterbox)
        # Increase contrast
        alpha = 1.3  # Contrast control
        beta = 10    # Brightness control
        image = cv2.convertScaleAbs(image, alpha=alpha, beta=beta)
        
        # Add letterbox
        h, w = image.shape[:2]
        letterbox_height = int(h * 0.1)
        image[:letterbox_height, :] = 0
        image[-letterbox_height:, :] = 0
    
    return image

@app.route('/static/<path:path>')
def serve_static(path):
    return send_from_directory('static', path)

if __name__ == '__main__':
    app.run(debug=True)
