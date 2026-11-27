---
date: 2026-11-27 14:39
area: databricks-bundles
status: open
seen: 1
---

# US01 job received literal DAB parameter text

- Symptom: the US01 notebook received `{{ var.contracts_year }}` and could not convert it to an integer.
- Cause: the bundle resource used Go-template syntax instead of Databricks Asset Bundles variable interpolation.
- Fix: use `${var.<name>}` in job `base_parameters`.
- Prevention: validate parameter interpolation in the dry-run plan and one serverless execution.
