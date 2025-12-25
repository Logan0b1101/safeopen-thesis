import joblib
import json
import numpy as np
from pathlib import Path
from src.feature_extractor import extract_features_for_ml

BASE = Path("ml_results_advanced")

rf_model = joblib.load(BASE / "random_forest_model.pkl")
lr_model = joblib.load(BASE / "logistic_model.pkl")
scaler = joblib.load(BASE / "scaler.pkl")

with open(BASE / "feature_order.json") as f:
    FEATURE_ORDER = json.load(f)

def predict_file_features(feature_dict):
    """
    Predict malicious probability from extracted feature dictionary.
    Uses RF + LR ensemble.
    """
    X = np.array([[feature_dict.get(f, 0) for f in FEATURE_ORDER]])
    Xs = scaler.transform(X)

    rf_prob = rf_model.predict_proba(Xs)[0][1]
    lr_prob = lr_model.predict_proba(Xs)[0][1]

    combined = 0.6 * rf_prob + 0.4 * lr_prob
    return combined, {"rf": rf_prob, "lr": lr_prob}

def predict_file(path):
    """
    Full pipeline:
    file -> features -> ML probability
    """
    features = extract_features_for_ml(path)
    return predict_file_features(features)
