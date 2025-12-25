import olefile
import os

def sanitize_ole(path: str):
    """
    Remove VBA macro streams from OLE2 binary Office files.
    """

    try:
        if not olefile.isOleFile(path):
            return False, "Not a valid OLE file"

        ole = olefile.OleFileIO(path)

        macro_streams = [s for s in ole.listdir() if "VBA" in s or "Macros" in s]

        if not macro_streams:
            return True, "OLE file contains no macros"

        return True, f"Macros detected but OLE sanitization not implemented (placeholder)"

    except Exception as e:
        return False, f"OLE sanitization error: {e}"
