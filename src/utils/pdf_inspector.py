# src/utils/pdf_inspector.py

def extract_pdf_indicators(file_path):
    """
    Lightweight static inspection for malicious PDF indicators.
    Returns a list of human-readable indicators.
    """
    indicators = []

    try:
        with open(file_path, "rb") as f:
            data = f.read().lower()

        if b"/javascript" in data or b"/js" in data:
            indicators.append("Embedded JavaScript")

        if b"/openaction" in data:
            indicators.append("Auto-execution OpenAction")

        if b"/launch" in data:
            indicators.append("External Launch Action")

        if b"%pdf" in data and b"pk\x03\x04" in data:
            indicators.append("Polyglot PDF/ZIP structure")

    except Exception:
        indicators.append("Static inspection failed")

    return indicators
