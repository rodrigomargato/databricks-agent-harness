---
date: 2026-11-27 14:12
area: test-environment
status: open
seen: 1
---

# Python test runner is missing from the active interpreter

- Symptom: `python -m pytest tests/test_us01_ingest.py -q` returned `No module named pytest`.
- Cause: the active Python 3.12 environment does not have the repository's dev dependencies installed.
- Fix: none yet; restore dependencies with `python -m pip install -r requirements-dev.txt`.
- Prevention: setup verification should confirm pytest and the dev requirements before starting tests.
