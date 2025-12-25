import os
import json
import zipfile

ROOT = os.path.expanduser("~/thesis/~safeopen")
OUT = os.path.join(ROOT, "dataset", "benign")
os.makedirs(OUT, exist_ok=True)

created = []


# ------------------------------------------
# 1) Clean PDF (simple text-based)
# ------------------------------------------
pdf1 = os.path.join(OUT, "clean_report.pdf")
with open(pdf1, "wb") as f:
    f.write(b"%PDF-1.4\n")
    f.write(b"1 0 obj << /Type /Catalog >> endobj\n")
    f.write(b"%%EOF\n")
created.append(pdf1)


# ------------------------------------------
# 2) Resume PDF (just text)
# ------------------------------------------
resume = os.path.join(OUT, "resume.pdf")
with open(resume, "w") as f:
    f.write("John Doe\nSoftware Engineer Resume\nSkills: Python, Linux, Security\n")
created.append(resume)


# ------------------------------------------
# 3) Clean DOCX (simulated — not real DOCX)
# ------------------------------------------
docx1 = os.path.join(OUT, "project_notes.docx")
with open(docx1, "w") as f:
    f.write("This is a benign project notes document.\nNo macros.\n")
created.append(docx1)


# ------------------------------------------
# 4) Plain text file
# ------------------------------------------
txt = os.path.join(OUT, "notes.txt")
with open(txt, "w") as f:
    f.write("Reminder: Submit thesis draft.\n")
created.append(txt)


# ------------------------------------------
# 5) JSON config file
# ------------------------------------------
json_path = os.path.join(OUT, "config.json")
with open(json_path, "w") as f:
    json.dump({"setting": "enabled", "version": "1.0"}, f, indent=2)
created.append(json_path)


# ------------------------------------------
# 6) Simple ZIP archive
# ------------------------------------------
zip_path = os.path.join(OUT, "documents.zip")
with zipfile.ZipFile(zip_path, "w") as zf:
    zf.writestr("clean.txt", "This is a clean file inside a ZIP.\n")
    zf.writestr("readme.md", "No malicious content here.\n")
created.append(zip_path)


# ------------------------------------------
# 7) Clean image (binary placeholder)
# ------------------------------------------
img = os.path.join(OUT, "photo.jpg")
with open(img, "wb") as f:
    f.write(b"\xFF\xD8\xFF\xE0" + b"JPEG_PLACEHOLDER")  # Fake JPEG magic header
created.append(img)


# ------------------------------------------
# 8) Multi-page PDF (benign)
# ------------------------------------------
pdf_multi = os.path.join(OUT, "multipage_clean.pdf")
with open(pdf_multi, "wb") as f:
    f.write(b"%PDF-1.4\n% Simple multipage placeholder\n%%EOF\n")
created.append(pdf_multi)


# ------------------------------------------
# Manifest summary
# ------------------------------------------
manifest = {"benign_samples": []}
for p in created:
    manifest["benign_samples"].append({"path": p, "size": os.path.getsize(p)})

manifest_path = os.path.join(OUT, "manifest.json")
with open(manifest_path, "w") as mf:
    json.dump(manifest, mf, indent=4)

print("\nCreated benign dataset files:")
for p in created:
    print(" ✔", p)

print("\nManifest saved:", manifest_path)
print("\nRun this to scan all benign samples:")
print('for f in dataset/benign/*; do python3 -m src.cli_app "$f"; done')
