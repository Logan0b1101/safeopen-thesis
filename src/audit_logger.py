import sqlite3
import time
import os

DB_PATH = os.path.join(os.getcwd(), "safeopen_audit.db")

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS events (
            ts INTEGER,
            file_path TEXT,
            static_label TEXT,
            static_reason TEXT,
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
    static_reason,
    ml_prob,
    final_score,
    final_label,
    action,
    action_result,
    latency
):
    init_db()
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO events VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        int(time.time()),
        file_path,
        static_label,
        static_reason,
        float(ml_prob),
        float(final_score),
        final_label,
        action,
        action_result,
        float(latency)
    ))
    conn.commit()
    conn.close()
