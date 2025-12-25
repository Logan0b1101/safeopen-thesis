import csv
import time
from pathlib import Path

from src.risk_scorer.scorer import check_file_risk
from src.feature_extractor import extract_features_for_ml
from src.ml_integration import MLScorer
from src.cdr.cdr_engine import sanitize_file

# ---------------- CONFIG ----------------

EVAL_DIR = Path("dataset/evaluation")
OUTPUT_CSV = Path("results/evaluation_results.csv")

# ---------------- INIT ----------------

ml = MLScorer()

rows = []

# ---------------- PROCESS ----------------

for label_dir in ["benign", "malicious", "unknown"]:
    folder = EVAL_DIR / label_dir
    if not folder.exists():
        continue

    for file_path in folder.iterdir():
        if not file_path.is_file():
            continue

        start = time.time()

        # 1. Static analysis
        static_label, static_reason = check_file_risk(str(file_path))

        # 2. ML analysis
        features = extract_features_for_ml(str(file_path))
        ml_prob, ml_details = ml.predict(features)

        # 3. Fusion logic
        static_map = {"LOW": 0.2, "MEDIUM": 0.5, "HIGH": 0.9}
        static_score = static_map.get(static_label, 0.5)

        final_score = (0.5 * static_score) + (0.4 * ml_prob)
        final_score = min(final_score, 1.0)

        if final_score >= 0.7:
            final_label = "HIGH"
            action = "SANDBOX"
        elif final_score >= 0.45:
            final_label = "MEDIUM"
            action = "CDR"
        else:
            final_label = "LOW"
            action = "NONE"

        elapsed = time.time() - start

        rows.append([
            file_path.name,
            label_dir.upper(),
            static_label,
            ml_prob,
            final_score,
            final_label,
            action,
            round(elapsed, 4),
            static_reason
        ])

        print(f"[EVAL] {file_path.name} → {final_label}")

# ---------------- SAVE ----------------

OUTPUT_CSV.parent.mkdir(exist_ok=True)

with open(OUTPUT_CSV, "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow([
        "filename",
        "ground_truth",
        "static_label",
        "ml_probability",
        "final_score",
        "final_label",
        "action",
        "latency_sec",
        "static_reason"
    ])
    writer.writerows(rows)

print(f"\n[+] Evaluation completed → {OUTPUT_CSV}")

