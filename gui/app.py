import os
import sqlite3
import subprocess
from functools import wraps
from flask import (
    Flask, render_template, request,
    redirect, url_for, session, flash
)

# ==============================
# CONFIG
# ==============================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.abspath(os.path.join(BASE_DIR, "..", "safeopen_audit.db"))

APP_SECRET = "safeopen_thesis_secret"  # change later if needed

VALID_USERS = {
    "admin": "admin123",   # demo credentials (thesis-safe)
}

# ==============================
# FLASK APP
# ==============================
app = Flask(__name__)
app.secret_key = APP_SECRET


# ==============================
# AUTH DECORATOR
# ==============================
def login_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if "user" not in session:
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return wrapper


# ==============================
# DATABASE HELPERS
# ==============================
def get_recent_events(limit=20):
    if not os.path.exists(DB_PATH):
        return []

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    cur.execute("""
        SELECT
            ts,
            file_path,
            static_label,
            ml_prob,
            final_label,
            action
        FROM events
        ORDER BY ts DESC
        LIMIT ?
    """, (limit,))

    rows = cur.fetchall()
    conn.close()
    return rows


def get_event_counts():
    if not os.path.exists(DB_PATH):
        return {"LOW": 0, "MEDIUM": 0, "HIGH": 0}

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("""
        SELECT final_label, COUNT(*)
        FROM events
        GROUP BY final_label
    """)

    counts = {"LOW": 0, "MEDIUM": 0, "HIGH": 0}
    for label, count in cur.fetchall():
        if label in counts:
            counts[label] = count

    conn.close()
    return counts


# ==============================
# DAEMON STATUS
# ==============================
def daemon_status():
    try:
        result = subprocess.run(
            ["systemctl", "is-active", "safeopen.service"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        return result.stdout.strip()
    except Exception:
        return "unknown"


# ==============================
# ROUTES
# ==============================
@app.route("/")
def index():
    if "user" in session:
        return redirect(url_for("dashboard"))
    return redirect(url_for("login"))


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        if username in VALID_USERS and VALID_USERS[username] == password:
            session["user"] = username
            return redirect(url_for("dashboard"))
        else:
            flash("Invalid credentials", "error")

    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

@app.route("/dashboard")
@login_required
def dashboard():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    cur.execute("""
        SELECT ts, file_path, final_label, action
        FROM events
        ORDER BY ts DESC
        LIMIT 20
    """)
    events = cur.fetchall()
    conn.close()

    daemon_status = "RUNNING" if os.system("pgrep -f daemon.py > /dev/null") == 0 else "STOPPED"

    return render_template(
        "dashboard.html",
        events=events,
        daemon_status=daemon_status
    )


# ==============================
# MAIN
# ==============================
if __name__ == "__main__":
    app.run(
        host="127.0.0.1",
        port=5000,
        debug=True
    )
