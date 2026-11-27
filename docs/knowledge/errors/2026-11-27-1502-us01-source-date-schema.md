---
date: 2026-11-27 15:02
area: databricks-pipelines
status: open
seen: 1
---

# US01 Bronze source date column changed from void to string

- Symptom: rerun failed with `DELTA_METADATA_MISMATCH` because `_source_date` was `void` and incoming data was `string`.
- Cause: the first successful load had no catalog publication date and Spark inferred a null-only column as `void`.
- Fix: add a non-null year fallback and alter the existing `_source_date` column to `string` before the partition write.
- Prevention: add fallback metadata values at the first load so source metadata columns never become `void`.
