import datetime
import sqlite3
import os

DB_PATH = 'history.db'

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            image_path TEXT,
            datetime TEXT,
            person_count INTEGER
        )
    ''')
    conn.commit()
    conn.close()

def save_analysis_record(image_path, person_count):
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO history (image_path, datetime, person_count)
        VALUES (?, ?, ?)
    ''', (image_path, now, person_count))
    conn.commit()
    conn.close()