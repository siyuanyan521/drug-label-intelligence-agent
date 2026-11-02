"""Small offline helpers. Product identity requires external evidence."""
import hashlib
import json
import os
import tempfile
from datetime import date
from pathlib import Path

def latest_record(records):
    """Select latest dated record AFTER the caller verifies product identity.

    Never use acceptance dates as label revision or approval dates.
    """
    if not records:
        raise ValueError("No matched records")
    def key(row):
        return date.fromisoformat(row["acceptance_date"])
    newest = max(key(row) for row in records)
    return [row for row in records if key(row) == newest]

def sha256_file(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()

def verified_cache(record, root):
    """Do not reuse partial, replaced, or out-of-root downloads."""
    if record.get("verification") != "VERIFIED":
        return False
    root = Path(root).resolve()
    path = (root / record["file"]).resolve()
    if not path.is_relative_to(root) or not path.is_file():
        return False
    return sha256_file(path) == record.get("sha256")

def save_checkpoint(path, value):
    """Atomic checkpoint replacement; callers must exclude task data from Git."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(dir=path.parent, suffix=".tmp")
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as stream:
            json.dump(value, stream, ensure_ascii=False, indent=2)
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def search_terms(name):
    """Generate recall terms only; never change the target dosage form."""
    import re
    normalized = re.sub(r"\s+", "", name).replace("(", "（").replace(")", "）")
    terms = [name]
    if normalized != name:
        terms.append(normalized)
    if "紫杉醇" in normalized and "白蛋白" in normalized:
        terms.extend(["注射用紫杉醇（白蛋白结合型）", "紫杉醇"])
    elif "伊立替康" in normalized and "脂质体" in normalized:
        terms.append("伊立替康")
    return list(dict.fromkeys(terms))
