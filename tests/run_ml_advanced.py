#!/usr/bin/env python3
"""
Advanced ML pipeline for SafeOpen
Auto-detects results.csv and evaluation files.
Place this script in: ~/thesis/~safeopen/tests/run_ml_advanced.py

Run:
    python3 tests/run_ml_advanced.py
"""

import os
import math
import pandas as pd
import numpy as np
from collections import Counter
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix,
    classification_report
)
from sklearn.decomposition import PCA
import matplotlib.pyplot as plt


# -----------------------------------------------------------
# CONFIG — auto detect your SafeOpen project root
# -----------------------------------------------------------

HOME = os.path.expanduser("~")
PROJECT_ROOT = os.path.join(HOME, "thesis", "~safeopen")
EVAL_DIR = os.path.join(PROJECT_ROOT, "evaluation")

RESULTS_FILE = os.path.join(EVAL_DIR, "results.csv")  # Must exist

OUT_DIR = os.path.join(PROJECT_ROOT, "ml_results_advanced")
os.makedirs(OUT_DIR, exist_ok=True)


# -------------------------
# Utility functions
# -------------------------
def read_bytes_safe(path, max_bytes=65536):
    try:
        with open(path, "rb") as f:
            return f.read(max_bytes)
    except:
        return None


def shannon_entropy(data: bytes) -> float:
    if not data:
        return 0.0
    counts = Counter(data)
    probs = [c/len(data) for c in counts.values()]
    return -sum(p * math.log2(p) for p in probs if p > 0)


def byte_histogram(data: bytes, normalize=True):
    hist = np.zeros(256)
    for b in data:
        hist[b] += 1
    if normalize and hist.sum() > 0:
        hist /= hist.sum()
    return hist


# -------------------------
# Load data
# -------------------------
if not os.path.exists(RESULTS_FILE):
    raise FileNotFoundError(f"❌ results.csv not found at: {RESULTS_FILE}\n"
                            "Move your results.csv there and retry.")

print(f"[+] Loading results: {RESULTS_FILE}")
df = pd.read_csv(RESULTS_FILE)

print(df)


# -------------------------
# Build features from actual files
# -------------------------
features = []
missing_files = []

for _, row in df.iterrows():
    fname = row["file"]
    label = row["label"].lower()

    # Convert label → integer
    if label == "malicious":
        y = 1
    elif label == "benign":
        y = 0
    else:
        continue  # skip mixed

    # Search for actual file inside evaluation directory
    found_path = None
    for root, dirs, files in os.walk(EVAL_DIR):
        if fname in files:
            found_path = os.path.join(root, fname)
            break

    if not found_path:
        missing_files.append(fname)
        continue

    data = read_bytes_safe(found_path)
    if data is None:
        missing_files.append(found_path)
        continue

    # Extract features
    entropy = shannon_entropy(data)
    hist = byte_histogram(data)
    ext = os.path.splitext(found_path)[1].lower().replace(".", "")

    text = data.decode("latin-1", errors="ignore").lower()
    js_flag = int(("javascript" in text) or ("app.alert" in text))
    macro_flag = int(("vba" in text) or ("sub autoopen" in text) or ("macro" in text))

    features.append({
        "file": fname,
        "label": y,
        "size": os.path.getsize(found_path),
        "entropy": entropy,
        "js_flag": js_flag,
        "macro_flag": macro_flag,
        "ext": ext,
        "hist": hist.tolist()
    })


if missing_files:
    print("⚠ Missing files:", missing_files)


if len(features) < 4:
    raise ValueError("❌ Not enough files to train ML model. Need at least 4 supervised examples.")


# -------------------------
# Prepare ML dataset
# -------------------------
rows = []
for f in features:
    base = {
        "file": f["file"],
        "label": f["label"],
        "size": f["size"],
        "entropy": f["entropy"],
        "js_flag": f["js_flag"],
        "macro_flag": f["macro_flag"],
        "ext": f["ext"],
    }
    for i, v in enumerate(f["hist"]):
        base[f"hist_{i}"] = v
    rows.append(base)

df_feat = pd.DataFrame(rows)

# One-hot extension
top_ext = df_feat["ext"].value_counts().nlargest(5).index.tolist()
df_feat["ext"] = df_feat["ext"].apply(lambda x: x if x in top_ext else "other")

ohe = OneHotEncoder(sparse_output=False, handle_unknown="ignore")
ext_ohe = ohe.fit_transform(df_feat[["ext"]])
ext_cols = [f"ext_{c}" for c in ohe.categories_[0]]
ext_df = pd.DataFrame(ext_ohe, columns=ext_cols, index=df_feat.index)

# Combine
base_cols = ["size", "entropy", "js_flag", "macro_flag"]
hist_cols = [f"hist_{i}" for i in range(256)]

X = pd.concat([df_feat[base_cols], ext_df, df_feat[hist_cols]], axis=1).values
y = df_feat["label"].values
feature_names = list(pd.concat([df_feat[base_cols], ext_df, df_feat[hist_cols]], axis=1).columns)

# Scaling
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# Train/Test split
X_train, X_test, y_train, y_test = train_test_split(
    X_scaled, y, test_size=0.33, random_state=42, stratify=y
)

# -------------------------
# Train Models
# -------------------------
lr = LogisticRegression(max_iter=2000, class_weight="balanced")
rf = RandomForestClassifier(n_estimators=300, class_weight="balanced")

lr.fit(X_train, y_train)
rf.fit(X_train, y_train)

lr_pred = lr.predict(X_test)
rf_pred = rf.predict(X_test)

# -------------------------
# Metrics
# -------------------------
def metrics(y_true, y_pred):
    return {
        "accuracy": accuracy_score(y_true, y_pred),
        "precision": precision_score(y_true, y_pred),
        "recall": recall_score(y_true, y_pred),
        "f1": f1_score(y_true, y_pred)
    }

lr_m = metrics(y_test, lr_pred)
rf_m = metrics(y_test, rf_pred)

pd.DataFrame([lr_m, rf_m], index=["LogReg", "RandomForest"]).to_csv(
    os.path.join(OUT_DIR, "model_metrics.csv")
)

print("✔ ML metrics saved to model_metrics.csv")
print(lr_m, rf_m)


# -------------------------
# Save Confusion Matrices
# -------------------------
pd.DataFrame(confusion_matrix(y_test, lr_pred)).to_csv(os.path.join(OUT_DIR, "cm_lr.csv"))
pd.DataFrame(confusion_matrix(y_test, rf_pred)).to_csv(os.path.join(OUT_DIR, "cm_rf.csv"))


# -------------------------
# Feature Importance
# -------------------------
feat_imp = pd.DataFrame({
    "feature": feature_names,
    "importance": rf.feature_importances_
}).sort_values("importance", ascending=False)

feat_imp.to_csv(os.path.join(OUT_DIR, "feature_importances.csv"), index=False)


# -------------------------
# PCA plot
# -------------------------
pca = PCA(n_components=2)
Xp = pca.fit_transform(X_scaled)

plt.figure()
plt.scatter(Xp[:, 0], Xp[:, 1], c=y, s=40)
plt.title("PCA of SafeOpen Features")
plt.savefig(os.path.join(OUT_DIR, "pca_plot.png"))
plt.close()

print("🎉 ML Evaluation Completed Successfully!")
print(f"All results saved in: {OUT_DIR}")
