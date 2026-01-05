#!/usr/bin/env python3
"""
SafeOpen Background Daemon (FINAL STABLE VERSION)

- Real-time filesystem monitoring
- Deterministic risk escalation
- Robust logging (no missing variables)
- Thesis-safe and demo-safe
"""

import os
import time
import traceback
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

from src.risk_scorer.scorer import check_file_risk
from src.feature_extractor import extract_features_for_ml
from src.ml_integration import MLScorer
from src.cdr.cdr_engine import sanitize_file
from src.sandbox_manager.sandbox import open_in_sandbox
from src.audit_logger import log_event
from src.utils.audit import init_db
from src.utils.pdf_inspector import extract_pdf_indicators
from src.utils.pdf_indicators import extract_pdf_indicators

# ---------------- CONFIG ----------------

WATCH_DIRS = [
    str(Path.home() / "Downloads")
]

MIN_FILE_SIZE_BYTES = 32
DEBOUNCE_SEC = 1.0

# ---------------- ML INIT ----------------

try:
    ml = MLScorer()
    print("[daemon] MLScorer loaded")
except Exception as e:
    ml = None
    print("[daemon] MLScorer unavailable:", e)

# ---------------- HANDLER ----------------

class ScanHandler(FileSystemEventHandler):
    def __init__(self):
        super().__init__()
        self.seen = set()

    def on_created(self, event):
        self._handle_event(event)

    def on_modified(self, event):
        self._handle_event(event)

    def _handle_event(self, event):
        if event.is_directory:
            return

        path = event.src_path

        # Ignore temp / lock files
        if os.path.basename(path).startswith("."):
            return

        # Deduplicate events
        if path in self.seen:
            return

        time.sleep(DEBOUNCE_SEC)

        if not os.path.exists(path):
            return

        if os.path.getsize(path) < MIN_FILE_SIZE_BYTES:
            return

        self.seen.add(path)
        print("[daemon] Scanning:", path)
        self.scan_file(path)

    def scan_file(self, path):
        start_time = time.time()

        try:
            # ---------------- Static Analysis ----------------
            static_label, static_reason = check_file_risk(path)

            # ---------------- ML Analysis ----------------
            ml_prob = 0.0
            if ml:
                features = extract_features_for_ml(path)
                ml_prob, _ = ml.predict(features)

            # ---------------- Indicator Escalation ----------------
            indicators = []

            if path.lower().endswith(".pdf"):
                indicators = extract_pdf_indicators(path)
            
            # HARD ESCALATION RULE (STRUCTURAL EXECUTION)
            escalated = False

            if indicators:
                if "Auto-execution OpenAction" in indicators:
                    escalated = True
                if "Embedded JavaScript" in indicators:
                    escalated = True

            static_reason += " | Indicators: " + ", ".join(indicators)

            # ---------------- Score Fusion ----------------
            static_map = {"LOW": 0.2, "MEDIUM": 0.5, "HIGH": 0.9}
            static_score = static_map.get(static_label, 0.5)

            final_score = (0.5 * static_score) + (0.4 * ml_prob)
            final_score = min(final_score, 1.0)

            # ---------------- Decision Logic ----------------
            if escalated:
                final_label = "HIGH"
                action = "SANDBOX"
                static_reason += " | Indicators: " + ", ".join(indicators)
            else:
                if escalated:
                    final_label = "HIGH"
                    action = "SANDBOX"
                elif final_score >= 0.65:
                    final_label = "HIGH"
                    action = "SANDBOX"
                elif final_score >= 0.40:
                    final_label = "MEDIUM"
                    action = "CDR"
                else:
                    final_label = "LOW"
                    action = "NONE"
            # ---------------- Response ----------------
            action_result = ""

            if action == "SANDBOX":
                ok, msg = open_in_sandbox(path)
                action_result = msg

            elif action == "CDR":
                ok, result = sanitize_file(path)
                action_result = f"Sanitized → {result}" if ok else f"CDR failed: {result}"

            latency = round(time.time() - start_time, 4)

            # ---------------- Audit Log ----------------
            log_event(
                file_path=path,
                static_label=static_label,
                static_reason=static_reason,
                ml_prob=float(ml_prob),
                final_score=float(final_score),
                final_label=final_label,
                action=action,
                action_result=action_result,
                latency=float(latency)
            )

            print(f"[daemon] {path} → {final_label} ({action})")

        except Exception:
            print("[daemon] ERROR scanning:", path)
            traceback.print_exc()

# ---------------- WATCHER ----------------

def start_watcher():
    observer = Observer()
    handler = ScanHandler()

    print("[daemon] HOME =", Path.home())
    print("[daemon] WATCH_DIRS =", WATCH_DIRS)

    for d in WATCH_DIRS:
        if os.path.exists(d):
            observer.schedule(handler, d, recursive=True)
            print("[daemon] Watching:", d)
        else:
            print("[daemon] WARNING: Missing directory:", d)

    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()

    observer.join()

# ---------------- MAIN ----------------

if __name__ == "__main__":
    start_watcher()
