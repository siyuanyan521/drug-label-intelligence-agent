# Drug Label Intelligence Agent

[中文说明](README.zh-CN.md)

An agent-guided workflow for locating drug prescribing information with explicit source provenance, manufacturer roles, and original/generic product classification. This repository contains a reusable Codex skill and small offline utilities, not a production search service.

## Retrieval order
1. Original product labels from NMPA/CDE.
2. Original manufacturer's Chinese website; other regions' Chinese-body labels are separately identified. Foreign-language bodies are excluded by default.
3. NMPA generic labels, then manufacturer websites and other freely downloadable sources. Always identify the actual generic manufacturer.

## Architecture
Input manifest → evidence-based product matching → ordered source discovery → candidate/detail records → download → PDF and identity review → checkpoint and report.

The skill directs the agent. Playwright CLI provides real browser interaction and network inspection; optional Firecrawl provides search/scrape/map. Neither integration is bundled as an unattended Python adapter. Offline Python helpers cover date selection, hashes, safe cache reuse, atomic checkpoints, and local PDF inspection.

## Install
Python 3.10+:
```sh
python -m venv .venv
# Activate the environment using your operating system's command.
python -m pip install -e .
python -m unittest discover -s tests -v
```
Copy `skills/drug-insert-retrieval` into your Codex skill directory. Install Playwright CLI separately if browser work is needed. Firecrawl is optional and may require authentication or credits; configure credentials locally, never in this repository.

## Usage
Invoke `$drug-insert-retrieval` with a local manifest and an output folder. For example: “Retrieve labels for my manifest using the three source tiers; preserve every candidate URL and mark blocked steps.”

`examples/*.synthetic.json` are invented schema examples, not evidence of real searches. JSON is an example interchange format; spreadsheet reading/report generation is performed by the agent's available spreadsheet tools, not a shipped Python Excel pipeline.

Inspect a local file:
```sh
python scripts/inspect_pdf.py /path/to/local-label.pdf
```
This checks parsing and hashing only. A parseable file is not proof of a correct label. Scans require rendering and human review. `latest_record` accepts already-matched candidates and preserves date ties; it does not resolve company aliases or prove approval.

## Status and limitations
Historical local experiments demonstrated headed-browser CDE queries, candidate pages and selected individual downloads. Their raw task data and PDFs are intentionally excluded. These observations do not guarantee current access, coverage or reliability.

Implemented here: skill instructions, offline provenance helpers, synthetic examples, local PDF inspection and offline tests. Not implemented: stable standalone CDE API client, automatic manufacturer identity resolution, unattended end-to-end batch retrieval, production resume orchestration or automatic Excel export. CDE endpoints and dynamic parameters are not a public API contract. Browser access can fail; acceptance dates are not approval or revision dates. Professional-status prompts require a truthful user declaration and authorization.

## Data and publication boundaries
Do not commit real manifests, downloaded labels, private company material, credentials, cookies, browser sessions or network traces. An ignore file is not a security audit. Review the exact staged files before every publication. Third-party labels retain their owners' rights; this repository distributes none. See [publication review](docs/PUBLICATION_REVIEW.md) and [test results](docs/TEST_RESULTS.md).

## License
No open-source license has been selected yet. Public visibility alone does not grant reuse rights. Choose a license before inviting redistribution or contributions. No third-party skill package or CLI source is vendored.


## Chinese candidate discovery and adoption

Priority ranks retrieval and adoption; it is not a domain allowlist. After priority sources fail to yield a qualifying Chinese label, broaden searches by generic name, brand, holder and approval number. Unknown public CDN PDFs remain candidates. Review access/use terms before fetching; never bypass paywalls, memberships, excluded databases (including DXY), or their mirrors.

Track `file_status`, `content_status`, `source_status`, `access_status` and `redistribution_status` independently. A downloaded complete Chinese label may still have UNKNOWN provenance and require manual review. An English-body file is rejected for language, not queued for uncertain provenance. Free access does not establish redistribution rights. Default final adoption requires verified content/product identity, allowed access/use and evidenced official/institutional provenance. Third-party adoption requires an explicit project policy; UNKNOWN is never automatically adopted or published.

The offline [source policy module](src/drug_label_agent/source_policy.py) constructs broad/trace queries and evaluates recorded evidence; it does not perform live provenance tracing or authenticate evidence. Local PDF inspection now exposes metadata and identity hints without certifying them. See the [source strategy](skills/drug-insert-retrieval/references/source-policy.md) and [test report](docs/TEST_RESULTS.md). No code automatically uploads PDFs to GitHub, including candidates with unknown sources. CDE latest-date selection, query expansion and task-scoped professional authorization remain in place.
