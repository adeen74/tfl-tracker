# app.py
from flask import Flask
import sqlite3
import requests
import os

app = Flask(__name__)

DB_FILE = "tfl_history.db"
TFL_APP_KEY = os.environ.get("TFL_APP_KEY", "PASTE_YOUR_API_KEY_HERE")

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

def fetch_live_status():
    url = "https://api.tfl.gov.uk/Line/Mode/tube/Status"
    params = {"app_key": TFL_APP_KEY}

    response = requests.get(url, params=params, timeout=10)
    response.raise_for_status()
    data = response.json()

    results = []

    for line in data:
        line_name = line["name"]
        statuses = line["lineStatuses"]
        status = statuses[0]["statusSeverityDescription"]

        one_result = {"line": line_name, "status": status}
        results.append(one_result)

    return results

@app.route("/")
def home():
    return "London Transport Delay Tracker is running!"

if __name__ == "__main__":
    init_db()
    # print(fetch_live_status())   # temporary
    app.run(debug=True)