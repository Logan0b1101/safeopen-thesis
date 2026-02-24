# SafeOpen

**Explainability-Driven Pre-Execution Framework for Document-Based Malware Mitigation**

SafeOpen is a research prototype developed as part of a Master's thesis.  
It implements a hybrid, explainability-driven risk assessment pipeline for document-based threats and applies proportional mitigation strategies before file execution.

---

## 1. Research Context

Document-based malware remains one of the primary initial access vectors in modern cyber attacks. Attackers exploit trusted file formats such as PDF and Office documents by embedding active content (e.g., JavaScript, OpenAction triggers, macros).

SafeOpen addresses three core research objectives:

1. Pre-execution protection at the endpoint level  
2. Explainable security decision-making  
3. Proportional mitigation instead of binary allow/block logic  

The system integrates static structural analysis, explainability indicators, machine learning scoring, and a formal risk fusion model.

---

## 2. System Architecture

SafeOpen follows a layered hybrid architecture:

Filesystem Watcher  
→ Static Risk Analysis  
→ Explainability Analyzer  
→ Machine Learning Predictor  
→ Risk Fusion Engine  
→ Decision Layer (NONE / CDR / SANDBOX)  
→ Audit Logging (SQLite)

Key principle: **Analyze before execution. Escalate proportionally. Log transparently.**

---

## 3. Core Features

- Real-time filesystem monitoring daemon
- PDF structural inspection
- Detection of JavaScript and OpenAction indicators
- Hard escalation rules for deterministic execution primitives
- Hybrid weighted risk model
- Content Disarm and Reconstruction (CDR)
- Firejail sandbox integration
- SQLite-based audit logging for traceability

---

## 4. System Requirements

### Operating System
- Linux (Tested on Kali Linux and Ubuntu)

### Python
- Python 3.10 or newer

### System Dependencies

Install required system tools:

```bash
sudo apt update
sudo apt install firejail sqlite3 python3-venv
```

### Python Dependencies

Install using pip:

```bash
pip install -r requirements.txt
```

If `requirements.txt` does not exist, create it with:

```
watchdog
PyPDF2
scikit-learn
numpy
```

---

## 5. Installation

Clone repository:

```bash
git clone https://github.com/YOUR_USERNAME/SafeOpen.git
cd SafeOpen
```

Create virtual environment:

```bash
python3 -m venv venv
source venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

---

## 6. Running SafeOpen

Start the monitoring daemon:

```bash
export PYTHONPATH=$(pwd)
python3 src/daemon.py
```

The system monitors:

```
~/Downloads
```

All new files placed in this directory are automatically analyzed.

---

## 7. Demonstration / Test Execution

Example test files:

### Low Risk Example

```bash
cp dataset/benign/sample.pdf ~/Downloads/
```

Expected result:  
LOW → No mitigation.

---

### Medium Risk Example (CDR)

```bash
cp dataset/malicious/js_valid_embedded.pdf ~/Downloads/
```

Expected result:  
MEDIUM → Content Disarm and Reconstruction.

Sanitized files are generated inside:

```
safe_outputs/
```

---

### High Risk Example (Sandbox)

```bash
cp dataset/malicious/openaction_highrisk.pdf ~/Downloads/
```

Expected result:  
HIGH → Firejail sandbox execution.

---

## 8. Audit Logging

All decisions are stored in SQLite for reproducibility and transparency.

Open database:

```bash
sqlite3 safeopen_audit.db
```

View tables:

```sql
.tables
```

View logged decisions:

```sql
SELECT file_path, decision FROM events;
```

---

## 9. Risk Model

SafeOpen implements a formal weighted fusion model:

R = w_s S + w_m M + w_e E

Where:

- S = static analysis score  
- M = machine learning score  
- E = explainability score  
- w_s + w_m + w_e = 1  

Hard escalation rules override weighted scoring for deterministic execution indicators (e.g., OpenAction + JavaScript).

---

## 10. Evaluation Overview

The prototype was evaluated using a controlled dataset of benign and malicious samples.  
Performance metrics include:

- Precision
- Recall
- F1-Score
- ROC Curve
- Ablation study on explainability impact

Results demonstrate strong detection capability while maintaining proportional mitigation.

---

## 11. Limitations

- Currently focused primarily on PDF format
- Limited evaluation dataset size
- Sandbox provides isolation but limited behavioral telemetry
- Not production-hardened

---

## 12. Reproducibility

To reproduce evaluation:

1. Run daemon  
2. Execute test samples  
3. Extract logged decisions from SQLite  
4. Compute confusion matrix from logged results  

---

## 13. Academic Disclaimer

This project is developed for academic research purposes only.  
It is not intended for production deployment without further security validation, scaling, and robustness testing.

---

## Author

Khushal Kaklotar  
Master Thesis Research Project – SafeOpen  
