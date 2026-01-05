# src/cdr/cdr_engine.py
import shutil
from pathlib import Path

SANITIZED_DIR = Path.home() / "SafeOpen" / "sanitized"
SANITIZED_DIR.mkdir(parents=True, exist_ok=True)

def sanitize_file(path):
    try:
        src = Path(path)
        dst = SANITIZED_DIR / f"{src.stem}_sanitized{src.suffix}"

        # ⚠️ Thesis note:
        # Real CDR removes active content.
        # Here we simulate safe reconstruction.
        shutil.copy(src, dst)

        return True, str(dst)

    except Exception as e:
        return False, str(e)
