<!-- Thanks for contributing! Keep changes surgical and tests green. -->

**What & why**
What does this change and why? Link any issue (`Closes #…`).

**Type**
- [ ] fix
- [ ] feat
- [ ] refactor
- [ ] docs
- [ ] test / chore

**Checks**
- [ ] `uv run pytest scripts/tests/` is green
- [ ] If I touched an install script, I updated its bash/PowerShell counterpart
      (`test_install_parity.py` still passes)
- [ ] If I touched the pipeline/validators, I updated the relevant `references/` docs
- [ ] No secrets, no placeholder/stub code in anything that ships
