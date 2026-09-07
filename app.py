# app.py

from flask import Flask, jsonify
import sqlite3
import requests
import os
from datetime import datetime

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


def save_to_history(results):
    connection = sqlite3.connect(DB_FILE)
    cursor = connection.cursor()

    now = datetime.now().isoformat()

    for item in results:
        cursor.execute(
            "INSERT INTO disruptions (line_name, status, checked_at) VALUES (?, ?, ?)",
            (item["line"], item["status"], now)
        )

    connection.commit()
    connection.close()


@app.route("/")
def home():
    return "London Transport Delay Tracker is running!"


@app.route("/api/live")
def live_status():
    results = fetch_live_status()
    save_to_history(results)
    return jsonify(results)


@app.route("/api/history")
def history():
    connection = sqlite3.connect(DB_FILE)
    cursor = connection.cursor()

    cursor.execute("SELECT line_name, status, checked_at FROM disruptions")
    rows = cursor.fetchall()

    connection.close()

    history_list = []
    for row in rows:
        one_row = {"line_name": row[0], "status": row[1], "checked_at": row[2]}
        history_list.append(one_row)

    return jsonify(history_list)


@app.route("/api/summary")
def summary():
    connection = sqlite3.connect(DB_FILE)
    cursor = connection.cursor()

    cursor.execute("SELECT line_name, status FROM disruptions")
    rows = cursor.fetchall()

    connection.close()

    counts = {}

    for row in rows:
        line_name = row[0]
        status = row[1]

        if status != "Good Service":
            if line_name in counts:
                counts[line_name] = counts[line_name] + 1
            else:
                counts[line_name] = 1

    summary_list = []
    for line_name in counts:
        one_summary = {"line": line_name, "disruption_count": counts[line_name]}
        summary_list.append(one_summary)

    return jsonify(summary_list)


if __name__ == "__main__":
    init_db()
    app.run(debug=True)