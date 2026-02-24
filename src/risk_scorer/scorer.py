import os
import re
import magic
import yara

# YARA rules directory
YARA_RULES_DIR = os.path.join(os.path.dirname(__file__), "yara_rules")


# -------------------------
# Load YARA rules
# -------------------------
def load_yara_rules():
    """Load all YARA rules from the local folder."""
    rules = []

    if not os.path.exists(YARA_RULES_DIR):
        print("[!] YARA rule directory missing:", YARA_RULES_DIR)
        return rules

    for file in os.listdir(YARA_RULES_DIR):
        if file.endswith(".yar"):
            try:
                filepath = os.path.join(YARA_RULES_DIR, file)
                rules.append(yara.compile(filepath=filepath))
            except Exception as e:
                print(f"[!] Error loading rule {file}: {e}")

    return rules


YARA_RULES = load_yara_rules()


# -------------------------
# URL Risk Analysis
# -------------------------
def check_url_risk(url):
    """Basic URL heuristic scoring."""
    score = 0
    reason = []

    if re.search(r"\d{5,}", url):
        score += 1
        reason.append("Contains long numeric sequences")

    if len(url) > 80:
        score += 1
        reason.append("Unusually long URL")

    if not re.match(r"^https://", url):
        score += 1
        reason.append("Non-HTTPS URL")

    if re.search(r"(free|bonus|win|verify|login|account|secure)", url.lower()):
        score += 1
        reason.append("Contains phishing keywords")

    # Map score → risk category
    if score == 0:
        return "LOW", "Clean URL"
    elif score == 1:
        return "MEDIUM", "; ".join(reason)
    else:
        return "HIGH", "; ".join(reason)


# -------------------------
# File Risk Analysis
# -------------------------
def check_file_risk(path):
    try:
        with open(path, "rb") as f:
            data = f.read(200_000)

        has_js = b"/JavaScript" in data or b"/JS" in data
        has_openaction = b"/OpenAction" in data or b"/AA" in data
        has_launch = b"/Launch" in data or b"/URI" in data
        has_polyglot = b"PK\x03\x04" in data[:1024]

        if has_openaction or has_launch or has_polyglot:
            return "HIGH", "Auto-execution or polyglot detected"

        if has_js:
            return "MEDIUM", "Active content detected"

        return "LOW", "No active content"

    except Exception as e:
        return "LOW", f"Error reading file: {e}"

    # -------- PDF HIGH-RISK INDICATORS --------

    if "/OpenAction" in text:
        return "HIGH", "PDF OpenAction auto-execution detected"

    if "/JavaScript" in text or "/JS" in text:
        return "HIGH", "Embedded JavaScript detected"

    if "/EmbeddedFile" in text:
        return "HIGH", "Embedded file detected"

    if "PK\x03\x04" in data.decode(errors="ignore"):
        return "HIGH", "Polyglot PDF-ZIP detected"


    """Static analysis + YARA rules."""
    if not os.path.exists(file_path):
        return "HIGH", "File does not exist"

    reasons = []

    # 1. File Type via MIME
    mime = magic.from_file(file_path, mime=True)
    ext = os.path.splitext(file_path)[1].lower()

    # Office macros
    if ext in [".docm", ".xlsm", ".pptm"]:
        reasons.append("Macro-enabled Office file")

    # JavaScript PDFs
    if ext == ".pdf":
        reasons.append("PDF file (possible embedded scripts)")

    # Extension vs MIME mismatch
    expected_pdf = ext == ".pdf" and mime != "application/pdf"
    expected_docx = ext == ".docx" and mime not in ["application/vnd.openxmlformats-officedocument.wordprocessingml.document"]

    if expected_docx or expected_pdf:
        reasons.append(f"Extension/MIME mismatch: {mime}")

    # 2. YARA Matching
    yara_hits = []
    for rule in YARA_RULES:
        try:
            matches = rule.match(file_path)
            if matches:
                for m in matches:
                    yara_hits.append(m.rule)
        except Exception as e:
            pass

    if yara_hits:
        reasons.append("Matched YARA: " + ", ".join(yara_hits))

    # 3. Risk Category
    if "Macro-enabled" in " ".join(reasons) or yara_hits:
        risk = "HIGH"
    elif reasons:
        risk = "MEDIUM"
    else:
        risk = "LOW"

    return risk, "; ".join(reasons) if reasons else "No issues detected"
