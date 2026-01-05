# src/utils/pdf_indicators.py
import pikepdf

def extract_pdf_indicators(pdf_path):
    """
    Extract high-risk PDF indicators for explainable escalation.
    Returns a list of indicator strings.
    """
    indicators = []

    try:
        with pikepdf.open(pdf_path) as pdf:
            root = pdf.root

            # 1. JavaScript
            if "/Names" in root:
                names = root["/Names"]
                if "/JavaScript" in names:
                    indicators.append("Embedded JavaScript")

            # 2. OpenAction (auto execution)
            if "/OpenAction" in root:
                indicators.append("Auto-execution OpenAction")

            # 3. Embedded files
            if "/EmbeddedFiles" in root:
                indicators.append("Embedded File")

            # 4. Launch action
            if "/AA" in root:
                indicators.append("Additional Actions (AA)")

    except Exception:
        # Fail-safe: never crash daemon
        pass

    return indicators
