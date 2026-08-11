---
name: pr-blocker-summarizer
description: Summarizes open pull requests into a blockers-first standup digest. Activates when the user asks to summarize open PRs, find blocked pull requests, generate a PR standup, or triage review backlog from a PR export.
license: MIT
metadata:
  author: agent-skill-creator
  version: 1.0.0
  created: 2026-06-27
  last_reviewed: 2026-07-20
  review_interval_days: 180
---

# PR Blocker Summarizer

Turn a JSON export of open pull requests into a blockers-first digest: which PRs
are blocked (failing checks, requested changes, or stale), which are ready to
merge, and a one-line count an agent can post to standup.

A bundled **example** skill — small but real, used to demonstrate the creator's
validation, pipeline, and eval-rollout machinery.

## Activation

Activates on "summarize open PRs", "what's blocking my PRs", "PR standup",
"review backlog". Do **not** activate on general git/GitHub questions unrelated to
triaging a set of PRs.

## Input

A JSON array of PRs, each with `title`, `state` (`open`), `checks`
(`passing`/`failing`), `review` (`approved`/`changes_requested`/`pending`), and
`age_days`. Missing fields are treated conservatively (counted as not-blocked only
when clearly ready).

## Run

```bash
python3 scripts/run_pipeline.py --input prs.json --output digest.json
```

Output JSON shape:

```json
{
  "total": 7,
  "blocked": [{"title": "...", "reasons": ["failing checks"]}],
  "ready": ["..."],
  "summary": "7 open · 3 blocked · 2 ready to merge"
}
```

## Gotchas

- **`blocked` + `ready` does not equal `total`.** A PR is `ready` only when
  `checks` is explicitly `passing` *and* `review` is explicitly `approved`. A PR
  with no blockers but a missing `checks` field lands in neither list and vanishes
  from both counts. Never narrate the summary line as if the two numbers account
  for every PR — say "N blocked, M ready" and leave the remainder unclaimed.
- **`state` is read from the input but never filtered on.** A closed or merged PR
  left in the export is counted in `total` and classified like any open one. Filter
  the export before running if it may contain non-open PRs.
- **`review: pending` counts as blocked** ("awaiting review"). A PR opened five
  minutes ago is reported as a blocker. This is intentional for standup triage, but
  it inflates the blocked count on teams that open PRs early.
- **A non-numeric `age_days` silently skips the stale check** rather than erroring.
  An export with `"age_days": "unknown"` will never flag anything stale, and the
  digest gives no sign that the check did not run.

## Anti-goals

- Does not call the GitHub API; it works on an exported PR list.
- Does not merge or comment on PRs; it only summarizes.
