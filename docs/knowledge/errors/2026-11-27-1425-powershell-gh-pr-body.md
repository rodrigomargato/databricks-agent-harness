---
date: 2026-11-27 14:25
area: github-pr-flow
status: fixed-in-learnings
seen: 1
---

# PowerShell rejected an inline gh PR body here-string

- Symptom: `gh pr create --body $body` failed with "No characters are allowed after a here-string header".
- Cause: the multiline PowerShell string used inline quoting that was parsed by the shell as a here-string header.
- Fix: write the PR body to a temporary Markdown file and pass `--body-file <path>`.
- Prevention: use `gh pr create --body-file` for PRs with multiline Markdown bodies on Windows.
