from flask import Flask, request, jsonify, render_template
import cv2
import numpy as np
import time
import base64
import os

from ultralytics import YOLO
from google_drive_upload import upload_to_drive

app = Flask(__name__)

# Load YOLOv5 model from local weights
model = YOLO('yolov5s.pt')

# ---------- Image Enhancement Function ----------
def enhance_dark_image(img):
    """Enhance dark image using CLAHE (Contrast Limited Adaptive Histogram Equalization)."""
    lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)
    l, a, b = cv2.split(lab)

    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
    cl = clahe.apply(l)

    limg = cv2.merge((cl, a, b))
    enhanced = cv2.cvtColor(limg, cv2.COLOR_LAB2BGR)
    return enhanced

# ---------- Routes ----------
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
    data = request.get_json()

    drive_folder_id = data.get('drive')
    image_data = data.get('image')

    try:
        # Decode base64 image
        image_data = image_data.split(",")[1]
        img_bytes = base64.b64decode(image_data)
        nparr = np.frombuffer(img_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        # Enhance image for low-light detection
        enhanced_img = enhance_dark_image(img)

        # Run YOLOv5 detection
        results = model(enhanced_img)
        labels = results[0].names

        if 'person' in labels:
            timestamp = time.strftime("%Y%m%d-%H%M%S")
            image_path = f"media/detected_{timestamp}.jpg"
            cv2.imwrite(image_path, enhanced_img)

            print(f"[INFO] Person detected. Image saved: {image_path}")

            try:
                # Upload to Google Drive
                upload_to_drive(image_path, drive_folder_id)

                print(f"[INFO] Image uploaded to Google Drive: {image_path}")

                message = (
                    "🚨 Person detected!\n"
                    "📁 Picture uploaded to Drive."
                )

                return jsonify({
                    'person_detected': True,
                    'message': message
                })

            except Exception as upload_err:
                print(f"[UPLOAD ERROR]: {upload_err}")
                return jsonify({
                    'person_detected': True,
                    'error': str(upload_err)
                })

        else:
            print("[INFO] No person detected.")
            return jsonify({'person_detected': False})

    except Exception as e:
        print(f"[ERROR]: {e}")
        return jsonify({'error': str(e)}), 500

# ---------- Entry point for Render ----------
if __name__ == '__main__':
    if not os.path.exists('media'):
        os.makedirs('media')
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
