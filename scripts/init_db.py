import sqlite3

conn = sqlite3.connect("safeopen_audit.db")
cur = conn.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ts INTEGER,
    file_path TEXT,
    static_label TEXT,
    ml_score REAL,
    risk TEXT,
    action TEXT,
    action_result TEXT,
    latency REAL
)
""")

conn.commit()
conn.close()

print("[DB] events table initialized")
