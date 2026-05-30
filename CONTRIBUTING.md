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

## License

By contributing, you agree that your contributions are licensed under the
[MIT License](LICENSE).
