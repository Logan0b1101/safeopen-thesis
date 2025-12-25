# src/feature_extractor.py
import os
from collections import Counter
import math

def read_bytes(path, maxb=65536):
    try:
        with open(path,"rb") as f:
            return f.read(maxb)
    except:
        return b""

def shannon_entropy(b):
    if not b:
        return 0.0
    counts = Counter(b)
    probs = [c/len(b) for c in counts.values()]
    return -sum(p * math.log2(p) for p in probs if p>0)

def byte_hist(b):
    hist = [0]*256
    for x in b:
        hist[x] += 1
    s = sum(hist)
    if s>0:
        hist = [h/s for h in hist]
    return hist

def extract_features_for_ml(file_path):
    b = read_bytes(file_path)
    ent = shannon_entropy(b)
    hist = byte_hist(b)
    text = ""
    try:
        text = b.decode("latin-1", errors="ignore").lower()
    except:
        text = ""
    feat = {}
    feat['size'] = os.path.getsize(file_path)
    feat['entropy'] = ent
    feat['js_flag'] = int(("javascript" in text) or ("/js" in text) or ("app.alert" in text))
    feat['macro_flag'] = int(("vba" in text) or ("macro" in text) or ("sub autoopen" in text))
    # add hist_0..hist_255
    for i,v in enumerate(hist):
        feat[f"hist_{i}"] = v
    # ext handling if model expects ext_* one-hot fields, those will be filled by MLScorer from feature_order (defaults 0)
    return feat
