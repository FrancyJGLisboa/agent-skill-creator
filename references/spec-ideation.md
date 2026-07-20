# Spec Ideation — the factory front door for vague input

Most factory input names a workflow ("every week I pull sales data and make a
report") — go straight to Phase 1. This reference is for the other case: the user
arrives **without a skill in mind** and needs help finding one *and* shaping it
into a spec before anything gets built.

Fire this **before Phase 1** when the input is too thin to spec:

- One word or a shrug: `freight`, `here`, `this is ridiculous, there has to be a better way`
- An explicit ask: "give me a skill idea", "what should I automate", "what could I build with this"
- A pile with no goal: a dumped transcript / inbox / folder and no stated outcome

If the input already names a concrete recurring workflow, skip this — you'd only
slow the user down.

## The inversion (read first)

Ideation instincts say "reject the obvious, get novel." **For skills that is
backwards.** A good skill is *boring, repeated, and obvious* — its value is
reliability on a chore the user already does every week, not surprise. Spend the
creativity on *how* to automate the chore, never on *what* to automate. The
winning candidate is usually the dullest recurring task the user mentions.

## Procedure

### 1 — Harvest real recurring work (never invent)

Do not brainstorm skill ideas in a vacuum — "AI skill ideas" is peak slop. Pull
the constraint from the user's actual life:

- Ask: "paste your last 15–20 repeated tasks", or "walk me through a typical
  week", or point me at the folder / inbox / transcript you already have.
- Atomize into one task per line.
- Keep only what recurs. A thing done once is not a skill.

If the user gives you nothing to mine, **stop and ask** — a harvested-from-nothing
idea is fabricated by construction and will fail the grounding check.

### 2 — Filter by skill-fit (kill non-skills before shaping)

A harvested task is skill-worthy only if **all four** hold. Drop the rest — say
plainly why, and point app/game/firmware ideas at plain coding-agent work instead
(the factory ships markdown + scripts, not a native binary).

| # | Check | Fails when |
|---|---|---|
| 1 | **Repeatable** — recurring trigger, run again and again | it's a one-off build |
| 2 | **Runs as markdown + scripts** (Python/shell) | needs a native app, game engine, firmware toolchain, or GPU |
| 3 | **File / data / document / API / inbox centric** | operates on pixels or physical hardware |
| 4 | **Binary-checkable** — you can write 3–5 yes/no evals + golden cases | success is subjective ("make it delightful") |

### 3 — Shape each survivor as a situated job

State the trigger concretely (Jobs-to-Be-Done form), so it isn't a platitude:

> **When [situation/trigger], I want to [do the chore], so I can [outcome].**

Generic ("when I want to be productive") → reject. Specific ("every Monday when I
merge five regional CSVs by hand") → keep.

### 4 — Hand off

Present 2–3 shaped candidates, cheapest-win first, and let the user pick one. Then
either:

- **Continue into the factory** — carry the chosen job into Phase 1/2 as the
  workflow to build; or
- **Emit a paste-ready spec** the user can run themselves (the "finished tool as
  if it already exists" shape):

```
The finished skill, as if it already exists:
[one paragraph — who runs it, what triggers it, what it does end to end]

Recurring trigger: [the exact situation that fires it]

The 3 things it must do, in order:
1. [step]   2. [step]   3. [step]

Inputs it reads: [real files / folders / API / inbox]
Output it produces: [the artifact]
"Done" looks like: [an observable end state a stranger could verify]

Grade itself against these binary checks: [3–5 yes/no checks]
```

The `grade itself against` line seeds Phase 2's eval spec directly — no
reformatting. Never emit a spec with an empty bracket: that just defers the work
to the factory as a question, which is the failure this front door exists to prevent.

## Success criteria (loss function)

1. **Zero-question handoff** — the chosen spec enters Phase 1/2 (or pastes back in)
   with no follow-up questions: trigger, the 3 ordered steps, and "done" are all filled.
2. **Grounded** — every candidate cites the harvested line it came from, never an
   invented chore.
3. **Skill-shaped** — at least one survivor passes all four skill-fit checks;
   app/game/firmware candidates were dropped in step 2 with a reason.

**Held-out bellwether (never tune against it):** run the emitted spec end to end
through the factory and confirm the generated skill's *bundled eval passes on its
first golden case.* This front door never sees that result while generating — it is
the only check that proves the spec was real, not merely well-formed. If
well-formed specs keep yielding skills that fail their own first eval, the harvest
or the skill-fit filter is wrong, not the formatting.

## Worked example

Harvested line: *"every Monday I download 5 regional sales CSVs, paste them into
one sheet, dedupe by store ID, and email the total to my manager."*

- Skill-fit: repeatable ✓, scripts ✓, file-centric ✓, binary-checkable ✓ → keep.
- Job: "When it's Monday and the 5 regional CSVs have landed, I want them merged,
  deduped, and totalled, so I can send one number without an hour of paste."
- Self-grading checks → "5 files consumed", "no duplicate store IDs", "grand total
  == sum of per-file totals" — these drop straight into Phase 2's eval spec.

Contrast — *"I want a cozy desktop pet of my cat"*: fails check 4 (delight isn't
gradeable) and 2/3. Drop it, name why, don't shape it.

## Anti-slop notes

- The failure mode here is **inventing** plausible chores instead of harvesting
  real ones. If you can't cite the source line, you made it up.
- Don't get clever. "A skill that generates creative reports" is slop; "a skill
  that merges these 5 named CSVs and flags rows where Q3 < Q2" is a skill.
- Don't route apps/games/firmware here to be polite. Say the factory can't ship
  them and redirect.
