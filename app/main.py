from flask import Flask, request, render_template, redirect, url_for, send_file
from ultralytics import YOLO
import cv2
import os
from database import init_db, save_analysis_record
from report import generate_report
import sqlite3
import numpy as np

app = Flask(__name__)

model = YOLO('yolov8n.pt')

UPLOAD_FOLDER = 'app/uploads'
STATIC_FOLDER = 'app/static'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(STATIC_FOLDER, exist_ok=True)

init_db()

@app.route('/', methods=['GET', 'POST'])
def upload_image():
    if request.method == 'POST':
        if 'image' not in request.files:
            return "No file uploaded", 400
        file = request.files['image']
        if file.filename == '':
            return "No selected file", 400

        filename = file.filename
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        file.save(filepath)

        results = model(filepath)
        if isinstance(results, list):
            results = results[0]

        image_path = cv2.imread(filepath)

        boxes = results.boxes.xyxy.cpu().numpy()
        scores = results.boxes.conf.cpu().numpy()
        classes = results.boxes.cls.cpu().numpy()

        person_indices = [i for i, c in enumerate(classes) if c == 0]

        rects = []
        filtered_scores = []

        for i in person_indices:
            x1, y1, x2, y2 = boxes[i]
            rects.append([x1, y1, x2 - x1, y2 - y1])
            filtered_scores.append(scores[i])

        iou_threshold = 0.5
        score_threshold = 0.25

        if len(rects) > 0:
            indices_nms = cv2.dnn.NMSBoxes(rects, filtered_scores, score_threshold, iou_threshold)

            if len(indices_nms) > 0:
                for idx, i in enumerate(indices_nms.flatten()):
                    x, y, w, h = map(int, rects[i])
                    cv2.rectangle(image_path, (x, y), (x + w, y + h), (0, 255, 0), 3)
                    label = f"Person {idx + 1}"
                    text_x = x
                    text_y = y - 10 if y - 10 > 10 else y + 20
                    cv2.putText(image_path, label, (text_x, text_y), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2, cv2.LINE_AA)
            person_count = len(indices_nms)
        else:
            person_count = 0

        output_filename = f"result_{filename}"
        output_path = os.path.join(STATIC_FOLDER, output_filename)
        cv2.imwrite(output_path, image_path)

        save_analysis_record(output_filename, person_count)

        return render_template('result.html', count=person_count, image_url=f'/static/{output_filename}')

    return render_template('upload.html')

@app.route('/generate_report')
def report():
    reports_dir = os.path.join(os.path.dirname(__file__), 'reports')
    report_path = os.path.join(reports_dir, 'report.pdf')
    generate_report(report_path)

    if os.path.exists(report_path):
        return send_file(report_path, as_attachment=True)
    else:
        return "Report not found. Please try generating the report again.", 404

if __name__ == '__main__':
    app.run(debug=True)

