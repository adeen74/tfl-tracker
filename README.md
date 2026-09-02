# London Transport Delay Tracker

A Flask app that checks live status for London Tube lines using TFL's
public API, and saves each check to a database so I can build up a
history of delays over time. 

I'm building this one small piece at a time and updating this README
as I go, instead of writing it all at once at the end. Partly so I
actually remember why I made each decision, and partly because I want
this file to genuinely show how the project came together.

---

## Log

### Day 1 — it runs

Got the absolute simplest version of this working today: a Flask app
with one route that just says the tracker is running. 


```python
from flask import Flask

app = Flask(__name__)

@app.route("/")
def home():
    return "London Transport Delay Tracker is running!"

if __name__ == "__main__":
    app.run(debug=True)
```

**Run it:**
```bash
pip install flask
python app.py
```
Then open `http://127.0.0.1:5000`.

