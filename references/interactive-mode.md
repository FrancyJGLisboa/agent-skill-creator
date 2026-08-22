# Interactive and Guided-Light Creation

The default experience is guided-light: the user confirms the real-world workflow
and judges the first result while the factory owns technical decisions. Use full
interactive mode only when the user asks to learn the internals, requests control over
a consequential choice, or supplies domain expertise that materially changes the
result.

## Default: Guided-Light

### 1. Understand

Read all supplied material before asking anything. Present one compact hypothesis:

```
Here is the workflow I found:

Input: the Friday CRM export
Work: remove duplicates and total sales by region
Output: a PDF summary for the VP
Success: totals reconcile to the source and every region appears

Reply “yes” or correct the part I got wrong.
```

Ask no more than one high-impact question with the hypothesis. Do not ask the user to
choose an API, skill structure, file layout, eval format, or platform adapter unless
that choice changes the result they receive.

If confidence is already high and the user explicitly requested autonomous creation,
state the hypothesis as an assumption and continue without pausing.

### 2. Build

Use four user-facing progress labels regardless of the internal phase count:

```
Understand  ✓ workflow and success criteria confirmed
Build       ● creating the reusable workflow
Check       ○ testing structure, code, and known security risks
Try         ○ installing and producing one example result
```

Keep API comparisons, directory trees, frontmatter, file counts, and architecture
decisions in internal working notes. Show them only when the user asks for technical
detail or must make a real tradeoff.

### 3. Check

Run the normal validation, pipeline, security, and eval gates. Fix failures before
continuing. Describe the meaning in plain language:

- Validation: the skill has the required structure and metadata.
- Pipeline: its scripts compile and their dependencies are declared.
- Security scan: no known dangerous pattern matched; this is not proof of safety.
- Evals: the defined examples and checks pass.

### 4. Try

Auto-install the generated skill. Run one representative use case using a supplied
artifact when possible, otherwise a local golden fixture.

Verification must be safe and reversible. Do not send a real email or message, publish,
purchase, modify production data, or invoke another consequential action just to prove
the skill works. Use dry-run, sandbox, temporary output, or a local fixture.

Use the completion states defined in the root `SKILL.md`:

- `verified` only when an inspectable result exists.
- `verification-blocked` when credentials, data, or authority are missing.
- `installed` only when the user explicitly declines the run.
- `failed` when any build, gate, install, or representative run fails.

Lead a verified handoff with what now works, show the output, provide one invocation,
and give one correction command. Ask the user to judge the result before offering team
sharing.

## Full Interactive Mode

Activate when the user says “walk me through,” “explain each step,” “let me choose,”
or otherwise requests control.

Pause only for decisions that alter the real-world outcome:

1. Confirm the workflow and success criteria.
2. Present a source or API choice when cost, coverage, privacy, or reliability differs.
3. Present an architecture choice only when it changes maintenance or team ownership.
4. Preview consequential permissions or external effects before implementation.
5. Show and verify the representative result.

For each choice, recommend one option and explain the user-visible tradeoff. Avoid raw
file counts and implementation terminology unless the user is learning skill internals.

## Learning Mode

When the user asks to learn the process, map the human journey to the technical phases:

| User sees | Factory does |
|---|---|
| Understand | Input triage, discovery, success-criteria derivation |
| Build | Design, architecture, detection, implementation |
| Check | Validation, pipeline checks, security scan, evals |
| Try | Auto-install, safe representative run, correction capture |

Explain each phase after its output exists, so the explanation is grounded in the
user's actual skill rather than an abstract tutorial.

## Resuming

On resume, restate the four-state progress line and continue from the first incomplete
state. Reconfirm only when new evidence conflicts with the existing workflow or success
criteria.
