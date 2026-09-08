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


### Day 2 — somewhere to put the data

Added SQLite today so I have somewhere to actually save the status
checks. First time really using it — turns out it's just a file, no
separate server to install, which wasn't what I expected.

Wrote one function, `init_db()`, that creates a table called
`disruptions` if it doesn't already exist. Used `IF NOT EXISTS`
since I call this every time the app starts, and forgot `.commit()`
the first time and couldn't figure out why nothing was saving.

```python
import sqlite3

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
```
### Day 3 — adding real data

Added the actual TFL API call today. This is the first time the app
does something with real, live data instead of placeholder text.

Hit a snag straight away, got a `429 Too Many Requests` error the
first time I ran it, because I was using the placeholder API key.
Turned out TFL's status endpoint works without a real key for light
use, but the rate limit on that is very easy to hit while testing
repeatedly. Registered for a free TFL API key and set it as an
environment variable instead of putting it in the code, so it never
ends up in git history.

```python

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
```

Tested it by temporarily printing the result before committing, and
saw real live line statuses (Bakerloo on Severe Delays, Central on
Minor Delays, etc.) —first time this project actually reflects
something real happening in London right now, which felt like a good
milestone.


### Day 4 — adding real data

Connected everything together. Added `save_to_history()`, which
writes each line's status into the database, plus `/api/live` and
`/api/history` — one fetches fresh data and saves it, the other just
reads back what's already stored.

Made sure to use `?` placeholders in the SQL insert instead of
putting values straight into the string, learned that's what stops
SQL injection, so wanted to actually get that instead of just copying
it.

Also added `/api/summary`, which counts how many times each line's
had a bad status. Did the counting with a plain dictionary instead of
SQL's `GROUP BY`, since I don't know that yet, might redo it properly
later 

Tested by hitting `/api/live` a few times, then checking `/api/history`
and `/api/summary` actually reflected it. Core app's working now 
still want to add a real frontend at some point.

### Day 5 — a real frontend

Added `static/index.html` and updated the homepage route to serve it
with `send_from_directory` instead of returning plain text. Styled it
as a departure board, using the real TfL line colours as status
indicators next to each line — felt more fitting for a Tube tracker
than a generic dashboard look.

```python

from flask import Flask, jsonify, send_from_directory

app = Flask(__name__, static_folder="static")

@app.route("/")
def home():
    return send_from_directory("static", "index.html")
```

Ran into a couple of local setup issues along the way that had
nothing to do with the code itself — a stuck old Flask process
holding onto port 5000, and having to reset my API key each new
terminal session. Fixed both: added `TFL_APP_KEY` permanently to my
shell config instead of exporting it every time.

