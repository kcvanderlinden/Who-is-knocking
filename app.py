#!/usr/bin/env python3
"""
Flask app that displays a ranking of source countries
from the `kernel_logs` SQLite table.

Usage
-----
    export FLASK_APP=app.py
    flask run   # or: python app.py
"""

import sqlite3
from collections import Counter
from flask import Flask, render_template, g

# ----------------------------------------------------------------------
# Configuration
# ----------------------------------------------------------------------
DB_PATH = '/var/log/kernel_logs.db'   # ← adjust if your db lives elsewhere
TABLE   = 'kernel_logs'

app = Flask(__name__)

# ----------------------------------------------------------------------
# Database helpers
# ----------------------------------------------------------------------
def get_db():
    """
    Lazily open a database connection for the current request.
    The connection is stored in Flask's `g` object so it can be
    reused and closed automatically at the end of the request.
    """
    if 'db' not in g:
        g.db = sqlite3.connect(DB_PATH)
        g.db.row_factory = sqlite3.Row  # Access columns by name
    return g.db

@app.teardown_appcontext
def close_db(error=None):
    """Close the database at the end of the request."""
    db = g.pop('db', None)
    if db is not None:
        db.close()

# ----------------------------------------------------------------------
# Core logic – build the ranking
# ----------------------------------------------------------------------
def get_country_ranking():
    """
    Query the DB, count occurrences of `country_src`,
    and return a list of (country, count) tuples sorted descending.
    """
    db = get_db()
    cur = db.execute(
        f'''
        SELECT country_src, COUNT(*) AS cnt
        FROM {TABLE}
        WHERE country_src IS NOT NULL
        GROUP BY country_src
        ORDER BY cnt DESC
        '''
    )
    rows = cur.fetchall()
    return [(row['country_src'], row['cnt']) for row in rows]

# ----------------------------------------------------------------------
# Flask route
# ----------------------------------------------------------------------
@app.route('/')
def index():
    ranking = get_country_ranking()
    return render_template('index.html', ranking=ranking)

# ----------------------------------------------------------------------
# Run the app if this file is executed directly
# ----------------------------------------------------------------------
if __name__ == '__main__':
    # For quick testing you can use `debug=True`
    app.run(host='0.0.0.0', port=5000, debug=True)