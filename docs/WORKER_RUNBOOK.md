# Worker runbook: turn recurring work into a governed skill

Start with work you actually do. Paste a sentence, attach the files you already
use, or share a link to the source material. Do not write a technical specification.

This runbook is for a worker creating or improving a skill. A workflow owner
confirms business meaning when it affects correctness. A marketplace operator
approves and publishes skills for wider use.

## 1. Install and confirm the creator is available

On macOS or Linux, run this in Terminal:

```bash
curl -fsSL https://raw.githubusercontent.com/FrancyJGLisboa/agent-skill-creator/main/scripts/bootstrap.sh | sh
```

On Windows, run this in PowerShell:

```powershell
irm https://raw.githubusercontent.com/FrancyJGLisboa/agent-skill-creator/main/scripts/bootstrap.ps1 | iex
```

Reopen your AI tool and ask:

```text
What can agent-skill-creator do?
```

Expected: it describes creating reusable agent skills from workflows and source
material. If it does not, stop and use the [installation guide](INSTALL.md).

## 2. Give it one recurring workflow

Paste this into your AI tool, not into Terminal:

```text
/agent-skill-creator Every Friday I export Salesforce opportunities, exclude
test accounts, group revenue by region, and prepare a one-page PDF for the sales VP.
```

You can attach the export, an old report, an SOP, a spreadsheet, a PDF, a
transcript, a link, or a script. Better source material produces a more useful
first version.

Other useful prompts:

```text
/agent-skill-creator Turn this monthly-close spreadsheet and the attached SOP into a reusable skill.

/agent-skill-creator Every morning I check our public GitHub dependencies for new releases and summarize what needs human review.

/agent-skill-creator --audit ./downloaded-skill/
```

## 3. Confirm the one thing only a human can decide

The creator should first summarize the workflow, input, output, evidence, and
success condition. It may ask one bounded question when a business definition,
authority, or risk boundary is unclear.

Example response:

```text
Use Billing's definition of an active customer: at least one billable event in
the previous 30 days. The Commercial Analytics owner approves this definition.
Do not send email or update Salesforce as part of the first version.
```

Expected: the agent records that decision and continues building. If no authorized
person can decide the meaning, `BLOCKED` is the correct result. Do not guess or
ask the agent to invent an approval.

## 4. Inspect the first result

The creator should report these stages:

```text
Understand  workflow and success criteria confirmed
Build       reusable skill created
Check       structure, code, security patterns, and examples checked
Try         installed and run once on representative input
```

You should receive a skill package containing instructions, executable scripts
when needed, evaluations, and maintenance records. Inspect the actual output—not
just the checkmarks—and ask:

- Does this answer the business question I started with?
- Did it use the right source and definition?
- Did it avoid production writes, sending email, purchases, or publishing?

`VERIFICATION.md` records the checks performed at generation time. It does not
prove production safety, other agent runtimes, or future user outcomes. A missing
credential, permission, or safe representative input should produce a
`verification-blocked` instruction with one specific next action.

## 5. Correct it after first use

Describe the mistake in the words you would use with a colleague:

```bash
python3 ./weekly-sales-report-skill/scripts/evolve.py \
  --correct "UK sales arrive one business day late; do not treat missing UK revenue as zero."
```

Expected: the correction becomes a proposed skill edit, an executable regression
record, and a versioned reason in `EVOLUTION.md`. Re-run verification before
requesting an updated marketplace release.

## When to involve the marketplace operator

Ask for marketplace intake only when the skill has an owner, a reviewed version,
and current verification evidence. The operator manages approval, publication,
runtime certification, version-pinned installation, rollback, quarantine, and
retirement. Follow the [team marketplace timeline](TEAM_MARKETPLACE.md) for those
commands.

## Escalate instead of proceeding when

- A credential, permission, production dataset, or consequential external action
  is required.
- The workflow owner cannot confirm a definition that affects correctness.
- The generated result contradicts the supplied source material.
- The verification report is missing, stale, or records failed checks.

In each case, preserve the evidence, name the blocked decision, and ask the
appropriate owner or operator for the one missing authorization.
