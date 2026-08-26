# Structured workflow and meaning interview

Users do not need a complete skill prompt or a prewritten semantic contract. Start
from their problem, materials, and examples. The agent carries investigation,
comparison, structure, memory, drafting, and test generation. Humans retain business
authority and risk acceptance.

## Required flow

1. Start `interview.json` immediately:

   ```bash
   python3 scripts/structured_interview.py start interview.json \
     --problem "Monthly customer totals disagree" --created-by workflow-expert
   ```

2. Inspect supplied files, API/MCP documentation, schemas, representative samples,
   prior accepted outputs, and marketplace policy before asking questions. Record
   evidence-backed agent conclusions as `proposed`; never mark them `confirmed`.

3. Record competing meanings as `conflicting`. Each candidate must carry its own
   evidence. Do not collapse disagreement into generic prose.

4. Ask the single question returned by `status`. Show the evidence and bounded
   alternatives. Do not ask users for facts the agent can inspect, and do not present
   a questionnaire containing several unrelated decisions.

5. Let an identified human confirm consequential decisions. The domain owner must
   resolve definitions and precedence; the workflow owner must accept the objective,
   consequence, success measure, and failure impact.

6. Run the gate before design or generation:

   ```bash
   python3 scripts/structured_interview.py gate interview.json
   ```

   Exit `0` and `READY` permit generation. Exit `2` and `BLOCKED` require another
   evidence or decision loop. Copy the ready state into the generated skill root as
   `interview.json`; `validate.py` rejects a present but unresolved state.

## State meanings

| State | Meaning | Can generate? |
|---|---|---:|
| `unknown` | Not investigated | No |
| `proposed` | Agent inference with evidence | No |
| `conflicting` | Multiple supported interpretations | No |
| `confirmed` | Identified human accepted the decision | Yes |
| `not_applicable` | Identified human excluded it with a reason | Yes |

The core fields always cover objective, decision consumer, decision consequence,
success measure, failure impact, environmental requirements, authority owner, and
whether organizational semantics matter. When semantics apply, the gate additionally
requires definitions, source precedence, grain/unit, time semantics, ambiguity
behavior, and freshness policy.

## Agent commands

Record an investigated proposal:

```bash
python3 scripts/structured_interview.py propose interview.json \
  --field objective --value "Report active customers for revenue planning" \
  --actor agent --evidence accepted-report.xlsx
```

Record a conflict:

```bash
python3 scripts/structured_interview.py conflict interview.json \
  --field semantic.definitions --actor agent \
  --candidate '{"value":"open CRM account","evidence":["crm-schema"]}' \
  --candidate '{"value":"billable event in 30 days","evidence":["billing-policy"]}'
```

An authorized human resolves it:

```bash
python3 scripts/structured_interview.py resolve interview.json \
  --field semantic.definitions --choice '"billable event in 30 days"' \
  --authorized-human commercial-analytics-owner
```

The CLI also provides `confirm`, `not-applicable`, `status`, and `gate`. Confirmation
and exclusion require `--authorized-human <identity>`; agent proposals use `--actor`.
Values are parsed as JSON when possible, so use `true` or `false` for
`semantic_contract_applies`.

## Authority boundary

The agent may discover that CRM and billing disagree, propose a likely contextual
rule, draft the semantic contract, and generate its evals. It may not decide which
definition governs revenue reporting. If no authorized person can decide, generation
remains blocked or the eventual skill must explicitly ask/refuse at runtime.
