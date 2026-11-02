"""Inspect a local PDF; does not certify label identity or original manufacturer."""
import argparse
import json
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
    return {"pages": len(reader.pages), "sha256": sha256_file(path),
            "identity_status": "NEEDS_REVIEW", "has_extractable_text": bool(text.strip()),
            "note": "Empty text may indicate a scanned PDF; render for human verification."}

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("path")
    args = parser.parse_args()
    print(json.dumps(inspect(args.path), ensure_ascii=False, indent=2))
