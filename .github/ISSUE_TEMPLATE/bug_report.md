---
name: Bug report
about: Something the creator or a generated skill did wrong
title: "[bug] "
labels: bug
---

**What happened**
A clear description of the bug.

**What you ran**
The exact `/agent-skill-creator …` prompt or command, and the tool you ran it in
(Claude Code, Cursor, Gemini CLI, …).

**Expected vs. actual**
What you expected to happen, and what actually happened (paste output / errors).

**Environment**
- OS:
- Tool + version:
- Python version (`python3 --version`):
- agent-skill-creator version / commit:

**If a generated skill is involved**
- Output of `python3 scripts/validate.py <skill>/`
- Output of `python3 scripts/check_pipeline.py <skill>/`
