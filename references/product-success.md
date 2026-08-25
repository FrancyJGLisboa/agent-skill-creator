# Product Success Ledger

The factory's product-success metric is **Durable Active Skills**, not generated
file count. A skill is durable and active when, during the trailing 28 days, it
has at least three successful representative or real runs across two days, has
passed gates, and has no regression newer than its latest passing gate.

## Privacy boundary

The ledger is local JSONL. It has no network client and stores only:

- a fixed event name;
- a locally salted, pseudonymous skill ID;
- UTC timestamp and run ID;
- `success` or `failure`;
- an optional duration.

It never stores skill names, paths, prompts, workflow descriptions, inputs,
outputs, corrections, credentials, or endpoints. The random salt remains beside
the ledger with owner-only permissions where the platform supports them. Deleting
the ledger and salt deletes the measurement history; there is no remote copy.

Run `python3 scripts/success_ledger.py path` to see the location. Set
`ASC_SUCCESS_LEDGER=/another/local/path.jsonl` to move it, or set
`ASC_SUCCESS_LEDGER=off` to disable recording. Summaries are local unless the user
explicitly decides to share them.

## Lifecycle events

The vocabulary is closed so arbitrary business data cannot become an event:

| Event | Record when |
|---|---|
| `creation_started` | The factory starts turning evidence into one skill |
| `intent_confirmed` | The user confirms or corrects the workflow hypothesis |
| `gates_passed` | The graph constraints and four static gates pass |
| `representative_run_passed` | The first safe result is produced and inspectable |
| `skill_run` | A generated skill completes a later real or safe run |
| `correction_recorded` | `evolve.py --correct` captures a user correction |
| `regression_detected` | The eval rollout fails during maintenance |
| `skill_shared` | A skill is successfully distributed to another user or team |

Generate one creation run ID and reuse it through the representative run:

```bash
python3 scripts/success_ledger.py new-run
python3 scripts/success_ledger.py record creation_started --skill <planned-skill> --run-id <run-id>
python3 scripts/success_ledger.py record intent_confirmed --skill <skill-name> --run-id <run-id>
python3 scripts/success_ledger.py record gates_passed --skill <skill-name> --run-id <run-id>
```

For the representative pipeline run, set `ASC_RUN_EVENT` and `ASC_RUN_ID`; the
generated `run_pipeline.py` records the successful result with the same run ID:

```bash
ASC_RUN_EVENT=representative_run_passed ASC_RUN_ID=<run-id> \
  python3 <skill>/scripts/run_pipeline.py --input <fixture> --output <result>
```

Ordinary pipeline runs omit those variables and record `skill_run`. Recording is
best-effort: a read-only state directory or disabled ledger must never make the
business workflow fail.

## Local metrics

Run:

```bash
python3 scripts/success_ledger.py summary
python3 scripts/success_ledger.py summary --json
```

The report contains:

- **Verified creation rate** — representative runs divided by creation starts,
  paired by creation run ID.
- **Median minutes to first result** — creation start to representative result.
- **14-day second-run rate** — eligible verified skills with a later successful
  `skill_run` within 14 days. Recent skills are excluded until their window closes.
- **Durable Active Skills** — the 28-day definition at the top of this file.
- **Correction recovery rate** — corrections followed by a passing gate.
- **Shared durable-skill rate** — durable skills with a recorded successful share.

Malformed JSONL records are skipped and counted. Use `--as-of <ISO timestamp>` for
reproducible reports and tests.
