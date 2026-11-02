"""Inspect a local PDF; does not certify label identity or original manufacturer."""
import argparse
import json
import re
from pathlib import Path
from pypdf import PdfReader
from drug_label_agent.provenance import sha256_file

def inspect(path):
    path = Path(path)
    with path.open("rb") as stream:
        if stream.read(5) != b"%PDF-":
            raise ValueError("Not a PDF header")
    reader = PdfReader(path)
    text = "\n".join(page.extract_text() or "" for page in reader.pages)
    if not reader.pages:
        raise ValueError("PDF has no pages")
    # Evidence hints only. Scans, two-column text and split lines need visual review.
    hints = {}
    for key, label in [('generic_name', '通用名称|通用名'),
                       ('brand', '商品名称|商品名'),
                       ('company', '企业名称|公司名称')]:
        hints[key] = re.findall(r'(?:' + label + r')\s*[：:]\s*([^\n]{1,160})', text)
    hints['approval_numbers'] = sorted(set(re.findall(
        r'国药准字\s*[A-Z]{1,2}\s*\d{8}', text)))
    return {"pages": len(reader.pages), "sha256": sha256_file(path),
            "file_status": "DOWNLOADED", "content_status": "NEEDS_REVIEW",
            "source_status": "UNKNOWN", "access_status": "UNKNOWN",
            "redistribution_status": "UNKNOWN",
            "metadata": {str(k): str(v) for k, v in (reader.metadata or {}).items()},
            "identity_hints": hints,
            "identity_status": "NEEDS_REVIEW", "has_extractable_text": bool(text.strip()),
            "note": "Empty text may indicate a scanned PDF; render for human verification."}

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("path")
    args = parser.parse_args()
    print(json.dumps(inspect(args.path), ensure_ascii=False, indent=2))
