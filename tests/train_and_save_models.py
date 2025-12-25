#!/usr/bin/env python3
"""
Train (or re-train) LogisticRegression and RandomForest on your processed dataset
and save models + scaler + encoder + feature order to ml_results_advanced/.
Run from project root inside venv:

python3 tests/train_and_save_models.py
"""
import os, json
import pandas as pd
import numpy as np
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
import joblib

PROJECT_ROOT = os.path.expanduser("~/thesis/~safeopen")
OUT_DIR = os.path.join(PROJECT_ROOT, "ml_results_advanced")
os.makedirs(OUT_DIR, exist_ok=True)

# 1) Try to load processed dataset produced by previous pipeline.
# Look for processed_dataset.csv or features_table.csv in OUT_DIR or PROJECT_ROOT.
candidates = [
    os.path.join(OUT_DIR, "processed_dataset.csv"),
    os.path.join(OUT_DIR, "features_table.csv"),
    os.path.join(PROJECT_ROOT, "ml_results_advanced", "processed_dataset.csv"),
    os.path.join(PROJECT_ROOT, "ml_results_advanced", "features_table.csv"),
    os.path.join(PROJECT_ROOT, "ml_results_advanced", "processed_dataset.csv")
]

df = None
for p in candidates:
    if os.path.exists(p):
        print("Using features file:", p)
        df = pd.read_csv(p)
        break

if df is None:
    # fallback: try to build from evaluation files (calls the previous run pipeline)
    eval_csv = os.path.join(PROJECT_ROOT, "evaluation", "results.csv")
    if not os.path.exists(eval_csv):
        raise SystemExit("No processed dataset found and evaluation/results.csv missing. Place results.csv under evaluation/ and raw files under evaluation/*")
    # Lightweight fallback: use file name tokens + time(s)
    df0 = pd.read_csv(eval_csv)
    records = []
    def ext_from_name(n):
        p = str(n)
        return p.split('.')[-1].lower() if '.' in p else 'other'
    for _, r in df0.iterrows():
        if str(r.get("label","")).lower() not in ("malicious","benign"):
            continue
        name = r['file']
        rec = {
            "file": name,
            "label": 1 if str(r['label']).lower()=="malicious" else 0,
            "time_s": float(r.get("time(s)",0.0)),
            "has_test": int("test" in name.lower()),
            "has_phish": int("phish" in name.lower()),
            "has_macro": int("macro" in name.lower() or name.lower().endswith("docm")),
            "has_js": int("js" in name.lower() or "javascript" in name.lower()),
            "name_len": len(name),
            "ext": ext_from_name(name)
        }
        records.append(rec)
    df = pd.DataFrame(records)
    # one-hot encode ext later

# df should now contain label + features or hist columns
# Standardize pipeline expectations: label column named 'label' and features present
if 'label' not in df.columns:
    raise SystemExit("Loaded dataset has no 'label' column. Aborting.")

# Choose feature columns automatically: numeric columns except file/path/label
drop_cols = [c for c in df.columns if c.lower() in ('file','path')]
feature_columns = [c for c in df.columns if c not in drop_cols + ['label']]

# If ext column exists, apply OneHotEncoder and remove original ext
 #if 'ext' in feature_columns:
     #pass

# Handle categorical ext
if 'ext' in df.columns:
    ext_vals = df['ext'].astype(str).fillna('other')
    top_ext = ext_vals.value_counts().nlargest(10).index.tolist()
    df['ext'] = df['ext'].apply(lambda x: x if x in top_ext else 'other')
    ohe = OneHotEncoder(sparse_output=False, handle_unknown='ignore')
    ext_ohe = ohe.fit_transform(df[['ext']])
    ext_cols = [f"ext_{c}" for c in ohe.categories_[0]]
    ext_df = pd.DataFrame(ext_ohe, columns=ext_cols, index=df.index)
    df = pd.concat([df.drop(columns=['ext']), ext_df], axis=1)
else:
    ohe = None
    ext_cols = []

# Ensure hist_* columns (if present) remain ordered
hist_cols = sorted([c for c in df.columns if c.startswith("hist_")], key=lambda x: int(x.split('_')[1])) if any(c.startswith("hist_") for c in df.columns) else []
# Build final feature list deterministically
numeric_cols = [c for c in df.columns if c not in ['file','path','label'] and not c.startswith('hist_') and not c.startswith('ext_')]
feature_order = numeric_cols + ext_cols + hist_cols

X = df[feature_order].fillna(0).values
y = df['label'].astype(int).values

# Train-test split (for final model we train on all; but keep a split for quick eval)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25, random_state=42, stratify=y)

# Scale features
scaler = StandardScaler()
X_train_s = scaler.fit_transform(X_train)
X_test_s = scaler.transform(X_test)

# Train models
lr = LogisticRegression(max_iter=2000, class_weight='balanced', random_state=42)
rf = RandomForestClassifier(n_estimators=300, class_weight='balanced', random_state=42)

lr.fit(X_train_s, y_train)
rf.fit(X_train_s, y_train)

# Save artifacts
joblib.dump(lr, os.path.join(OUT_DIR, "logistic_model.pkl"))
joblib.dump(rf, os.path.join(OUT_DIR, "random_forest_model.pkl"))
joblib.dump(scaler, os.path.join(OUT_DIR, "scaler.pkl"))
if ohe is not None:
    joblib.dump(ohe, os.path.join(OUT_DIR, "ohe.pkl"))
# Save feature order
with open(os.path.join(OUT_DIR, "feature_order.json"), "w") as f:
    json.dump(feature_order, f, indent=2)

# Quick evaluation on held-out test
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
X_test_full = scaler.transform(X_test)
print("LR test acc:", accuracy_score(y_test, lr.predict(X_test_full)))
print("RF test acc:", accuracy_score(y_test, rf.predict(X_test_full)))

print("Saved models to:", OUT_DIR)
