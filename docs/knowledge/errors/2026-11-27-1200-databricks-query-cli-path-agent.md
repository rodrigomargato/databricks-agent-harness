---
date: 2026-11-27 12:00
area: databricks-sql-query
status: open
seen: 1
---

# Read-only query agent could not find Databricks CLI

- Symptom: `scripts/dbquery.py` exited with `Databricks CLI not found. See skill environment-setup.`
- Cause: the delegated agent's shell did not have the WinGet-installed Databricks CLI directory on PATH.
- Fix: none yet; retry with the known installed CLI directory added to PATH in the agent's execution environment.
- Prevention: `skills/databricks/databricks-sql-query/SKILL.md` should describe how to run the read-only wrapper when WinGet CLI installation is not in the agent shell PATH.
