# Eval Spec: live-weather-briefing-skill

Each rollout makes a real, read-only API request. Conditions naturally change, so
the checks validate briefing structure rather than pinning a weather value.

```json
{
  "skill": "live-weather-briefing-skill",
  "run": "python3 scripts/run_pipeline.py --input {input} --output {output}",
  "criteria": [
    {"id": "title", "text": "Names a current weather briefing", "type": "command", "cmd": "grep -q '^# Current weather:' {output}"},
    {"id": "conditions", "text": "Contains the required current-condition fields", "type": "command", "cmd": "grep -q '^- Temperature:' {output} && grep -q '^- Feels like:' {output} && grep -q '^- Wind:' {output}"},
    {"id": "provenance", "text": "Includes both live source URLs", "type": "command", "cmd": "grep -q 'Geocoding: https://geocoding-api.open-meteo.com' {output} && grep -q 'Forecast: https://api.open-meteo.com' {output}"}
  ],
  "golden": [
    {"id": "sao-paulo", "input": "golden/sao-paulo/input.txt", "expected": null, "split": "val", "expected_status": "pending-first-green", "compare": "none"},
    {"id": "new-york", "input": "golden/new-york/input.txt", "expected": null, "split": "val", "expected_status": "pending-first-green", "compare": "none"},
    {"id": "tokyo", "input": "golden/tokyo/input.txt", "expected": null, "split": "test", "expected_status": "pending-first-green", "compare": "none"}
  ]
}
```
