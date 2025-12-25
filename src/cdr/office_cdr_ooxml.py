import zipfile
import shutil
import os
import tempfile

def sanitize_ooxml(path: str):
    """
    Remove macros and scripts from Office OOXML (ZIP) documents.
    Produces sanitized copy next to original file.
    """

    try:
        with zipfile.ZipFile(path, "r") as z:
            namelist = z.namelist()

            # Reject malformed OOXML
            if "[Content_Types].xml" not in namelist:
                return False, "Invalid OOXML structure"

        # Extract to temp dir
        temp_dir = tempfile.mkdtemp()

        with zipfile.ZipFile(path, "r") as zin:
            zin.extractall(temp_dir)

        # Delete macro storage
        for root, dirs, files in os.walk(temp_dir):
            for f in files:
                if f.lower().endswith("vba") or "vba" in f.lower():
                    os.remove(os.path.join(root, f))

        # Save sanitized
        sanitized = path + ".sanitized.docx"
        shutil.make_archive(sanitized.replace(".docx", ""), "zip", temp_dir)
        os.rename(sanitized.replace(".docx", "") + ".zip", sanitized)

        return True, f"OOXML sanitized → {sanitized}"

    except Exception as e:
        return False, f"OOXML sanitization error: {e}"
