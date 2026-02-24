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
from src.analysis.explainability import analyze_pdf_explainability

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

#--------scan file handler-----------#

   def scan_file(self, path):
    start_time = time.time()

    try:
        # ---------------- Static Analysis ----------------
        static_label, static_reason = check_file_risk(path)

        # ---------------- Explainability Analysis (PDF) ----------------
        indicators = []
        explain_reason = ""
        explain_score = 0.0

        if path.lower().endswith(".pdf"):
            indicators, explain_reason, explain_score = analyze_pdf_explainability(path)

        if explain_reason:
            static_reason = f"{static_reason} | {explain_reason}"

        # ---------------- ML Analysis ----------------
        ml_prob = 0.0
        if ml:
            features = extract_features_for_ml(path)
            ml_prob, _ = ml.predict(features)

        # ---------------- Indicator Escalation ----------------
        escalated = False

        if indicators:
            if "Auto-execution OpenAction" in indicators:
                escalated = True
            elif "Embedded JavaScript" in indicators:
                escalated = True

            static_reason += " | Indicators: " + ", ".join(indicators)

        # ---------------- Score Fusion ----------------
        static_map = {"LOW": 0.2, "MEDIUM": 0.5, "HIGH": 0.9}
        static_score = static_map.get(static_label, 0.5)

        final_score = (0.4 * static_score + 0.4 * ml_prob + 0.2 * explain_score)
        final_score = min(final_score, 1.0)

        # ---------------- Decision Logic ----------------
        action_result = "NONE"

        if escalated:
            final_label = "HIGH"
            action = "SANDBOX"
            action_result = "Structural execution indicators detected"

        elif final_score >= 0.65:
            final_label = "HIGH"
            action = "SANDBOX"
            action_result = "High composite risk score"

        elif final_score >= 0.40:
            final_label = "MEDIUM"
            action = "CDR"
            ok, result = sanitize_file(path)
            if ok:
                action_result = f"Sanitized → {result}"
            else:
                action_result = f"CDR failed: {result}"

        else:
            final_label = "LOW"
            action = "NONE"
            action_result = "No active content detected"

        latency = time.time() - start_time

        log_event(
            file_path=path,
            static_label=static_label,
            static_reason=static_reason,
            ml_prob=ml_prob,
            final_score=final_score,
            final_label=final_label,
            action=action,
            action_result=action_result,
            latency=float(latency)
        )

        print(f"[daemon] {path} → {final_label} ({action})")
        print(f"Reason: {static_reason}")

    except Exception:
        print(f"[daemon] ERROR scanning: {path}")
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
