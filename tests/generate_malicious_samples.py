import os
import zipfile
import json

# -----------------------------
# Output directory
# -----------------------------
ROOT = os.path.expanduser("~/thesis/~safeopen")
OUT = os.path.join(ROOT, "dataset", "malicious")
os.makedirs(OUT, exist_ok=True)

created = []


# -----------------------------
# 1) PDF with embedded JavaScript-like content
# -----------------------------
pdf_js = os.path.join(OUT, "js_embedded.pdf")
with open(pdf_js, "wb") as f:
    f.write(b"%PDF-1.4\n")
    f.write(b"1 0 obj << /Type /Catalog /OpenAction 2 0 R >> endobj\n")
    f.write(b"2 0 obj << /S /JavaScript /JS (app.alert('SafeOpen test: harmless JS')) >> endobj\n")
    f.write(b"%%EOF\n")
created.append(pdf_js)


# -----------------------------
# 2) DOCM-like file containing macro text (NOT real macro)
# -----------------------------
docm = os.path.join(OUT, "macro_test.docm")
with open(docm, "w", encoding="utf-8") as f:
    f.write("This is a synthetic DOCM container for testing.\n")
    f.write("-----BEGIN-MACRO-----\n")
    f.write("Sub AutoOpen()\n    MsgBox \"SafeOpen test macro (harmless)\"\nEnd Sub\n")
    f.write("-----END-MACRO-----\n")
created.append(docm)


# -----------------------------
# 3) MIME mismatch — content is PDF but extension is JPG
# -----------------------------
mime_mismatch = os.path.join(OUT, "mismatched_pdf_as_jpg.jpg")
with open(mime_mismatch, "wb") as f:
    f.write(b"%PDF-1.5\n% This file is actually a PDF but named .jpg\n%%EOF\n")
created.append(mime_mismatch)


# -----------------------------
# 4) Fake phishing invoice PDF (actually plain text)
# -----------------------------
phish = os.path.join(OUT, "phishing_invoice.pdf")
with open(phish, "w", encoding="utf-8") as f:
    f.write("ACME Corp\nINVOICE\n\n")
    f.write("Pay at: http://malicious.example.com/login\n")
    f.write("Amount Due: $9999\n")
created.append(phish)


# -----------------------------
# 5) ZIP file with suspicious embedded script
# -----------------------------
zip_path = os.path.join(OUT, "suspicious_nested.zip")
with zipfile.ZipFile(zip_path, "w") as zf:
    zf.writestr("README.txt", "This is a test archive. Contains nested payload.\n")
    zf.writestr("payload.js", "/* harmless js-like file */\napp.alert('safeopen test');\n")
created.append(zip_path)


# -----------------------------
# 6) OpenAction-triggered PDF (fake JavaScript action)
# -----------------------------
pdf_open = os.path.join(OUT, "openaction_trigger.pdf")
with open(pdf_open, "wb") as f:
    f.write(b"%PDF-1.7\n")
    f.write(b"1 0 obj << /Type /Catalog /OpenAction << /S /JavaScript /JS (app.alert('OpenAction executed')) >> >> endobj\n")
    f.write(b"%%EOF\n")
created.append(pdf_open)


# -----------------------------
# 7) Polyglot PDF-ZIP hybrid file
# -----------------------------
poly = os.path.join(OUT, "polyglot_pdf_zip.pdf")

# Write fake PDF header
with open(poly, "wb") as f:
    f.write(b"%PDF-1.4\n%Polyglot start\n%%EOF\n")

# Append ZIP structure (ZIP will follow PDF, forming polyglot)
with open(poly, "ab") as f:
    with zipfile.ZipFile(f, mode="w", compression=zipfile.ZIP_DEFLATED) as z:
        z.writestr("dummy.txt", "Polyglot dummy content.\n")

created.append(poly)


# -----------------------------
# 8) Plain text file with .pdf extension
# -----------------------------
txt_pdf = os.path.join(OUT, "text_as_pdf.pdf")
with open(txt_pdf, "w", encoding="utf-8") as f:
    f.write("Just a plain text file saved with .pdf extension.\n")
created.append(txt_pdf)


# -----------------------------
# Write manifest summary
# -----------------------------
manifest = {"samples": []}
for p in created:
    manifest["samples"].append({"path": p, "size": os.path.getsize(p)})

manifest_path = os.path.join(OUT, "manifest.json")
with open(manifest_path, "w") as mf:
    json.dump(manifest, mf, indent=4)


# -----------------------------
# Print summary
# -----------------------------
print("\nCreated synthetic malicious-like files:")
for p in created:
    print(" ✔", p)

print("\nManifest saved:", manifest_path)

print("\nRun this to test all samples:")
print('for f in dataset/malicious/*; do python3 -m src.cli_app "$f"; done')
