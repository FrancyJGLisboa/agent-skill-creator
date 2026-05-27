# agent-skill-creator v6.0 — Artifacts-First Design

**Status:** Draft for review
**Date:** 2026-05-27
**Author:** Francy Lisboa Charuto (brainstormed with Claude)
**Supersedes:** Prior v6 spec drafts focused on five-axis composability

---

## 1. Mission and positioning

v6 is the first agent skill creator that generates skills which emit
interactive React artifacts in Claude Code (with Claude.ai web as a stretch
target if the same emission format works there — to be verified). Outside
Claude (Cursor, Cline, Codex CLI, Gemini CLI, etc.), skills degrade honestly
to formatted markdown.

This is a deliberate scope reduction from the prior v6 drafts. The earlier
spec proposed a five-axis composability model with capability registry,
contracts, and a custom handoff protocol. Two issues forced a redesign:

1. The handoff protocol (`::: visualization` named blocks) does not exist in
   any host. Artifact rendering is a host capability, not a skill capability.
   Skills emit text; hosts decide what to do with it.
2. If composability is invisible to the user (the UX invariant), the only
   consumer of the abstraction is the creator's own internals. That is code
   organization, not a product feature.

The honest scope of v6 is: **v4 plus a new Phase 2 step that detects when a
skill's output is visualizable and inlines a React artifact emission template
into the generated skill.**

### Headline

"v6 — agent-skill-creator now generates skills that render dashboards in
Claude. Other hosts receive formatted markdown."

Specific. Verifiable. Defensible against Anthropic Skills (markdown-only),
community creators (no one else does this), and agent frameworks (no React
code required from the user).

---

## 2. UX invariants

These cannot break, or v6.0 does not ship.

- **Same command, same UX as v4.** `/agent-skill-creator <description>`
  produces an installed skill, with no JSON manifest editing, no axis prefix,
  no exposed composability concept.
- **Cross-platform install path unchanged.** `install.sh` and `install.ps1`
  continue working on macOS, Linux, Windows; the supported hosts list stays
  at 20+.
- **v4 skills keep working.** Skills authored under v4 install and execute
  under v6 without modification. There is no migration tool because there is
  no capability registry to migrate.
- **Time to install does not regress.** A v6 skill creation from prompt to
  installed-and-ready is ≤110% of the equivalent v4 timing.

### What the user sees that is new

Before: requested "weekly sales report skill," received a skill that produces
markdown.

After: requests the same skill, receives a skill that produces markdown plus,
when the output is tabular/numeric/spatial and the host is Claude, an
interactive React component rendered alongside.

### What the user does not see

The Phase 2 artifact assessment step. The inline React template. Any new
naming convention. Any new frontmatter fields exposed in the install summary.

---

## 3. Architecture

### 3.1 No new abstractions

v6 deliberately does not introduce:

- A capability skill registry separate from the existing skill registry
- An axis prefix system (no `dom/`, `cap/`, `fmt/`)
- A custom handoff protocol with named blocks
- A composition manifest
- Per-skill input/output schemas as a first-class concept

If any of these become necessary later, they can be added in v6. For v6.0,
the simplest design that delivers artifact output is the design.

### 3.2 One new pipeline step

A new step inside Phase 2 (Design), named "Artifact Opportunity Assessment,"
runs after the domain has been identified and before the SKILL.md is
generated.

The step answers two questions:

1. Is this skill's expected output visualizable? (heuristic, see §3.4)
2. If yes, which artifact template fits? (line chart, bar chart, table, KPI
   cards, or none for v6.0)

If the answer to (1) is yes, the chosen template is inlined into the
SKILL.md being generated. The skill's body gets instructions like: "When
emitting output, also emit the following React component using Claude's
artifact protocol: [inlined template body]."

If the answer to (1) is no, the skill is generated exactly as v4 would have
generated it.

### 3.3 Artifact emission target

