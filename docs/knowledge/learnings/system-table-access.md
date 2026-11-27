---
status: verified
Last checked: 2026-11-27
---

# Verified system table access

Read-only discovery through `scripts/dbquery.py` confirmed the `system.billing` and `system.lakeflow` schemas.

Visible tables:

- `system.billing`: `account_prices`, `attributed_usage`, `list_prices`, `usage`
- `system.lakeflow`: `job_run_timeline`, `job_task_run_timeline`, `job_tasks`, `jobs`, `pipeline_update_timeline`, `pipelines`, `zerobus_ingest`, `zerobus_stream`

`DESCRIBE TABLE system.billing.usage` and a read-only aggregate query against that table succeeded. The query result was withheld. Availability and permissions can differ between workspaces.
