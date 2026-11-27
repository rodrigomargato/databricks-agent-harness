---
date: 2026-11-27 10:50
area: github-auth
status: open
seen: 1
---

# GitHub login in the browser was not detected by the agent terminal

- Symptom: `gh auth status` reported "You are not logged into any GitHub hosts" after the user confirmed that both `gh auth login` and `gh auth refresh -s project` were completed.
- Cause: unknown; verification could not confirm whether the browser login and the agent terminal shared the same Windows user or authentication configuration.
- Fix: none yet; stop initialization before repository or board writes.
- Prevention: `skills/core/environment-setup/SKILL.md` and `skills/core/databricks-cli-auth/SKILL.md` should state explicitly that the agent must rerun verification and stop if the terminal does not detect the login, instead of accepting a browser-only confirmation.
