# Contributing

Thanks for your interest in improving **agent-skill-creator**. This skill
generates cross-platform agent skills, so changes need to keep the generator
correct and its tests green.

## Workflow

1. Fork the repository and create a feature branch.
2. Make your changes.
3. Add or update tests under `scripts/tests/`.
4. Run the checks below — they must pass.
5. Open a pull request describing what changed and why.

## Local checks

The tooling is stdlib-only Python; tests run with `pytest`.

```bash
# Run the full test suite (must be green)
uv run pytest scripts/tests/

# Validate a skill's SKILL.md against the spec
python3 scripts/validate.py <skill-dir>

# Verify a skill's script pipeline (compiles, deps declared)
python3 scripts/check_pipeline.py <skill-dir>

# Security scan
python3 scripts/security_scan.py <skill-dir>
```

## Conventions

- **Commits:** conventional commits (`feat:`, `fix:`, `refactor:`, `docs:`,
  `test:`, `chore:`).
- **Style:** PEP 8, type annotations on function signatures, `ruff` clean.
- **Cross-platform parity:** the install scripts ship as bash/PowerShell pairs.
  When you touch one (`install-skill.sh`, `bootstrap.sh`, `install-template.sh`,
  `install.sh`), update its `.ps1`/`.bat` counterpart so
  `scripts/tests/test_install_parity.py` stays green.
- **Single source of truth:** SKILL.md parsing lives in `scripts/skill_document.py`
  and the install-target list in `scripts/platforms.py` — extend those rather than
  re-implementing parsing or hardcoding platform paths.

## Adding a new platform

The most common contribution. A platform addition touches a fixed set of
files — change them together or CI's parity tests will catch the drift:

1. **`scripts/platforms.py`** — add the platform tuple (name, user-level
   install path, project-level install path, detection directory). This is
   the single source of truth the registry and installers read.
2. **`install.sh` and `install.ps1`** — add the detection/install branch to
   both (bash and PowerShell must stay in lockstep).
3. **`scripts/install-template.sh` and `scripts/install-template.ps1`** —
   the installer template bundled into generated skills; mirror the same
   branch there.
4. **Docs** — add the platform to the tier table in `SKILL.md` and
   `references/cross-platform-guide.md`. If the platform needs a format
   adapter (not native SKILL.md), document the transformation in the Tier 2
   section.
5. **Platform count** — the number of supported platforms is stated in
   `README.md`, `SKILL.md`, and `references/cross-platform-guide.md`. Bump
   it in **all three** in the same PR (and remind a maintainer to update the
   GitHub repo description).

Then verify:

```bash
uv run pytest scripts/tests/test_platforms.py scripts/tests/test_install_parity.py
```

`test_platforms.py` cross-checks `platforms.py` against the shell installers,
so a partial addition fails loudly.

## A note on eval specs

Generated skills bundle `run_evals.py` (from `scripts/run_evals_template.py`),
which executes spec-defined command checks via the shell. Eval specs are
trusted input — only run evals from specs you or your team wrote.

## License

By contributing, you agree that your contributions are licensed under the
[MIT License](LICENSE).
