# Agent-run technical exercises — 2026-08-27

These are agent-run technical exercises. They prove only the commands and local
state stated below. They are not independent human-use, adoption, business-meaning,
or cross-runtime evidence.

## 1. Live API exercise: current weather briefing

- Input: `Sao Paulo, BR`
- Live result: São Paulo, Brazil; clear sky; 23.0 °C; observation time
  `2026-08-27T10:45`.
- Evidence: two read-only Open-Meteo source URLs in the generated briefing.
- The live rollout passed 9 structural output checks. The correction-retention
  test was created by this exercise, not by an external workflow owner.

## 2. Live API exercise: dependency release briefing

- Input: `openai/openai-python`
- Live result: release `v3.5.0`, published `2026-08-27T01:00:03Z`.
- Reliability: live cases for `openai/openai-python`,
  `anthropics/anthropic-sdk-python`, and `vercel/ai` all passed.
- Artifact: [github-release-briefing-skill verification](../../references/examples/github-release-briefing-skill/VERIFICATION.md).

## 3. Local marketplace exercise: governed publication

- Initialized an isolated Git-backed marketplace and admitted the version-bound
  release-briefing skill through `attest` and `add`.
- Publication initially failed because the declared compatibility set had no
  certification evidence. The claim was narrowed to Codex, where this agent ran
  the command; this does not certify an independent Codex user installation.
- Marketplace health reported `healthy`: 1 skill, 0 findings.

## 4. Simulated correction: maintenance mechanics

The simulated correction, “Treat a trailing two-letter country code as a
geographic qualifier, not part of the city name,” automatically produced:

- a proposed `SKILL.md` Gotchas edit;
- `evals/corrections/correction-20260827-135741-90678cdffd.json` as its
  regression test; and
- a patch-version recommendation with the reason recorded in `EVOLUTION.md`.

The refreshed weather [VERIFICATION.md](../../references/examples/live-weather-briefing-skill/VERIFICATION.md)
records the current fingerprint, commit binding, and a clean live rollout.

## 5. Local measurement exercise

With explicit consent valid through `2026-12-31T23:59:59Z`, this agent inserted
five test events. The resulting aggregate proves the privacy filter and counting
mechanics, not real adoption, retention, or reliability rates.

## 6. Local deployment-plan exercise

The published `github-release-briefing-skill` produced a non-mutating project
install plan for Codex. The plan selected the `native-skill` adapter, listed the
exact destination, and included its read-only API boundary and runtime readiness
requirements before installation.

## 7. Local stale-evidence exercise

In an isolated committed skill package, a human guidance edit made
`verification_errors()` return `verification is stale: SKILL.md, scripts, or
evals changed`. Regenerating `VERIFICATION.md` cleared that error. The artifact
cannot silently remain valid after behavior-defining files change.
