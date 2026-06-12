# pr-blocker-summarizer

A bundled example skill: turns a JSON export of open pull requests into a
blockers-first digest — which PRs are blocked (failing checks, requested
changes, or stale), which are ready to merge, and a one-line standup count.

It is small but real, and demonstrates the creator's full machinery end to
end: SKILL.md activation, a `run_pipeline.py` orchestrator, and a bundled
eval spec with golden cases.

## Requirements

Python 3.10+ only — the pipeline uses the standard library (no third-party
dependencies, no requirements.txt needed).

## Run it

```bash
python3 scripts/run_pipeline.py \
  --input evals/golden/case-1/input.json \
  --output /tmp/pr-digest.json
cat /tmp/pr-digest.json
```

Input: a JSON array of PRs, each with `title`, `state`, `checks`
(`passing`/`failing`), `review` (`approved`/`changes_requested`/`pending`),
and `age_days`. Missing fields are treated conservatively.

## Run the evals

```bash
python3 scripts/run_evals.py . --validate   # check the eval spec is well-formed
python3 scripts/run_evals.py . --rollout    # execute the skill on golden inputs
python3 scripts/run_evals.py . --rollout --promote   # capture first baselines
```

The eval spec lives in `evals/pr-blocker-summarizer.eval.md` with three
golden cases under `evals/golden/`.

## Layout

```
pr-blocker-summarizer/
├── SKILL.md                  # activation + usage contract
├── scripts/run_pipeline.py   # PR JSON → blocked/ready triage → digest JSON
├── scripts/run_evals.py      # eval runner (validate / rollout / promote)
└── evals/                    # eval spec + golden cases
```
