# Local test results

Date: 2026-11-02. Python 3.12.14 (bundled runtime; see actual local validation output for runtime details). Command: `python -m unittest discover -s tests -v`.

8 tests passed (0.078 seconds). Coverage: latest-date ties, invalid and absent dates, atomic checkpoint replacement, modified/unverified cache rejection, cache path escape rejection, HTML disguised as PDF rejection, blank PDF remaining NEEDS_REVIEW.

No live CDE/enterprise/Firecrawl requests were made by these tests. No end-to-end batch processing is proven. GitHub Actions configuration is included but has not yet run remotely. An initial sandbox run stalled on temporary-file handling; the completed run used a task-local temporary directory.
