# Live Weather Briefing Skill

Create a current, source-linked weather briefing for a named city using the
Open-Meteo public APIs.

## Use

```bash
python3 scripts/run_pipeline.py --city "Sao Paulo, BR" --output briefing.md
```

## Verification

The creation evidence is in [VERIFICATION.md](VERIFICATION.md). Regenerate it from
the factory after a material change:

```bash
python3 ../../scripts/generate_verification.py . --run-kind live --environment codex
```

The command performs live API requests. Use `--no-rollout` when an external system
is unavailable and only static checks are appropriate.

## Install

```bash
./install.sh --platform codex --project
```
