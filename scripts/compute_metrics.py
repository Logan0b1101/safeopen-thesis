import pandas as pd

df = pd.read_csv("results/evaluation_results.csv")

def pred_class(label):
    return "MALICIOUS" if label in ("MEDIUM", "HIGH") else "BENIGN"

df["predicted"] = df["final_label"].apply(pred_class)

TP = ((df.ground_truth=="MALICIOUS") & (df.predicted=="MALICIOUS")).sum()
TN = ((df.ground_truth=="BENIGN") & (df.predicted=="BENIGN")).sum()
FP = ((df.ground_truth=="BENIGN") & (df.predicted=="MALICIOUS")).sum()
FN = ((df.ground_truth=="MALICIOUS") & (df.predicted=="BENIGN")).sum()

precision = TP / (TP + FP) if (TP+FP)>0 else 0
recall = TP / (TP + FN) if (TP+FN)>0 else 0
f1 = (2*precision*recall)/(precision+recall) if (precision+recall)>0 else 0

print("Confusion Matrix")
print("----------------")
print(f"TP: {TP}")
print(f"FP: {FP}")
print(f"TN: {TN}")
print(f"FN: {FN}\n")

print("Metrics")
print("-------")
print(f"Precision: {precision:.3f}")
print(f"Recall:    {recall:.3f}")
print(f"F1-score:  {f1:.3f}")
