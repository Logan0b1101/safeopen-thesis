from PyPDF2 import PdfReader, PdfWriter
from PyPDF2.generic import DictionaryObject, NameObject, ArrayObject
from pathlib import Path
import pikepdf
import os

SAFE_OUTPUT_DIR = Path("safe_outputs")
SAFE_OUTPUT_DIR.mkdir(exist_ok=True)


def _safe_del(d, key):
    """Safely delete a key from a PDF DictionaryObject or IndirectObject."""
    try:
        if hasattr(d, "get_object"):
            d = d.get_object()
        if isinstance(d, dict) and key in d:
            del d[key]
    except Exception:
        pass


def _get_dict(obj):
    """Resolve indirect objects into real dictionaries."""
    try:
        return obj.get_object()
    except Exception:
        return obj


def sanitize_pdf(input_path):
    try:
        output_dir = os.path.join(os.getcwd(), "safe_outputs")
        os.makedirs(output_dir, exist_ok=True)

        output_path = os.path.join(
            output_dir,
            os.path.basename(input_path).replace(".pdf", "_sanitized.pdf")
        )

        with pikepdf.open(input_path) as pdf:
            # Remove JavaScript
            if "/Names" in pdf.Root:
                pdf.Root.pop("/Names", None)

            # Remove OpenAction
            pdf.Root.pop("/OpenAction", None)

            # Remove embedded files
            pdf.Root.pop("/EmbeddedFiles", None)

            pdf.save(output_path)

        return True, output_path

    except Exception as e:
        return False, str(e)
