
# AI Noise Removal Tool

## Overview
The **AI Noise Removal Tool** is a web-based application that allows users to upload images, remove noise using AI-based processing, and enhance image quality. The tool is built using **Flask** for the backend, **OpenCV** for image processing, and a frontend built with **HTML, CSS, and JavaScript**.

## Features
- **Upload & Process Images**: Users can upload images through drag-and-drop or file selection.
- **AI-Based Noise Removal**: Uses OpenCV to enhance image quality.
- **Simple Web Interface**: Built with Flask, JavaScript, and CSS.
- **Image Management**: Uploaded images are stored in a directory and processed images are saved separately.

## Tech Stack
- **Frontend**: HTML, CSS, JavaScript
- **Backend**: Flask, Python
- **Image Processing**: OpenCV
- **Storage**: Local file system

## Folder Structure
```
noise-removal/
│── backend/
│   │── static/
│   │   │── frontend/
│   │   │   │── app.js
│   │   │   │── styles.css
│   │   │── processed/  # Stores processed images
│   │   │── uploads/    # Stores uploaded images
│   │── templates/
│   │   │── index.html  # Main web page
│   │   │── api.html
│   │── app.py         # Flask application
│   │── model.py       # Image processing logic
│   │── requirements.txt
│── .venv/            # Virtual environment (optional)
```

## Setup Instructions
### 1. Clone the Repository
```sh
git clone https://github.com/your-username/noise-removal.git
cd noise-removal/backend
```

### 2. Create & Activate Virtual Environment (Optional but Recommended)
```sh
python -m venv venv
# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On Mac/Linux:
source venv/bin/activate
```

### 3. Install Dependencies
```sh
pip install -r requirements.txt
```

### 4. Run the Flask Server
```sh
python app.py
```
Flask will start running at **http://127.0.0.1:5000/**

## Usage
1. Open the app in your browser: [http://127.0.0.1:5000/](http://127.0.0.1:5000/)
2. Drag and drop an image or select a file to upload.
3. Click the "Process" button to remove noise from the image.
4. Download the enhanced image.

## Troubleshooting
- **Frontend is not responsive?**
  - Check if `app.js` is linked correctly in `index.html`.
  - Open the browser console (`F12 > Console`) to check for errors.

- **Server not running?**
  - Ensure Flask is installed (`pip install flask`).
  - Restart the server with `python app.py`.

## Future Improvements
- Add **GPU acceleration** for faster processing.
- Implement **real-time noise reduction** using deep learning.
- Deploy the app on **AWS/GCP**.

## License
This project is open-source and available under the **MIT License**.

---
**Author:** Shashank Choudhary  


