# ...existing code...
import os
import sqlite3
from datetime import datetime

BASE_DIR = os.path.dirname(__file__)
DB_PATH = os.path.join(BASE_DIR, "sensors.db")

def _get_conn():
    conn = sqlite3.connect(DB_PATH, detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = _get_conn()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS raindrops (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            value REAL NOT NULL,
            ts DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()

def insert_raindrop(value, ts=None):
    """Insert a raindrop reading. ts can be a datetime or None."""
    if ts is None:
        ts = datetime.utcnow()
    conn = _get_conn()
    cur = conn.cursor()
    cur.execute("INSERT INTO raindrops (value, ts) VALUES (?, ?)", (float(value), ts))
    conn.commit()
    last_id = cur.lastrowid
    conn.close()
    return last_id

def get_last_raindrops(limit=10):
    """Return the last `limit` readings ordered oldest->newest as list of dicts."""
    conn = _get_conn()
    cur = conn.cursor()
    cur.execute("SELECT id, value, ts FROM raindrops ORDER BY ts DESC LIMIT ?", (int(limit),))
    rows = cur.fetchall()
    conn.close()
    # rows are newest first; reverse to oldest->newest
    rows = list(reversed(rows))

    out = []
    for r in rows:
        ts = r["ts"]
        # Normalize timestamp to ISO8601 (UTC). DB may return datetime or string 'YYYY-MM-DD HH:MM:SS'
        if isinstance(ts, datetime):
            ts_iso = ts.isoformat() + "Z"
        else:
            s = str(ts) if ts is not None else ""
            # convert "YYYY-MM-DD HH:MM:SS" -> "YYYY-MM-DDTHH:MM:SSZ"
            if s and "T" not in s:
                ts_iso = s.replace(" ", "T") + "Z"
            else:
                ts_iso = s
        out.append({"id": r["id"], "value": r["value"], "ts": ts_iso})
    return out

# Initialize DB on import
init_db()
# ...existing code...