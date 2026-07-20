# Changelog

All notable changes to this project are documented here. The format is based
on [Keep a Changelog](https://keepachangelog.com/), and this project adheres
to semantic versioning where practical.

## [Unreleased]

### Fixed
- **skill_document.py depth-blind YAML lookups**: `field()`/`has_field()` matched
  nested keys as top-level and `subfield()` matched any depth under the parent —
  so a `dependencies[].version` could shadow `metadata.version` (mislabeling
  export zips and registry entries) and a nested `license` silenced validate.py's
  missing-license warning. All four lookups are now depth-aware; blank lines no
  longer terminate a block scan. `export_utils.get_skill_version` now reads
  `metadata.version` (it only ever worked via the old bug).
- **skill_registry.py path traversal**: `metadata.author: ".."` slugged to `..`,
  letting `cmd_publish` `rmtree` the registry's entire `skills/` root. Slugs now
  strip edge dots, and publish refuses any destination that resolves outside
  `skills/` (defense in depth).
- **dependency_health.py / schema_drift.py dead status branches**: `urlopen`
  raises `HTTPError` (a `URLError` subclass) on 4xx/5xx, so every error status
  was misreported as "unreachable". `HTTPError` is now caught first and
  classified by status code.
- **export_utils.py egg-info exclusion**: `'*.egg-info'` was exact-matched, never
  globbed, so real `.egg-info/` build metadata shipped inside export zips.

### Added
- **Pinned LLM-judge harness** (`run_evals.py --rollout --judge`): grades
  `llm-judge` criteria via the Anthropic API (stdlib urllib, `ANTHROPIC_API_KEY`)
  with the judge model + temperature pinned in the spec's `judge` block. The
  judge sees only criterion + output, and a known-bad `canary` output must fail
  every judge criterion or the entire run is invalid — a judge that passes
  garbage proves nothing. Previously llm-judge checks were printed as a
  checklist and never graded anywhere.
- **Evidence artifacts**: any failed eval run appends the raw failing check
  rows to the skill's `EVOLUTION.md` (timestamped), and
  `staleness_check --record` does the same for stale/degraded findings — a
  detected failure now produces consumable evidence, not just an exit code.
- **Shipped evolve loop**: generated skills carry `scripts/evolve.py` plus the
  staleness/dependency-health/schema-drift modules, so
  `python3 scripts/evolve.py` closes detect → record → re-verify from the
  skill's own root (previously these tools lived only in the creator repo).
  The bundled examples ship it and CI runs it end-to-end.
- **Instruction-body injection scanning** in `security_scan.py`: SKILL.md and
  reference prose are now scanned for override phrases, concealment and
  exfiltration directives, hidden/bidirectional unicode, and encoded blobs —
  skill-file prompt injection fires at load time, before any code runs, and the
  old scanner missed that class entirely. Plus a least-privilege cross-check:
  script URLs must be declared in frontmatter (`Undeclared network endpoint`).
- **Registry scan gate hardened**: `publish --force` no longer bypasses
  high-severity security findings — `--force` only overrides duplicate-version
  entries. Unreviewed ingestion is the documented dominant registry risk.
- **Real regression gate in the bundled eval runner** (`run_evals.py --rollout`):
  each produced output is now compared against the case's promoted `expected`
  baseline (JSON-value equality; `compare_ignore: [keys]` for volatile fields
  like timestamps, `compare: "none"` to opt out) — divergence that slips past
  the command checks is reported as a `<baseline>` regression and exits 1.
  Promoted baselines at `golden/<id>/expected.json` arm the gate automatically
  and are never overwritten by a later `--promote`. Previously baselines were
  write-only and behavioral regressions were undetectable.
- **Holdout split**: golden cases marked `"split": "test"` are skipped by
  default, never promoted, and scored only with `--include-holdout` (CI does
  this as release scoring). The three bundled example skills each carry a
  promoted baseline set and one holdout case.
- **Claude Code plugin install path** (ponytail-style): `.claude-plugin/plugin.json`
  + `marketplace.json` at the repo root make the factory installable with
  `/plugin marketplace add FrancyJGLisboa/agent-skill-creator` +
  `/plugin install agent-skill-creator@agent-skill-creator` — no `curl | sh`
  needed on Claude Code. Generated skills get the same treatment: Phase 5
  Step 6.5 emits manifests from `scripts/claude-plugin-template/` (placeholders
  filled from SKILL.md frontmatter), so every generated skill is installable via
  `/plugin marketplace add <repo-or-local-path>`. The root SKILL.md is discovered
  through Claude Code's root-fallback, so no restructuring into `skills/` is
  required. Export zips (Desktop/Web, API variants) still exclude
  `.claude-plugin/` — those platforms don't read it; the plugin path travels
  with the git repo or local directory instead.

### Changed
- `references/agentdb-integration.md` is now explicitly marked **DESIGN
  DOCUMENT — NOT IMPLEMENTED** (no bridge module, nightly learner, or reflexion
  storage exists), and SKILL.md/README no longer present AgentDB as a current
  learning system. The shipped learning loop is the eval harness (rollout +
  baseline promotion + regression gate + holdout).
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