v6.0 targets exactly one rendering environment: **Claude Code in-chat
artifact rendering.** The implementation plan must include an explicit
verification task to confirm the exact emission format Claude Code expects.
This is non-negotiable — the previous spec was blocked on having invented a
non-existent protocol.

In hosts that do not render artifacts, the skill's output appears as the
markdown analysis followed by a fenced code block containing the React
component source. The component itself does not render, but the analysis is
still useful. This is "honest degradation."

### 3.4 Artifact detection heuristic

The detector classifies the expected output of a proposed skill across four
signals:

- **Tabular signal:** does the workflow describe rows × columns of data?
  (e.g., "weekly sales report", "inventory by warehouse")
- **Temporal signal:** does the output describe values over time? (e.g.,
  "month over month", "weekly trend")
- **Comparative signal:** does the output compare entities? (e.g., "by
  region", "by salesperson")
- **KPI signal:** does the output emphasize headline numbers? (e.g.,
  "executive dashboard", "key metrics")

These signals are not orthogonal — a "weekly regional sales report" hits
tabular + temporal + comparative. The detector picks the template that best
matches the dominant combination (line chart for temporal-dominant, bar chart
for comparative-dominant, KPI cards for headline-numbers-dominant, table as
a baseline when nothing else fits but data is structured).

Implementation: a Python script in `scripts/artifact_detector.py` that takes
the parsed Phase 1 Discovery output as input and returns either `None` or a
template name. Heuristic is keyword-and-pattern-based for v6.0. A learned
classifier is not in scope.

### 3.5 Artifact templates

Four templates ship in v6.0:

- `references/artifact-templates/line-chart.jsx` — time series
- `references/artifact-templates/bar-chart.jsx` — categorical comparisons
- `references/artifact-templates/kpi-cards.jsx` — headline numbers
- `references/artifact-templates/data-table.jsx` — structured rows (baseline)

Each template uses the same React + recharts (or shadcn for cards/tables)
stack that the artifact runtime supports. Templates use placeholder data
arrays that the Phase 2 generator replaces with skill-specific instructions
on how to populate them.

Templates are inlined into the generated SKILL.md. They do not live as
separate installable units. If a user inspects a generated v6 skill, the
React template is visible inside the SKILL.md alongside the domain
instructions.

---

## 4. Data flow

### 4.1 Skill creation flow

```
1. User invokes: /agent-skill-creator weekly sales report
2. Triage Engine: classifies input (existing v4 logic)
3. Phase 1 Discovery: identifies domain = sales reporting
4. Phase 2 Design:
   4a. (NEW) Artifact Opportunity Assessment
       - Detector reads Phase 1 output
       - Tabular ✓, Temporal ✓, Comparative ✓
       - Picks "bar-chart" as primary template
   4b. Template inlined into draft SKILL.md
   4c. Domain instructions written around the artifact emission
5. Phase 3 Architecture: existing v4 logic
6. Phase 4 Detection: existing v4 logic
7. Phase 5 Implementation:
   - Generate final SKILL.md
   - Run security scan (existing)
   - Validate spec (existing)
   - Install via install-skill.sh (existing — unchanged)
8. User sees: "✓ Skill weekly-sales-report installed"
   (same message as v4)
```

### 4.2 Skill invocation flow (Claude Code)

```
1. User invokes: /weekly-sales-report
2. Skill reads data, performs analysis
3. Skill emits:
   - Markdown analysis text
   - Claude artifact protocol invocation containing the React component
     with the analysis data substituted in
4. Claude Code:
   - Recognizes the artifact protocol
   - Renders the component in-chat
5. User sees: analysis text + rendered chart
```

### 4.3 Skill invocation flow (non-Claude host)

```
1. User invokes: /weekly-sales-report (via Cursor / Cline / Codex / Gemini)
2. Skill reads data, performs analysis
3. Skill emits the same output
4. Host:
   - Does not recognize artifact protocol
   - Displays the artifact tag/block as fenced code (host-dependent)
5. User sees: analysis text + React component source visible as code
```

This is acceptable. The analysis is still useful. The component source is
copy-pasteable into any React environment. The skill does not error.

---

## 5. Files added and modified

### 5.1 New files

```
references/
  phase2-artifact-assessment.md       # When and how to assess artifact fit
  artifact-templates/
    line-chart.jsx
    bar-chart.jsx
    kpi-cards.jsx
    data-table.jsx
scripts/
  artifact_detector.py                # Heuristic classifier
```

### 5.2 Modified files

```
SKILL.md                              # Mention Phase 2 artifact step
references/phase2-design.md           # Document the new step
references/pipeline-phases.md         # Update pipeline diagram and narrative
```

### 5.3 Files unchanged

```
install.sh, install.ps1               # Same install path
scripts/skill_registry.py             # No capability dimension
scripts/validate.py                   # No new validation rules
scripts/security_scan.py              # No changes
references/cross-platform-guide.md    # No new platforms
registry/registry.json                # No schema changes
```

The diff between v4 and v6 is intentionally small.

---

## 6. Failure modes and error handling

| Failure | Behavior |
|---|---|
| Detector misclassifies (false positive) | Skill emits a chart for non-chart data. User can regenerate with `--no-artifact` flag, or the runtime fallback (the data still shows up as text/table) carries the information. |
| Detector misclassifies (false negative) | Skill produces only markdown when a chart would have helped. User can regenerate with `--artifact <type>` flag. |
| Template is malformed in artifact rendering | Claude Code displays an error in the artifact iframe; the markdown analysis still renders correctly above it. Skill does not crash. |
| Host does not support artifacts | React component appears as fenced code. Analysis is unaffected. |
| Artifact protocol format changes upstream | The four templates need to be updated. This is a maintenance task, not a runtime failure. Pinning to a specific Claude Code version range in compatibility notes is reasonable. |

There is no migration tool because there is no capability registry to
migrate. v4 skills run unchanged. There is no install-time interaction
required.

---

## 7. Testing strategy

### 7.1 Unit tests

`scripts/artifact_detector.py` requires a labeled dataset:

- 50+ skill descriptions, half visualizable, half not
- Expected template assignment for the visualizable half
- Accuracy threshold: ≥85% correct template assignment

Examples to include in the test set:
- "weekly sales report" → bar-chart or line-chart
- "monthly revenue trend" → line-chart
- "executive KPI dashboard" → kpi-cards
- "inventory by warehouse" → data-table or bar-chart
- "deploy runbook" → None
- "SOX compliance checker" → None
- "Brazil regional crop forecast" → bar-chart or data-table

The 85% threshold is intentionally lower than the originally proposed 90%
on 20 examples — a larger sample makes the metric meaningful.

### 7.2 Integration tests

Generate a fixed set of 5 skills end-to-end (one per template plus one
non-visualizable to verify the negative path), install them in a sandbox,
invoke them with canned data, and verify:

- Markdown analysis is present
- Artifact emission is syntactically correct for the Claude protocol
- Component source includes the canned data correctly substituted

These tests run without a real LLM in the loop wherever possible (use fixture
outputs).

### 7.3 Regression tests

Critical for the 180+ forks. Select 10 representative v4 skills (the
implementation plan picks the specific 10, preferring those exercised in
existing examples or referenced in README), install them via v6's install
flow, invoke them with canned data, and verify output matches the v4
baseline byte-for-byte (excluding timestamps).

If any v4 skill fails to install under v6, the release blocks.

### 7.4 Manual verification

Two manual checks required before tagging v6.0:

1. Generate a skill in v6, install it, invoke it in Claude Code, and confirm
   the artifact renders visually. Capture the screenshot for release notes.
2. Generate the same skill, install it, invoke it in Cursor (or another
   non-Claude host), and confirm the markdown analysis is useful even
   without the artifact rendering.

---

## 8. Success criteria (binary)

All seven must be yes, or v6.0 does not ship.

1. **UX preserved.** Time from `/agent-skill-creator <input>` to installed
   skill is ≤110% of v4 on 20 sample inputs. ✓/✗
2. **v4 forks not broken.** Suite of 10 popular v4 skills installs and
   produces the same output under v6. ✓/✗
3. **Artifact end-to-end works in Claude Code.** A v6-generated skill
   visibly renders a React artifact when invoked. (Manual verification.) ✓/✗
4. **Honest degradation in non-Claude hosts.** A v6-generated skill produces
   useful markdown output in Cursor or Cline. (Manual verification.) ✓/✗
5. **Detector accuracy ≥85%.** On 50+ labeled examples. ✓/✗
6. **Cross-platform install works.** install.sh on macOS and Linux,
   install.ps1 on Windows. 20+ supported host claim still validates. ✓/✗
7. **Verification task completed.** Implementation plan includes (and
   completes) an explicit task to confirm Claude Code's exact artifact
   emission format before inlining templates. ✓/✗

---

## 9. Non-goals for v6.0

Each of these has been considered and explicitly excluded:

- **Multi-host artifact rendering.** Cursor, Cline, Codex CLI, Gemini CLI
  support beyond text degradation is out. Would require MCP infrastructure
  or per-host extensions.
- **Capability registry.** No `cap/*` skills. No separate registry. Templates
  are inlined into domain skills.
- **Axis prefix system.** No `dom/`, `cap/`, `fmt/`, `sty/`, `val/` namespace.
  Naming convention unchanged from v4.
- **Custom handoff protocol.** No `::: visualization` named blocks. Skills
  emit text and Claude's existing artifact protocol — nothing else.
- **Multi-domain composition.** No skills covering two domains.
- **Specialization tree.** No `specialization_of` field.
- **Parameterized compositions.** No composition manifest, parameterized or
  otherwise.
- **Runtime validation engine.** No `val/*` axis. Validation stays at
  generation time (existing v4 logic) plus the artifact assessment.
- **Auto-observation.** No proactive skill suggestion. User invokes the
  creator explicitly.
- **Marketplace for third-party templates.** Only the four bundled templates
  in v6.0. Community templates can be considered in v6.1+.
- **Telemetry to refine detection heuristics.** Optional follow-up, opt-in,
  not blocking v6.0.

If any of these are added later, they become explicit v6.x or v6 work.

---

## 10. Risks

### 10.1 Claude artifact protocol changes

The exact emission format for Claude Code artifacts is not documented as a
public stable interface. If it changes upstream, the four templates need
updates. Mitigation: pin templates to a known-good Claude Code version range
in compatibility notes, and treat template maintenance as ongoing work.

### 10.2 Detector false positives

A skill that should not have a chart gets one anyway. Mitigation: the
`--no-artifact` flag lets the user override. Telemetry-based refinement is a
v6.1 concern.

### 10.3 Marketing claim disputed

"Renders dashboards in Claude" is precise and verifiable. The risk is that
competitors counter with "we render too" claims that conflate Claude.ai
artifacts with what a skill creator delivers. Mitigation: lead with a video
demo, not a feature comparison table.

### 10.4 Scope creep during implementation

The temptation to bring back the capability registry "while we're at it"
will be real. The non-goals list is the answer. v6.0 is deliberately small.

---

## 11. Open questions

These are unresolved at the design stage and must be answered in or before
implementation planning:

- **Q1.** What is the exact emission format for Claude Code in-chat
  artifacts? (Empirical verification required before inlining templates.)
- **Q2.** Does Claude Code share the artifact protocol with Claude.ai, or
  does each have its own variant? If different, do we target both or one?
- **Q3.** How are the four templates kept in sync if Anthropic changes the
  artifact stack (e.g., adds a new sandbox library)? Versioning policy
  needed.
- **Q4.** Should v6 emit an artifact when the skill's input data is missing
  (the user invokes the skill without data)? Proposal: yes, with placeholder
  data clearly labeled — the artifact teaches the user what the skill
  produces. To be confirmed.

---

## 12. Implementation milestones (handoff to writing-plans)

Suggested decomposition for the implementation plan:

1. **M1 — Verify Claude artifact protocol.** Empirical task. Generate a
   minimal skill by hand that emits an artifact in Claude Code. Document the
   exact emission format. Pin to a known-good Claude Code version.
2. **M2 — Build the four templates.** Implement line-chart, bar-chart,
   kpi-cards, data-table as inline-able React components using the verified
   protocol.
3. **M3 — Build the detector.** `scripts/artifact_detector.py` with the
   50+ labeled example test set. Hit 85% accuracy.
4. **M4 — Wire Phase 2 artifact assessment.** Modify pipeline so Phase 2
   calls the detector and inlines the chosen template.
5. **M5 — Regression test against v4 skills.** Suite of 10 popular v4
   skills. Confirm no breakage.
6. **M6 — Manual end-to-end verification.** Generate, install, invoke in
   Claude Code and in one non-Claude host. Capture artifacts for release
   notes.
7. **M7 — Update docs.** SKILL.md, references/, README.

Each milestone is bounded, has a binary completion criterion, and the order
is sequential (M1 blocks M2, M3 is independent of M2 but blocks M4, etc.).

---

## 13. What this design does NOT promise

To be explicit, lest implementation drift back into the prior v6 ambition:

- It does not promise composability as a user-visible feature.
- It does not promise runtime validation.
- It does not promise auto-observation.
- It does not promise five-axis design.
- It does not promise contracts between skills.
- It does not promise a capability marketplace.
- It does not promise rendering in non-Claude hosts beyond honest text
  degradation.

These were discussed, judged out of scope for v6.0, and intentionally
excluded. If any of them become urgent, they become v6.1, v6, or a separate
project.

---

## Appendix A: Example generated skill (sketch)

The Phase 2 generator, when artifact assessment chooses `bar-chart`, would
produce a SKILL.md whose body looks roughly like this (simplified):

```markdown
# /weekly-sales-report

When the user invokes this skill, you will:

1. Read the sales data from the source specified in the user's input.
2. Aggregate revenue by region for the past 7 days.
3. Emit your analysis as markdown:
   - A 2-3 sentence summary of the week
   - Notable changes vs. prior week
   - Anomalies if any
4. Then emit the following artifact using Claude's artifact protocol,
   substituting the aggregated data into the `data` array:

   [INLINED bar-chart.jsx HERE, with a placeholder data array marked
    for substitution]

   The data array should be of the form:
   [{ region: "North", revenue: 12500 }, ...]
```

The exact protocol invocation syntax is filled in by M1's empirical
verification.

---

## Appendix B: Why "v6" and not "v4.1"

This change introduces a new category of output (artifacts) and a new
pipeline step. It is larger than a patch but smaller than the prior v6
draft. v6.0 still makes sense as a version name because:

- The pipeline gains a new phase step (architectural addition).
- Users see a qualitatively new behavior (rendered charts vs. text only).
- The marketing story is coherent at a major-version level.

If the scope grows during implementation to include any of the deferred
non-goals, the version remains v6; if scope shrinks to something less than
this design, it becomes v4.1.

---

## Appendix C: Decisions explicitly reversed from prior v6 drafts

For audit clarity, these decisions changed during this brainstorm:

- **Reversed:** "Composability as foundation, three features on top."
  Reason: invisible composability is just internal code organization, per
  advisor review. Adopted instead: no composability abstraction at all.
- **Reversed:** "Five-axis model with dom/, cap/, fmt/, sty/, val/ prefixes."
  Reason: same as above. Adopted instead: no axis system.
- **Reversed:** "Custom `::: visualization` handoff protocol."
  Reason: this protocol does not exist in any host; skills cannot invent
  rendering. Adopted instead: target Claude's actual artifact protocol with
  empirical verification.
- **Reversed:** "Cross-platform 20+ with artifacts."
  Reason: most of the 20 hosts do not render artifacts. Adopted instead:
  "Claude-native + honest degradation."
- **Confirmed:** UX invariant — zero visible composability for the common
  user. v4's single-command experience preserved.
