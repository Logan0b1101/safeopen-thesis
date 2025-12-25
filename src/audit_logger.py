import sqlite3
import time

DB_PATH = "safeopen_audit.db"

def log_event(
    file_path,
    static_label,
    static_reason,
    ml_prob,
    final_score,
    final_label,
    action,
    action_result
):
    ts = int(time.time())

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO events
        (ts, file_path, static_label, static_reason,
         ml_prob, final_score, final_label, action, action_result)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        ts,
        file_path,
        static_label,
        static_reason,
        ml_prob,
        final_score,
        final_label,
        action,
        action_result
    ))

    conn.commit()
    conn.close()
