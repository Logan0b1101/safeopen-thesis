#!/usr/bin/env python3
"""
SafeOpen Thesis Extractor (Clean Local Version)
-----------------------------------------------
This script:
- Finds your PDF automatically
- Extracts all text
- Splits into chapters
- Saves markdown + JSON + CSV
- Creates an output folder 'safeopen_extract'
"""

import re
import json
import pandas as pd
from pathlib import Path

# -------------------------------
# 1) Auto-detect the PDF file
# -------------------------------
pdf_candidates = list(Path(".").glob("*.pdf"))
if not pdf_candidates:
    raise FileNotFoundError("❌ No PDF file found in current directory. "
                            "Place your thesis PDF here.")

PDF_PATH = pdf_candidates[0]
print(f"📄 Using PDF: {PDF_PATH.name}")

# -------------------------------
# 2) Try extraction engines
# -------------------------------

def extract_pdf_text(path: Path):
    errors = {}

    # 1. pdfplumber
    try:
        import pdfplumber
        with pdfplumber.open(str(path)) as pdf:
            pages = [p.extract_text() or "" for p in pdf.pages]
        return "\n\n".join(pages)
    except Exception as e:
        errors["pdfplumber"] = str(e)

    # 2. PyMuPDF (fitz)
    try:
        import fitz
        doc = fitz.open(str(path))
        pages = [p.get_text("text") for p in doc]
        return "\n\n".join(pages)
    except Exception as e:
        errors["pymupdf"] = str(e)

    # 3. PyPDF2
    try:
        import PyPDF2
        reader = PyPDF2.PdfReader(str(path))
        pages = [pg.extract_text() or "" for pg in reader.pages]
        return "\n\n".join(pages)
    except Exception as e:
        errors["pypdf2"] = str(e)

    print("❌ All extractors failed:")
    print(json.dumps(errors, indent=2))
    raise RuntimeError("Cannot extract PDF text.")

# Extract text
text = extract_pdf_text(PDF_PATH)
clean = re.sub(r'\r\n?', '\n', text)
clean = re.sub(r'\n{3,}', '\n\n', clean).strip()

# -------------------------------
# 3) Output folder
# -------------------------------
OUT_DIR = Path("safeopen_extract")
OUT_DIR.mkdir(exist_ok=True)

# -------------------------------
# 4) Split into chapters (simple)
# -------------------------------
chapter_header = re.compile(r"(?im)^chapter\s+\d+.*$")
matches = list(chapter_header.finditer(clean))

chapters = []

if matches:
    print(f"📘 Detected {len(matches)} chapter headers.")
    boundaries = [m.start() for m in matches] + [len(clean)]
    for i, m in enumerate(matches):
        title = m.group(0).strip()
        start = m.start()
        end = boundaries[i+1]
        content = clean[start:end].strip()
        chapters.append({"title": title, "content": content})
else:
    print("⚠ No chapter headings found. Saving whole document as single chapter.")
    chapters.append({"title": "FullDocument", "content": clean})

# -------------------------------
# 5) Save chapters + structure
# -------------------------------
summary = []

for i, ch in enumerate(chapters, start=1):
    safe_title = re.sub(r"[^\w\- ]", "", ch["title"]).strip().replace(" ", "_")
    md_path = OUT_DIR / f"{i:02d}_{safe_title}.md"

    with open(md_path, "w", encoding="utf-8") as f:
        f.write(f"# {ch['title']}\n\n{ch['content']}\n")

    summary.append({
        "index": i,
        "title": ch["title"],
        "file": str(md_path),
        "words": len(ch["content"].split())
    })

# Save JSON structure
json_path = OUT_DIR / "thesis_structure.json"
with open(json_path, "w", encoding="utf-8") as f:
    json.dump(chapters, f, indent=2)

# Save CSV summary
csv_path = OUT_DIR / "chapters_summary.csv"
pd.DataFrame(summary).to_csv(csv_path, index=False)

# Save full document
full_md = OUT_DIR / "00_full_extracted.md"
with open(full_md, "w", encoding="utf-8") as f:
    f.write(clean)

# -------------------------------
# 6) Done
# -------------------------------
print("\n✅ Extraction Complete!")
print(f"📁 Output folder: {OUT_DIR.resolve()}\n")
print(f"Files created:")
print(f"- {full_md}")
print(f"- {json_path}")
print(f"- {csv_path}")
print("📄 And separate markdown files for each chapter.")
