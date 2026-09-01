# app.py

from flask import Flask

app = Flask(__name__)


@app.route("/")
def home():
    return "London Transport Delay Tracker is running!"


if __name__ == "__main__":
    app.run(debug=True)
