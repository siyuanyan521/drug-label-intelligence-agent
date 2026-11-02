# Publication review

Scope: only this isolated repository, not the source workspace or the user's computer. Prepared 2026-11-02.

Reviewed original skill and local experiment scripts. Experiment runners contain machine-specific paths, real drug tasks, unstable session assumptions and raw response handling; they are excluded, not copied. Only the user-authored reusable skill and a technical-reference summary are retained. New Python helpers are written for this repository. No third-party package/skill implementation is vendored.

Examples are invented, including drug/company identities and reserved example.org URLs. No source SOC workbook, company internal document, downloaded PDF, proprietary code, cookie, browser profile, session token, API credential, HAR or task log is included. No evidence of third-party proprietary code in the selected files was found; automated scanning cannot establish complete legal clearance or prove the absence of all secrets.

Text scan: no local Windows user paths, token-shaped keys, private-key blocks or email addresses found in selected files. Ignore rules exclude real datasets, PDFs, spreadsheets, environment files and browser artifacts. A final staged-file scan is required before push.

License: none selected; no third-party label redistribution authorized. User confirmation required before remote publication. Existing remote README is replaced with more precise prototype claims; existing commit history is retained.

## Reviewed files (before this review file)
- `.github/workflows/tests.yml`
- `.gitignore`
- `docs/TEST_RESULTS.md`
- `examples/input.synthetic.json`
- `examples/output.synthetic.json`
- `pyproject.toml`
- `README.md`
- `README.zh-CN.md`
- `requirements.txt`
- `scripts/inspect_pdf.py`
- `skills/drug-insert-retrieval/references/cde.md`
- `skills/drug-insert-retrieval/SKILL.md`
- `src/drug_label_agent/__init__.py`
- `src/drug_label_agent/provenance.py`
- `tests/test_core.py`
