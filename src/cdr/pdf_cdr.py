from PyPDF2 import PdfReader, PdfWriter
from PyPDF2.generic import DictionaryObject, NameObject, ArrayObject
from pathlib import Path

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


def sanitize_pdf(pdf_path: str):
    try:
        pdf_path = Path(pdf_path)
        reader = PdfReader(str(pdf_path))
        writer = PdfWriter()

        # ------- Get /Root -------
        root = reader.trailer.get("/Root", {})
        root = _get_dict(root)

        # ------- Remove JavaScript -------
        names = root.get("/Names")
        names = _get_dict(names)

        if isinstance(names, dict):
            js = names.get("/JavaScript")
            if js:
                _safe_del(names, NameObject("/JavaScript"))

            embedded = names.get("/EmbeddedFiles")
            if embedded:
                _safe_del(names, NameObject("/EmbeddedFiles"))

        # ------- Remove OpenAction & AA -------
        _safe_del(root, NameObject("/OpenAction"))
        _safe_del(root, NameObject("/AA"))

        # ------- Process pages -------
        for page in reader.pages:
            page_obj = _get_dict(page)

            # Remove annotations
            if "/Annots" in page_obj:
                try:
                    page_obj[NameObject("/Annots")] = ArrayObject()
                except Exception:
                    pass

            writer.add_page(page_obj)

        # ------- Copy metadata safely -------
        if "/Metadata" in root:
            _safe_del(root, NameObject("/Metadata"))

        # ------- Write output -------
        output_path = SAFE_OUTPUT_DIR / f"sanitized_{pdf_path.name}"
        with open(output_path, "wb") as f:
            writer.write(f)

        return True, f"PDF sanitized → {output_path}"

    except Exception as e:
        return False, f"PDF sanitization failed: {e}"
