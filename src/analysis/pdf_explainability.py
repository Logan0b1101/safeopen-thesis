# src/analyzers/pdf_explainability.py

from pathlib import Path
import PyPDF2

# src/analyzers/pdf_explainability.py

def analyze_pdf_explainability(file_path):
    indicators = []

    try:
        with open(file_path, "rb") as f:
            data = f.read(200_000)

        if b"/JavaScript" in data or b"/JS" in data:
            indicators.append("Embedded JavaScript")

        if b"/OpenAction" in data or b"/AA" in data:
            indicators.append("Auto-execution OpenAction")

        if b"/Launch" in data:
            indicators.append("Launch action detected")

        if b"PK\x03\x04" in data[:1024]:
            indicators.append("Polyglot PDF-ZIP structure")

        if b"/URI" in data:
            indicators.append("External URL invocation")

    except Exception as e:
        indicators.append(f"Explainability error: {e}")

    return indicators
