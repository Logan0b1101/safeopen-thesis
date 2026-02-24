# src/cdr/cdr_engine.py

import os
from pathlib import Path
import PyPDF2

def sanitize_file(path):
    path = Path(path)

    if path.suffix.lower() != ".pdf":
        return False, "Unsupported format for CDR"

    try:
        output_dir = Path("safe_outputs")
        output_dir.mkdir(exist_ok=True)

        sanitized_path = output_dir / f"{path.stem}_sanitized.pdf"

        reader = PyPDF2.PdfReader(str(path))
        writer = PyPDF2.PdfWriter()

        for page in reader.pages:
            writer.add_page(page)

        with open(sanitized_path, "wb") as f:
            writer.write(f)

        return True, str(sanitized_path)

    except Exception as e:
        return False, f"CDR error: {e}"
