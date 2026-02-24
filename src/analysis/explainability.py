# src/analyzers/explainability.py

import re

PDF_INDICATORS = {
    "JavaScript": re.compile(rb"/JavaScript", re.I),
    "OpenAction": re.compile(rb"/OpenAction", re.I),
    "Launch": re.compile(rb"/Launch", re.I),
    "EmbeddedJSStream": re.compile(rb"stream.*?JavaScript", re.I | re.S),
    "ZIPPolyglot": re.compile(rb"PK\x03\x04"),
}

def analyze_pdf_explainability(file_path):
    """
    Returns:
    indicators (list[str]),
    explanation (str),
    escalation_score (float)
    """
    indicators = []
    score = 0.0

    try:
        with open(file_path, "rb") as f:
            data = f.read(500000)  # read first 500KB only

        for name, pattern in PDF_INDICATORS.items():
            if pattern.search(data):
                indicators.append(name)

        # Risk scoring
        if "JavaScript" in indicators:
            score += 0.3
        if "OpenAction" in indicators:
            score += 0.4
        if "Launch" in indicators:
            score += 0.4
        if "ZIPPolyglot" in indicators:
            score += 0.5
        if "EmbeddedJSStream" in indicators:
            score += 0.2

        if indicators:
            explanation = (
                "PDF contains active content indicators: "
                + ", ".join(indicators)
            )
        else:
            explanation = "No active content indicators detected."

        return indicators, explanation, min(score, 1.0)

    except Exception as e:
        return [], f"Explainability analysis failed: {e}", 0.0
