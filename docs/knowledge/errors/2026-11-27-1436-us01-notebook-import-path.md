---
date: 2026-11-27 14:36
area: databricks-pipelines
status: open
seen: 1
---

# US01 Databricks notebook could not import src module

- Symptom: the serverless US01 run failed with `ModuleNotFoundError: No module named 'src'`.
- Cause: the deployed notebook resolved `/Workspace` rather than its DAB bundle files directory.
- Fix: derive the bundle root from the notebook context and insert it into `sys.path` before importing `src.us01_ingest`.
- Prevention: test notebook import paths in the deployed bundle before running the source ingestion.
