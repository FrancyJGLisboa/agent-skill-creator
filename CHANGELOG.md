# Changelog

All notable changes to this project are documented here. The format is based
on [Keep a Changelog](https://keepachangelog.com/), and this project adheres
to semantic versioning where practical.

## [Unreleased]

### Added
- `LICENSE` (MIT), `CONTRIBUTING.md`, and this `CHANGELOG.md`.
- Windows installers tracked in version control (`install.ps1`,
  `scripts/bootstrap.ps1`, `scripts/bootstrap.bat`, `scripts/install-skill.ps1`,
  `scripts/install-template.ps1`), with `test_install_parity.py` gating
  bash/PowerShell parity.
- Phase 5 harness patterns: every generated skill gets input validation,
  `--check-prereqs`, `--diagnostics`, self-bootstrapping wrappers, and
  `activation`/`provenance` frontmatter checks in `validate.py`.

### Changed
- Consolidated SKILL.md parsing into `scripts/skill_document.py` and the
  install-target registry into `scripts/platforms.py`.
- Bumped `architecture-guide.md` and `export-guide.md` headers to v6.0.

### Removed
- Marketing collateral (`Dynamous/`) and a one-off research dump
  (`agentic-tool-skill-systems/`).

## [6.0.0]

- Five-phase generation pipeline (discovery, design, architecture, detection,
  implementation) documented in `references/pipeline-phases.md`.
- Cross-platform export across 17 agent platforms.
- Per-skill eval specs (`evals/*.eval.md` + `scripts/run_evals.py`).
- Deterministic pipeline orchestration (`run_pipeline.py`) for multi-script
  skills.
