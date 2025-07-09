from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import sqlite3
import os

def generate_report(pdf_path='report.pdf'):
    conn = sqlite3.connect('history.db')
    cursor = conn.cursor()
    cursor.execute('SELECT image_path, datetime, person_count FROM history')
    records = cursor.fetchall()
    conn.close()

    reports_dir = os.path.join(os.path.dirname(__file__), 'reports')
    os.makedirs(reports_dir, exist_ok=True)

    if pdf_path is None:
        pdf_path = os.path.join(reports_dir, 'report.pdf')
    else:
        pdf_path = os.path.abspath(pdf_path)

    c = canvas.Canvas(pdf_path, pagesize=letter)
    width, height = letter
    y_position = height - 50
    y_position -= 30

    c.setFont("Helvetica", 12)

    for record in records:
        image_path, dt, count = record
        if isinstance(image_path, bytes):
            try:
                image_path = image_path.decode('utf-8')
            except UnicodeDecodeError:
                image_path = image_path.decode('latin-1', errors='ignore')
        if not os.path.isabs(image_path):
            image_path = os.path.join(os.path.dirname(__file__), 'static', image_path)
        if os.path.exists(image_path):
            c.drawImage(image_path, 50, y_position - 100, width=200, height=150)
        c.drawString(275, y_position - 20, f"DateTime: {dt}")
        c.drawString(275, y_position - 40, f"Persons detected: {count}")
        y_position -= 180
        if y_position < 100:
            c.showPage()
            y_position = height - 50

    c.save()
