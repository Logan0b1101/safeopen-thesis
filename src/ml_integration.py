from pathlib import Path
import joblib
import json
import numpy as np

BASE = Path("ml_results_advanced")

class MLScorer:
    def __init__(self):
        required = [
            BASE / "random_forest_model.pkl",
            BASE / "logistic_model.pkl",
            BASE / "scaler.pkl",
            BASE / "feature_order.json"
        ]

        for f in required:
            if not f.exists():
                raise FileNotFoundError(
                    f"Missing ML artifact: {f}. Train model before evaluation."
                )

        self.rf_model = joblib.load(BASE / "random_forest_model.pkl")
        self.lr_model = joblib.load(BASE / "logistic_model.pkl")
        self.scaler = joblib.load(BASE / "scaler.pkl")

        with open(BASE / "feature_order.json") as fh:
            self.feature_order = json.load(fh)

    def predict(self, feature_dict):
        X = np.array([[feature_dict.get(f, 0) for f in self.feature_order]])
        Xs = self.scaler.transform(X)

        rf_prob = self.rf_model.predict_proba(Xs)[0][1]
        lr_prob = self.lr_model.predict_proba(Xs)[0][1]

        combined = 0.6 * rf_prob + 0.4 * lr_prob
        return combined, {
            "rf": float(rf_prob),
            "lr": float(lr_prob)
        }
