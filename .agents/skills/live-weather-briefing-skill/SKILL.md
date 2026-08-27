---
name: live-weather-briefing-skill
description: >-
  Create a current, source-linked weather briefing for a named city using the
  Open-Meteo geocoding and forecast APIs. Activate for requests such as "what is
  the weather in Sao Paulo?", "prepare a current weather briefing for Tokyo", or
  "get today's live conditions for New York". Do not use for travel booking,
  weather alerts, historical climatology, or safety-critical decisions.
license: MIT
activation: /live-weather-briefing-skill
metadata:
  author: agent-skill-creator
  version: 1.0.0
  created: 2026-08-27
  last_reviewed: 2026-08-27
  review_interval_days: 30
  dependencies:
    - name: Open-Meteo Geocoding API
      url: https://geocoding-api.open-meteo.com/v1/search
      type: service
    - name: Open-Meteo Forecast API
      url: https://api.open-meteo.com/v1/forecast
      type: service
provenance:
  maintainer: agent-skill-creator
  version: 1.0.0
  created: 2026-08-27
  source_references:
    - https://open-meteo.com/en/docs/geocoding-api
    - https://open-meteo.com/en/docs
---

# /live-weather-briefing-skill

Create a current weather briefing for one city. Resolve the city through
Open-Meteo's geocoding API, then retrieve current conditions from its forecast API.
Always show the resolved location, observation time, and source URLs.

## Run

```bash
python3 scripts/run_pipeline.py --city "Sao Paulo, BR" --output briefing.md
```

The command makes two live, read-only API requests and writes a Markdown briefing.
It never books travel, sends alerts, or changes external data.

## Required behavior

1. Use the first exact geocoding result and show its country and coordinates.
2. Retrieve current temperature, apparent temperature, wind speed, weather code, and observation time.
3. State that weather is advisory and include the source URLs.
4. If a city cannot be resolved or an API response is incomplete, stop with an error; do not invent conditions.

## Gotchas

- Current conditions are model data, not a safety alert. Check local official warnings before decisions involving risk.
- A city name can be ambiguous. Include a country or region in the request when the city is not unique.
- Conditions change after retrieval; the briefing's observation time identifies the freshness of this result.

## References

- https://open-meteo.com/en/docs/geocoding-api
- https://open-meteo.com/en/docs
