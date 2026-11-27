# Error log

Do not store secrets or personal data here.

## 2026-11-27 11:04 · publish_backlog could not find gh.exe on Windows · open · seen 4
- Symptom: `publish_backlog.py --apply` stopped with `WinError 2: The system cannot find the file specified`.
- Cause: a fresh PowerShell process did not include `C:\Program Files\GitHub CLI` in PATH after WinGet installation.
- Fix: repeat the command with the GitHub CLI directory prepended explicitly to PATH.
- Prevention: environment setup verification should open a new terminal or add the WinGet CLI directory before invoking Python scripts that call `gh`.
- Seen again: 2026-11-27 11:20, board status verification in a fresh PowerShell process could not find `gh.exe`.
- Seen again: 2026-11-27 14:12, fresh PowerShell processes could not find `gh.exe`; prepending `C:\Program Files\GitHub CLI` fixed the lookup.
- Seen again: 2026-11-27 15:31, starting US02 could not find `gh` in the fresh PowerShell PATH; issue details were read from the GitHub API instead.
- Seen again: 2026-11-27 15:39, the harness was requested to consolidate error files into this log.

## 2026-11-27 13:55 · PowerShell split a GitHub CLI jq expression into multiple arguments · open · seen 1
- Symptom: `gh api ... --jq` returned `accepts 1 arg(s), received 3` when the filter used embedded double quotes.
- Cause: PowerShell argument quoting split the jq expression before it reached GitHub CLI.
- Fix: none; no retry was needed because PR merge and board Done status were independently verified.
- Prevention: use PowerShell single-quoted jq expressions or capture API JSON and filter it in PowerShell.
