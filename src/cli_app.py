import sys
import os
from src.risk_scorer import scorer
from src.sandbox_manager.sandbox import open_in_sandbox
from src.cdr.cdr_engine import sanitize_file
from src.feature_extractor import extract_features_for_ml as extract_features
from src.ml_integration import MLScorer


def compute_hybrid_score(static_label, ml_prob, cdr_flag):
    """Combine static + ML + CDR into a final hybrid score."""
    
    static_map = {"LOW": 0.2, "MEDIUM": 0.5, "HIGH": 0.9}
    static_score = static_map.get(static_label, 0.5)

    # base hybrid
    hybrid = (0.5 * static_score) + (0.4 * ml_prob)

    # CDR bonus risk
    if cdr_flag:
        hybrid += 0.1

    return min(hybrid, 1.0)


def hybrid_label(score):
    """Convert hybrid numeric score → categorical label."""
    if score >= 0.7:
        return "HIGH"
    elif score >= 0.45:
        return "MEDIUM"
    return "LOW"


def main():

    # ------------------------------
    # 1. Argument check
    # ------------------------------
    if len(sys.argv) < 2:
        print("Usage: python3 -m src.cli_app <file_path>")
        return
    
    # FORCE ABSOLUTE PATH HERE
    file_path = os.path.abspath(sys.argv[1])

    # Check if file exists before doing anything else
    if not os.path.exists(file_path):
        print(f"❌ Error: The file '{file_path}' does not exist.")
        return 

    print(f"\n🔍 Scanning file: {file_path}")

    # ------------------------------
    # 2. Static Risk Scoring
    # ------------------------------
    static_label, static_reason = scorer.check_file_risk(file_path)
    print(f"🧠 Static Risk Level: {static_label}")
    print(f"📋 Reason: {static_reason}")

    # ------------------------------
    # 3. ML Scoring
    # ------------------------------
    print("\n🤖 Extracting features for ML...")
    features = extract_features(file_path)

    ml = MLScorer()
    ml_prob, ml_probs = ml.predict_proba(features)

    print(f"🔬 ML Malicious Probability: {ml_prob:.4f}")

    # ------------------------------
    # 4. CDR Risk Flag (if PDF or macro)
    # ------------------------------
    cdr_flag = False
    if "PDF" in static_reason or "Macro" in static_reason:
        cdr_flag = True

    # ------------------------------
    # 5. Hybrid Score
    # ------------------------------
    final_num = compute_hybrid_score(static_label, ml_prob, cdr_flag)
    final_label = hybrid_label(final_num)

    print(f"\n🧩 Hybrid Combined Score: {final_num:.3f}")
    print(f"🏁 Final Hybrid Decision: {final_label}")

    # ------------------------------
    # 6. Action based on hybrid score
    # ------------------------------
    if final_label == "HIGH":
        print("\n🔒 High risk detected — Opening in Sandbox...")
        success, msg = open_in_sandbox(file_path)
        print(msg)

    elif final_label == "MEDIUM":
        print("\n🧼 Medium risk — Applying CDR sanitization...")
        success, msg = sanitize_file(file_path)
        print(msg)

    else:
        print("\n✅ File appears safe. No sandbox/CDR needed.")

    print("\n--- Analysis Complete ---\n")


if __name__ == "__main__":
    main()
