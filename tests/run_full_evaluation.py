import os
import time
import csv
import subprocess

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EVAL_DIR = os.path.join(ROOT, "evaluation")
RESULTS_FILE = os.path.join(EVAL_DIR, "results.csv")

CLI = "python3 -m src.cli_app"

def evaluate_folder(label, folder):
    full_path = os.path.join(EVAL_DIR, folder)
    for f in os.listdir(full_path):
        file_path = os.path.join(full_path, f)
        if not os.path.isfile(file_path):
            continue

        start = time.time()
        result = subprocess.run(
            f"{CLI} \"{file_path}\"",
            shell=True,
            capture_output=True,
            text=True
        )
        end = time.time()
        elapsed = round(end - start, 3)

        with open(RESULTS_FILE, "a") as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow([f, label, elapsed, result.stdout])

        print(f"[+] Tested {f} in {elapsed}s")

if __name__ == "__main__":
    print("Running evaluation...")
    open(RESULTS_FILE, "w").write("file,label,time(s),output\n")

    evaluate_folder("malicious", "malicious")
    evaluate_folder("benign", "benign")
    evaluate_folder("mixed", "mixed")

    print("Finished. Results saved to results.csv")
