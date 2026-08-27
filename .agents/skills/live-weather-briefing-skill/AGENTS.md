# Live Weather Briefing Skill

Use this skill for a current, source-linked weather briefing for one named city.

Run:

```bash
python3 scripts/run_pipeline.py --city "Sao Paulo, BR" --output briefing.md
```

It uses Open-Meteo's live geocoding and forecast APIs. Present the resolved city,
observation time, temperature, apparent temperature, wind, condition, and source
links. Do not make bookings, issue safety alerts, or infer missing conditions.

## Gotchas

- Current conditions are advisory model data, not a safety alert.
- Qualify ambiguous city names with a country or region.
- Always show the observation time because conditions change after retrieval.
