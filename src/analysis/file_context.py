# src/analysis/file_context.py
import subprocess
import os

def analyze_file_context(file_path):
    reasons = []

    # MIME mismatch
    try:
        mime = subprocess.check_output(["file", "--mime-type", "-b", file_path]).decode().strip()
        ext = os.path.splitext(file_path)[1].lower()

        if ext == ".pdf" and mime != "application/pdf":
            reasons.append("MIME mismatch")

    except Exception:
        pass

    # Polyglot hint
    try:
        with open(file_path, "rb") as f:
            data = f.read(2048)
            if b"PK\x03\x04" in data and b"%PDF" in data:
                reasons.append("PDF-ZIP polyglot")

    except Exception:
        pass

    return reasons

