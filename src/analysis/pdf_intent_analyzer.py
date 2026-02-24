# src/analysis/pdf_intent_analyzer.py

import os

SUSPICIOUS_KEYWORDS = {
    "JavaScript": "Embedded JavaScript",
    "/JS": "Embedded JavaScript",
    "/OpenAction": "Auto-execution OpenAction",
    "/AA": "Additional Actions trigger",
    "/Launch": "Launch action",
    "/EmbeddedFile": "Embedded file",
    "/RichMedia": "Rich media content",
    "/XFA": "Dynamic XFA form",
}

def analyze_pdf_intent(file_path):
    """
    Static semantic inspection of PDF structure to infer execution intent.
    Returns None or dict(intent, indicators, confidence)
    """

    if not file_path.lower().endswith(".pdf"):
        return None

    try:
        with open(file_path, "rb") as f:
            data = f.read(200_000)  # first 200KB is enough for object graph
    except Exception:
        return None

    text = data.decode("latin-1", errors="ignore")

    indicators = []

    for key, description in SUSPICIOUS_KEYWORDS.items():
        if key in text:
            indicators.append(description)

    if not indicators:
        return None

    # Intent classification
    if any("Auto-execution" in i for i in indicators):
        intent = "AUTO_EXECUTION"
        confidence = 0.95
    elif any("JavaScript" in i for i in indicators):
        intent = "SCRIPT_EXECUTION"
        confidence = 0.85
    elif any("Embedded file" in i for i in indicators):
        intent = "PAYLOAD_DELIVERY"
        confidence = 0.80
    else:
        intent = "SUSPICIOUS_DOCUMENT"
        confidence = 0.70

    return {
        "intent": intent,
        "indicators": indicators,
        "confidence": confidence
    }
