import sqlite3
from pathlib import Path

DB_PATH = Path.home() / "thesis/safeopen/safeopen_audit.db"

def get_recent_events(limit=10):
    try:
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()

        cur.execute("""
            SELECT ts, file_path, final_label, action
            FROM events
            ORDER BY ts DESC
            LIMIT ?
        """, (limit,))

        rows = cur.fetchall()
        conn.close()
        return rows
    except Exception:
        return []
