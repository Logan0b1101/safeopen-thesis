# test_tools/js_pdf.py
from pikepdf import Pdf
import os

# make sure the tests folder exists
os.makedirs("../tests", exist_ok=True)
outpath = "../tests/js_test.pdf"

# create a new blank PDF
pdf = Pdf.new()
pdf.add_blank_page(page_size=(595, 842))  # A4 page

# embed harmless JavaScript (document open alert)
js_code = 'app.alert("SafeOpen test: harmless embedded JavaScript executed.");'
js_dict = {
    "/S": "/JavaScript",
    "/JS": f"({js_code})"
}

# attach to document as OpenAction
pdf.Root["/OpenAction"] = js_dict

# save the PDF
pdf.save(outpath)
pdf.close()

print(f"✅ Created JS test PDF at: {os.path.abspath(outpath)}")
