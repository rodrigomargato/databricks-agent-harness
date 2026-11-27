---
date: 2026-11-27 14:45
area: databricks-free-edition
status: open
seen: 1
---

# US01 serverless job rejected Client-1 environment

- Symptom: the run failed with `Workspace doesn't support Client-1 channel for REPL`.
- Cause: the custom serverless environment selected by `environment_version: "1"` uses an unsupported channel in this Free Edition workspace.
- Fix: remove the custom environment and use the workspace serverless default, where `openpyxl` was already importable.
- Prevention: test custom serverless environments before deploying and avoid them when the default is sufficient.
