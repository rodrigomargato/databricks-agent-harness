---
date: 2026-11-27 12:05
area: environment-setup
status: open
seen: 1
---

# Notebook agent could not run local tests because PATH was incomplete

- Symptom: the delegated Testing run reported `pytest` was not found on PATH; `ruff` was not run and `scripts/check_environment.py` exited 1 with its output suppressed.
- Cause: unknown; likely the delegated shell did not expose the repository virtual environment and installed executables.
- Fix: none; stop without changing or bypassing the delegated environment.
- Prevention: `skills/core/environment-setup/SKILL.md` should describe how to verify the project virtual environment is selected for agent-run tests.
