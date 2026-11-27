---
date: 2026-11-27 11:18
area: databricks-official-skills
status: open
seen: 1
---

# GitHub Copilot rejects project-scoped Databricks skills

- Symptom: `databricks aitools install --scope project --agents copilot --skills-only --skills databricks-core,databricks-pipelines,databricks-dabs --profile free` failed with "GitHub Copilot: does not support project-scoped skills".
- Cause: the Databricks CLI 1.28.0 reports that GitHub Copilot supports skills only at global scope.
- Fix: none within the approved scope; do not install globally unless the user gives separate approval.
- Prevention: `skills/databricks/databricks-official-skills/SKILL.md` should note the Copilot project-scope limitation before setup commands.
