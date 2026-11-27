Status: verified

Last checked: 2026-11-27

# Windows GitHub PR body

For multiline pull request bodies, write the Markdown to a temporary file and use
`gh pr create --body-file <path>` instead of inline shell quoting. This avoids
PowerShell parsing embedded newlines and special characters incorrectly.
