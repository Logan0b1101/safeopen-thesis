import sqlite3
import time
from pathlib import Path

DB_PATH = Path("safeopen_audit.db")

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS events (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ts INTEGER,
        file_path TEXT,
        static_label TEXT,
        ml_prob REAL,
        final_score REAL,
        final_label TEXT,
        action TEXT,
        action_result TEXT,
        latency REAL
    )
    """)

    conn.commit()
    conn.close()


def log_event(
    file_path,
    static_label,
    ml_prob,
    final_score,
    final_label,
    action,
    action_result,
    latency
):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("""
    INSERT INTO events (
        ts, file_path, static_label, ml_prob,
        final_score, final_label, action,
        action_result, latency
    )
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        int(time.time()),
        file_path,
        static_label,
        float(ml_prob),
        float(final_score),
        final_label,
        action,
        action_result,
        float(latency)
    ))

    conn.commit()
    conn.close()
