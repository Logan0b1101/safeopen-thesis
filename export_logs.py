#!/usr/bin/env python3
"""
Export SafeOpen SQLite logs to CSV for analysis.
"""
import sqlite3
import csv
from pathlib import Path

DB = Path.home() / "thesis" / "~safeopen" / "safeopen_audit.db"
OUT = Path.cwd() / "ml_results_advanced" / "audit_export.csv"
OUT.parent.mkdir(parents=True, exist_ok=True)

def export():
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    rows = c.execute("SELECT * FROM events ORDER BY ts DESC").fetchall()
    cols = [d[0] for d in c.description]
    conn.close()
    with open(OUT, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(cols)
        for r in rows:
            writer.writerow(r)
    print("Exported", len(rows), "rows to", OUT)

if __name__ == "__main__":
    export()
