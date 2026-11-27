---
date: 2026-11-27 14:43
area: databricks-free-edition
status: open
seen: 1
---

# US01 serverless job rejected task libraries

- Symptom: deployment returned `Libraries field is not supported for serverless task, please specify libraries in environment`.
- Cause: `openpyxl` was configured under task `libraries`, while the serverless API requires job environments.
- Fix: move `openpyxl` to `environments[].spec.dependencies` and set `environment_key` on the task.
- Prevention: use serverless environment syntax for Pypi dependencies in Databricks jobs.
