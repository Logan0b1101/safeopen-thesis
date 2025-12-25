# src/cdr/office_cdr.py
"""
Office CDR (Content Disarm & Reconstruction) module.

Goal:
 - Remove macros (vbaProject.bin) from macro-enabled Office files.
 - Remove external relationships (TargetMode="External" and http(s) targets)
 - Remove ActiveX/controls entries if detected.
 - Repack sanitized file into safe_outputs/sanitized_<originalname>.docx (or .pptx/.xlsx).

Usage:
    from src.cdr.office_cdr import sanitize_office
    ok, msg = sanitize_office("/path/to/file.docm")
"""

import os
import zipfile
import shutil
import tempfile
from pathlib import Path
import xml.etree.ElementTree as ET

# XML namespace mapping helpers
NS = {
    'rels': 'http://schemas.openxmlformats.org/package/2006/relationships',
    'ct': 'http://schemas.openxmlformats.org/package/2006/content-types'
}
for prefix, uri in NS.items():
    ET.register_namespace(prefix, uri)

SAFE_OUTPUT_DIR = Path.cwd() / "safe_outputs"
SAFE_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def _is_office_file(path: Path):
    ext = path.suffix.lower()
    return ext in {'.docx', '.docm', '.pptx', '.pptm', '.xlsx', '.xlsm'}


def _should_strip_rel_target(target):
    if not target:
        return False
    t = target.lower()
    if t.startswith("http://") or t.startswith("https://"):
        return True
    return False


def sanitize_office(input_path: str):
    """
    Main entry - sanitizes an Office file.
    Returns (success: bool, message: str)
    """

    p = Path(input_path)
    if not p.exists():
        return False, f"File not found: {input_path}"
    if not _is_office_file(p):
        return False, f"Not an Office file (docx/docm/pptx/pptm/xlsx/xlsm): {p.suffix}"

    try:
        # Work in a temp dir
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)
            # Extract zip contents
            with zipfile.ZipFile(p, 'r') as zin:
                zin.extractall(tmpdir)

            # Remove macro binary if present (word/vbaProject.bin, xl/vbaProject.bin, ppt/vbaProject.bin)
            removed_items = []
            for macro_path in [
                tmpdir / "word" / "vbaProject.bin",
                tmpdir / "xl" / "vbaProject.bin",
                tmpdir / "ppt" / "vbaProject.bin",
            ]:
                if macro_path.exists():
                    macro_path.unlink()
                    removed_items.append(str(macro_path.relative_to(tmpdir)))

            # Remove activeX and controls (best-effort)
            # Example dirs: word/activeX, word/controls
            for folder in ["word/activeX", "word/controls", "xl/activeX", "xl/controls", "ppt/activeX", "ppt/controls"]:
                d = tmpdir / folder
                if d.exists() and d.is_dir():
                    shutil.rmtree(d)
                    removed_items.append(folder + "/* (dir removed)")

            # Sanitize all .rels files under tmpdir by removing External TargetMode or HTTP targets
            rels_paths = list(tmpdir.rglob("*.rels"))
            rels_removed = []
            for rels_file in rels_paths:
                try:
                    tree = ET.parse(rels_file)
                    root = tree.getroot()
                    # relationships are in the default namespace
                    to_remove = []
                    for rel in list(root):
                        # attributes: Id, Type, Target, TargetMode (optional)
                        target = rel.get('Target')
                        target_mode = rel.get('TargetMode')
                        if target_mode and target_mode.lower() == 'external':
                            to_remove.append(rel)
                        elif _should_strip_rel_target(target):
                            to_remove.append(rel)
                    if to_remove:
                        for r in to_remove:
                            root.remove(r)
                        tree.write(rels_file, xml_declaration=True, encoding='utf-8')
                        rels_removed.append(str(rels_file.relative_to(tmpdir)))
                except ET.ParseError:
                    # if parsing fails, skip but warn by listing the file
                    rels_removed.append(str(rels_file.relative_to(tmpdir)) + " (parse failed)")

            # Also sanitize [Content_Types].xml to remove references to VBA or ActiveX if present (best-effort)
            ct_file = tmpdir / "[Content_Types].xml"
            ct_removed = []
            if ct_file.exists():
                try:
                    ct_tree = ET.parse(ct_file)
                    ct_root = ct_tree.getroot()
                    # remove any Override elements with ContentType pointing to vbaProject or activeX
                    for override in list(ct_root.findall('{http://schemas.openxmlformats.org/package/2006/content-types}Override')):
                        ct = override.get('ContentType', '').lower()
                        if 'vba' in ct or 'activex' in ct or 'vbaProject' in ct:
                            ct_root.remove(override)
                            ct_removed.append(str(override.get('PartName')))
                    if ct_removed:
                        ct_tree.write(ct_file, xml_declaration=True, encoding='utf-8')
                except ET.ParseError:
                    pass

            # Ensure no residual references to vbaProject.bin remain in any XML by a simple textual cleanup (best-effort)
            for xml_file in tmpdir.rglob("*.xml"):
                try:
                    txt = xml_file.read_text(encoding='utf-8', errors='ignore')
                    if 'vbaProject.bin' in txt or 'activeX' in txt or 'oleObject' in txt:
                        newtxt = txt.replace('vbaProject.bin', '')
                        newtxt = newtxt.replace('activeX', '')
                        newtxt = newtxt.replace('oleObject', '')
                        xml_file.write_text(newtxt, encoding='utf-8')
                except Exception:
                    # skip unreadable files
                    continue

            # Build sanitized output filename and extension:
            # If input was macro-enabled (.docm/.pptm/.xlsm) produce sanitized .docx/.pptx/.xlsx
            out_suffix = p.suffix.lower()
            if out_suffix == '.docm':
                out_suffix = '.docx'
            elif out_suffix == '.pptm':
                out_suffix = '.pptx'
            elif out_suffix == '.xlsm':
                out_suffix = '.xlsx'

            sanitized_name = f"sanitized_{p.stem}{out_suffix}"
            out_path = SAFE_OUTPUT_DIR / sanitized_name

            # Repack the temp dir into a new zip (Office Open XML)
            with zipfile.ZipFile(out_path, 'w', zipfile.ZIP_DEFLATED) as zout:
                for root, dirs, files in os.walk(tmpdir):
                    for file in files:
                        file_path = Path(root) / file
                        # compute archive name relative to tmpdir
                        arcname = str(file_path.relative_to(tmpdir)).replace(os.path.sep, '/')
                        # avoid writing back removed macros (should already be removed)
                        if 'vbaProject.bin' in arcname:
                            continue
                        zout.write(file_path, arcname)

            # Success message summarizing what was removed
            summary_parts = []
            if removed_items:
                summary_parts.append(f"Removed macros: {', '.join(removed_items)}")
            if rels_removed:
                summary_parts.append(f"Sanitized rels: {', '.join(rels_removed)}")
            if ct_removed:
                summary_parts.append(f"Cleaned content types: {', '.join(ct_removed)}")
            if not summary_parts:
                summary = "No macros/external relationships found; file repackaged."
            else:
                summary = "; ".join(summary_parts)

            return True, f"Sanitized file written to: {out_path}. {summary}"

    except Exception as e:
        return False, f"Exception during sanitization: {e}"
