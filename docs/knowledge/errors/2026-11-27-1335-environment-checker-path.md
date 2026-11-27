---
date: 2026-11-27 13:35
area: environment-setup
status: open
seen: 1
---

# Environment checker did not find installed CLIs in a fresh shell

- Symptom: `scripts/check_environment.py` reported GitHub CLI and Databricks CLI as missing in a fresh PowerShell process.
- Cause: the process PATH did not include their WinGet installation directories.
- Fix: none yet; rerun the checker with the installed command directories added to PATH.
- Prevention: `skills/core/environment-setup/SKILL.md` should require checking command resolution in the same shell used for the verification script.
