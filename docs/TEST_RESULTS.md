# Local test results

Date: 2026-11-02. Python 3.12.14 (bundled runtime; see actual local validation output for runtime details). Command: `python -m unittest discover -s tests -v`.

8 tests passed (0.078 seconds). Coverage: latest-date ties, invalid and absent dates, atomic checkpoint replacement, modified/unverified cache rejection, cache path escape rejection, HTML disguised as PDF rejection, blank PDF remaining NEEDS_REVIEW.

No live CDE/enterprise/Firecrawl requests were made by these tests. No end-to-end batch processing is proven. No remote CI execution is claimed. An initial sandbox run stalled on temporary-file handling; the completed run used a task-local temporary directory.

## Rule update regression
2026-11-02: 11 offline tests passed (0.033s), including albumin-bound query expansion, liposomal query preservation, and generic-only selection coverage. Live regression evidence is private task data and is intentionally excluded.

## Chinese source policy update — 2026-11-02

Run `python -m unittest discover -s tests -v` with a writable task-local TEMP/TMP on Windows. The first run stalled in existing temporary-directory handling and was interrupted; rerun completed. Full suite result and duration below are updated from the actual final run.

Final result: **27 tests passed in 0.094 seconds**, Python 3.12.14. The bundled Skill Creator `quick_validate.py` could not start because PyYAML is absent (`ModuleNotFoundError: yaml`); this is not reported as a passed validator. Frontmatter and relative references were checked separately. No dependencies were installed for this change.

New behavioral coverage: unknown CDN discovery retention; downloaded files with UNKNOWN provenance; manual review of unresolved provenance; Chinese versus English/Japanese bodies; strict formulation/salt/route/combination matching; restricted/paid source exclusion; access/use permission separate from free availability; official claims require evidence; redistribution permission separate from adoption; explicit third-party admission policy; excluded databases and known mirror origins; invalid files and rejected content; broad queries without domain allowlists; unknown language review; invalid enum rejection; PDF metadata does not certify source.

Original CDE-related date selection (including ties), query expansion, hash/cache safety and atomic checkpoint tests remain in the full suite. These are offline policy regressions, not live CDE integration, automated provenance tracing, copyright authentication, or GitHub-upload tests. No network or upload is performed by the suite or new policy module.
