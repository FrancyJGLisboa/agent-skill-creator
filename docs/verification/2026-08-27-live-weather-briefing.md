# Live weather briefing — end-to-end verification

Run date: 2026-08-27

## Real workflow

A traveler asks for current conditions in São Paulo. The installed
`live-weather-briefing-skill` resolves the city through Open-Meteo's public
geocoding API, calls the live forecast API, and writes a source-linked Markdown
briefing. The workflow is read-only: it does not book travel, send alerts, or
change external data.

## Live result

```text
Current weather: São Paulo, São Paulo, Brazil
Observed: 2026-08-27T09:45 (America/Sao_Paulo)
Condition: Clear sky
Temperature: 21.1 °C
Feels like: 21.9 °C
Wind: 7.8 km/h
```

## Reliability evidence

```text
sao-paulo: 3 passed
new-york: 3 passed
rollout: 6 passed, 0 failed, 0 errored, 0 regressed
```

The full skill graph passed its specification, security, pipeline, and eval-schema
gates. The generated skill was installed at project scope for Codex and the installed
copy produced the live São Paulo briefing.

The package declares compatibility with 17 agent environments. This is installer
coverage, not a claim that this one run tested every environment.

## Reproduce

```bash
python3 scripts/skill_graph.py run references/examples/live-weather-briefing-skill --jobs 4
python3 references/examples/live-weather-briefing-skill/scripts/run_evals.py \
  references/examples/live-weather-briefing-skill --rollout
references/examples/live-weather-briefing-skill/install.sh --platform codex --project
.agents/skills/live-weather-briefing-skill/scripts/run_pipeline.py \
  --city "Sao Paulo, BR" --output /tmp/live-weather-briefing.md
```
