# src/analyzers/pdf_intent.py
import pikepdf

def analyze_pdf_intent(path):
    """
    Extracts security intent indicators from a PDF.
    Returns:
      {
        "risk_score": float (0.0–1.0),
        "indicators": [str, ...]
      }
    """
    indicators = []
    score = 0.0

    try:
        with pikepdf.open(path) as pdf:
            root = pdf.root

            # 1️⃣ Auto-execution
            if "/OpenAction" in root:
                indicators.append("Auto-execution OpenAction")
                score += 0.5

            # 2️⃣ Embedded JavaScript
            if "/Names" in root and "/JavaScript" in root["/Names"]:
                indicators.append("Embedded JavaScript")
                score += 0.3

            # 3️⃣ Launch actions
            if "/AA" in root:
                indicators.append("Additional Actions (/AA)")
                score += 0.4

            # 4️⃣ Embedded files
            if "/EmbeddedFiles" in root.get("/Names", {}):
                indicators.append("Embedded file payload")
                score += 0.4

    except Exception:
        indicators.append("Malformed or evasive PDF structure")
        score += 0.3

    return {
        "risk_score": min(score, 1.0),
        "indicators": indicators
    }
