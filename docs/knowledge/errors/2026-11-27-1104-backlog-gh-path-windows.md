---
date: 2026-11-27 11:04
area: github-setup
status: open
seen: 3
---

# publish_backlog could not find gh.exe on Windows

- Symptom: `publish_backlog.py --apply` stopped with `WinError 2: The system cannot find the file specified`.
- Cause: a fresh PowerShell process did not include `C:\Program Files\GitHub CLI` in PATH after WinGet installation.
- Fix: repeat the command with the GitHub CLI directory prepended explicitly to PATH.
- Prevention: environment setup verification should open a new terminal or add the WinGet CLI directory before invoking Python scripts that call `gh`.
- Seen again: 2026-11-27 11:20, board status verification in a fresh PowerShell process could not find `gh.exe`.
- Seen again: 2026-11-27 14:12, fresh PowerShell processes could not find `gh.exe`; prepending `C:\Program Files\GitHub CLI` fixed the lookup.
