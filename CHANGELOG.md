# Changelog

All notable changes to this project are documented here. The format is based
on [Keep a Changelog](https://keepachangelog.com/), and this project adheres
to semantic versioning where practical.

## [Unreleased]

### Added
- **Launch-readiness pass:** rewritten README first screen (working hero visual,
  quickstart, "why this vs alternatives" table), `assets/hero.svg` +
  `assets/demo.cast` terminal demo, GitHub Actions CI (`/.github/workflows/ci.yml`)
  with a status badge, issue/PR templates, `CITATION.cff`, two new runnable example
  skills (`weekly-crm-report`, `pr-blocker-summarizer`), and a launch kit
  (`LAUNCH.md` + `docs/launch/`). Corrected the platform count to the real **17**
  (was overstated as "20+") throughout the README.
- End-to-end eval **rollout harness**: `run_evals.py --rollout` runs a skill's
  declared `run` command on each golden input and scores the real output through
  the existing command checks (closing the "does not run the skill itself" gap).
  `--promote` captures the first passing output as the `pending-first-green`
  baseline; `--timeout` bounds each run. The bundled `stock-analyzer` example now
  ships a real eval spec + `run_pipeline.py` so the harness is integration-tested.
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
