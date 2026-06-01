# Eval Spec: stock-analyzer

This skill ships its own loss function: a set of binary checks plus golden cases
that define what "the analysis worked" means. Run it anytime with
`python3 scripts/run_evals.py` (scores the golden baseline) or
`python3 scripts/run_evals.py --rollout` (runs the skill end-to-end on each golden
input and scores the real output).

## Criteria

1. **valid-json** (command) — the produced output parses as JSON.
2. **has-ticker** (command) — the output carries the requested `ticker`.
3. **has-signal-action** (command) — a trading `signal.action` is present
   (BUY / SELL / HOLD).
4. **signal-is-justified** (llm-judge) — the `signal.reasoning` actually supports
   the chosen action (not graded by the runner; checklist only).

## Golden cases

Three representative analysis requests. The skill embeds a timestamp in its output
(`datetime.now()`), so outputs are not byte-stable — the cases are seeded as
`pending-first-green`: the structural command checks above pass on any run, and you
can capture a concrete baseline with
`python3 scripts/run_evals.py --rollout --promote`.

- **case-1** — AAPL with RSI + MACD.
- **case-2** — MSFT with RSI + MACD + Bollinger.
- **case-3** — GOOGL with RSI only.

## Spec

```json
{
  "skill": "stock-analyzer",
  "run": "python3 scripts/run_pipeline.py --input {input} --output {output}",
  "criteria": [
    {"id": "valid-json", "text": "Output parses as JSON", "type": "command", "cmd": "python3 -c \"import json,sys; json.load(open(sys.argv[1]))\" {output}"},
    {"id": "has-ticker", "text": "Output carries a ticker", "type": "command", "cmd": "python3 -c \"import json,sys; d=json.load(open(sys.argv[1])); assert d.get('ticker')\" {output}"},
    {"id": "has-signal-action", "text": "Output has a signal.action", "type": "command", "cmd": "python3 -c \"import json,sys; d=json.load(open(sys.argv[1])); assert d['signal']['action'] in ('BUY','SELL','HOLD')\" {output}"},
    {"id": "signal-is-justified", "text": "signal.reasoning supports the chosen action", "type": "llm-judge"}
  ],
  "golden": [
    {"id": "case-1", "input": "golden/case-1/input.json", "expected": null, "split": "val", "expected_status": "pending-first-green"},
    {"id": "case-2", "input": "golden/case-2/input.json", "expected": null, "split": "val", "expected_status": "pending-first-green"},
    {"id": "case-3", "input": "golden/case-3/input.json", "expected": null, "split": "val", "expected_status": "pending-first-green"}
  ]
}
```
