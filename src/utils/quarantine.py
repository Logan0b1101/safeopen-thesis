import os
import shutil

QUARANTINE_DIR = os.path.expanduser("~/SafeOpen/quarantine")

os.makedirs(QUARANTINE_DIR, exist_ok=True)

def quarantine_file(path):
    if not os.path.exists(path):
        return False

    base = os.path.basename(path)
    dst = os.path.join(QUARANTINE_DIR, base)

    shutil.move(path, dst)
    return True
