import os
import base64
import time
import cv2
import numpy as np
from flask import Flask, request, jsonify, render_template

from ultralytics import YOLO
from google_drive_upload import upload_to_drive

app = Flask(__name__)

# Load YOLOv5 model
MODEL_PATH = 'yolov5s.pt'
model = YOLO(MODEL_PATH)

# Enhance low-light images
def enhance_dark_image(img):
    lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)
    l, a, b = cv2.split(lab)
    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
    cl = clahe.apply(l)
    limg = cv2.merge((cl, a, b))
    return cv2.cvtColor(limg, cv2.COLOR_LAB2BGR)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/home')
def home():
    return render_template('home.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/logo.png')
def logo():
    return app.send_static_file('logo.png')

@app.route('/detect', methods=['POST'])
def detect():
    try:
        data = request.get_json()
        whatsapp_number = data.get('whatsapp')
        drive_folder_id = data.get('drive')
        image_data = data.get('image')

        if not image_data:
            return jsonify({'error': 'No image data provided'}), 400

        # Decode base64 image
        image_data = image_data.split(",")[1]
        img_bytes = base64.b64decode(image_data)
        nparr = np.frombuffer(img_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        # Enhance and detect
        enhanced_img = enhance_dark_image(img)
        results = model.predict(source=enhanced_img, save=False, verbose=False)
        detections = results[0].boxes.cls.cpu().numpy()
        labels = results[0].names
        detected_classes = [labels[int(cls)] for cls in detections]

        if 'person' in detected_classes:
            if not os.path.exists('media'):
                os.makedirs('media')

            timestamp = time.strftime("%Y%m%d-%H%M%S")
            image_path = f"media/detected_{timestamp}.jpg"
            cv2.imwrite(image_path, enhanced_img)

            upload_to_drive(image_path, drive_folder_id)

            return jsonify({
                'person_detected': True,
                'message': "🚨 Person detected! 📁 Picture uploaded to Drive."
            })
        else:
            return jsonify({'person_detected': False})

    except Exception as e:
        print(f"[ERROR]: {e}")
        return jsonify({'error': str(e)}), 500

# Optional: keep app.run for local testing only
if __name__ == '__main__':
    if not os.path.exists('media'):
        os.makedirs('media')
    app.run(host='0.0.0.0', port=5000)
