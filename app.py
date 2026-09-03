# app.py
from flask import Flask
import sqlite3

app = Flask(__name__)

DB_FILE = "tfl_history.db"

def init_db():
    connection = sqlite3.connect(DB_FILE)
    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS disruptions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            line_name TEXT,
            status TEXT,
            checked_at TEXT
        )
    """)

    connection.commit()
    connection.close()

@app.route("/")
def home():
    return "London Transport Delay Tracker is running!"

if __name__ == "__main__":
    init_db()
    app.run(debug=True)