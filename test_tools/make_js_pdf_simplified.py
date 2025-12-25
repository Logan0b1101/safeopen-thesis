from PyPDF2 import PdfWriter
from PyPDF2.generic import (
    NameObject,
    DictionaryObject,
    TextStringObject
)

output_path = "dataset/malicious/js_embedded_simplified.pdf"

writer = PdfWriter()
writer.add_blank_page(595, 842)

js_code = "app.alert('SafeOpen Test: Simplified JS executed');"

# Create JS action
js_action = DictionaryObject()
js_action.update({
    NameObject("/S"): NameObject("/JavaScript"),
    NameObject("/JS"): TextStringObject(js_code)
})

# Add as an Additional Action
writer._root_object.update({
    NameObject("/AA"): DictionaryObject({
        NameObject("/O"): js_action    # "O" = OpenAction in AA dictionary
    })
})

with open(output_path, "wb") as f:
    writer.write(f)

print("[+] Created simplified JS PDF →", output_path)
