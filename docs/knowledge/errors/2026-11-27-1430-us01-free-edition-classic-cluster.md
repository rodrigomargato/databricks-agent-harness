---
date: 2026-11-27 14:30
area: databricks-free-edition
status: open
seen: 1
---

# US01 job deployment rejected classic cluster configuration

- Symptom: `databricks bundle deploy -t dev` rejected `us01_bronze_contracts` with `Only serverless compute is supported in the workspace`.
- Cause: the initial job resource requested a classic `new_cluster`; Databricks Free Edition allows serverless compute only.
- Fix: remove `new_cluster` from the US01 job and use serverless task compute.
- Prevention: validate and test every Databricks job resource against the Free Edition serverless-only rule before deployment.
