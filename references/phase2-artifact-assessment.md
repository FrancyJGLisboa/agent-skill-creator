# Phase 2 — Artifact Opportunity Assessment

This step runs inside Phase 2 (Design), after Phase 1 has identified the
skill's domain and before the SKILL.md is generated. It decides whether
the generated skill should emit an interactive React artifact when invoked,
and if so, which of the four bundled templates to inline.

## Inputs

- `description` (str) — the user's workflow description (raw or normalized
  by Phase 1 Triage)
- `domain` (str | None) — the domain Phase 1 identified (unused in v6.0;
  reserved for future heuristics)

## Step 1 — Call the detector

```python
from artifact_detector import detect_artifact
template_name = detect_artifact(description, domain=domain)
```

`template_name` is one of:
- `"line-chart"` — temporal series
- `"bar-chart"` — categorical comparison
- `"kpi-cards"` — headline numbers
- `"data-table"` — structured rows baseline
- `None` — no artifact appropriate

## Step 2 — If no artifact, skip

If `template_name is None`, Phase 2 proceeds exactly as v4 did. The
generated SKILL.md contains no artifact instructions.

## Step 3 — If an artifact is chosen, inline the template

Read the template file:

```python
template_path = Path(__file__).parent / "artifact-templates" / f"{template_name}.jsx"
template_body = template_path.read_text()
```

Replace the substitution marker with skill-specific data shape
instructions. The marker is `/* AGENT_SKILL_DATA */` in every template.

The data shape instructions are a JavaScript comment block describing the
column names, types, and source for the array that the skill should
populate. For a "weekly sales report by region" skill, the substituted
section would read something like:

```jsx
const data = /* The skill must populate this with:
  [{ category: "<region name>", value: <numeric revenue> }, ...]
  Sourced from the sales database query in Step 2 of the workflow.
*/ [
  { category: 'Sample-A', value: 0 },
  { category: 'Sample-B', value: 0 },
];
```

The placeholder array stays as-is so the artifact still renders something
when the skill is invoked without real data.

## Step 4 — Wire emission instructions into SKILL.md

After inlining the template, add a section to the generated SKILL.md
body that tells the runtime model HOW to emit the artifact. Use the
emission format captured in `references/claude-artifact-format.md`.

The section should read approximately:

> "When emitting your output, after the markdown analysis, emit the
> following React component using Claude's in-chat artifact protocol
> [exact protocol syntax]. The data array should be populated from
> [data source described above]."

## Step 5 — Honest degradation note

Include a one-line note in the SKILL.md body acknowledging that the
artifact renders only in Claude environments. The exact wording:

> "Note: the React artifact renders interactively in Claude Code and
> Claude.ai. In other hosts, the component appears as fenced code and
> the markdown analysis above carries the full information."

## Failure handling

| Condition | Action |
|---|---|
| `detect_artifact` raises an exception | Phase 2 logs a warning, skips artifact inlining, proceeds as v4. Skill creation does not fail. |
| Template file missing | Phase 2 logs an error, skips artifact inlining, proceeds as v4. |
| Substitution marker absent from template | Same — log + skip + proceed. |

## Bypassing

The user can force or suppress artifact inlining:

- `/agent-skill-creator --no-artifact <description>` — never inline
- `/agent-skill-creator --artifact <template-name> <description>` — force
  the named template

When forced, the detector is not called and the named template is used
directly. Invalid `--artifact` values are rejected with a clear error
listing the four valid template names.

## Out of scope for v6.0

- Per-skill artifact customization (changing the JSX beyond the
  substitution marker)
- Multiple artifacts per skill
- User-defined templates
- Detector training based on telemetry
