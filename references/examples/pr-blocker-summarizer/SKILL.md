---
name: pr-blocker-summarizer
description: Summarizes open pull requests into a blockers-first standup digest. Activates when the user asks to summarize open PRs, find blocked pull requests, generate a PR standup, or triage review backlog from a PR export.
license: MIT
metadata:
  author: agent-skill-creator
  version: 1.0.0
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

## Anti-goals

- Does not call the GitHub API; it works on an exported PR list.
- Does not merge or comment on PRs; it only summarizes.
