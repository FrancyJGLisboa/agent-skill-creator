# Marketplace discovery metadata

Every generated skill includes `discovery.json`. The file describes the job a user
can complete, not implementation keywords. The governed marketplace validates it,
uses it for outcome-first search, and generates a structured skill page.

```json
{
  "question": "Why did monthly revenue deviate from plan?",
  "trigger": ["Monthly close data is available", "Revenue deviates from plan"],
  "decision": ["Escalate a material variance", "Accept the reported result"],
  "evidence": ["Revenue ledger", "Approved operating plan"],
  "success_measure": "Every material variance has an evidence-backed owner and action",
  "outcome": "Prepare a monthly revenue review for leadership",
  "intended_users": ["finance analysts", "revenue leaders"],
  "input_types": ["CSV", "spreadsheet"],
  "output_artifacts": ["executive Markdown report"],
  "use_cases": ["monthly close", "board reporting"],
  "examples": [
    {
      "invocation": "/revenue-review-skill revenue.csv",
      "description": "Review one month of revenue"
    }
  ],
  "permissions_systems": ["Read local input files", "No network access"],
  "typical_completion_time": "2-5 minutes",
  "compatibility": {
    "declared": ["codex", "cursor"],
    "certified": []
  },
  "support_tier": "supported"
}
```

Rules:

- `question` is the consequential question the skill helps a user answer.
- `trigger` names observable situations in which that question should be asked.
- `decision` names the actions or choices the result can support.
- `evidence` names the inputs required to justify the answer.
- `success_measure` states an observable measure of decision quality or outcome.
- All five decision-contract fields are required and must be non-empty. `trigger`,
  `decision`, and `evidence` are arrays of concrete statements.
- `outcome` states the inspectable result the skill produces.
- Each example invocation begins with the exact `/skill-name`.
- `permissions_systems` names concrete access rather than saying “standard access.”
- `support_tier` is `supported`, `community`, or `deprecated`.
- `compatibility.declared` uses canonical names from `scripts/platforms.py`.
- `compatibility.certified` is empty at creation. Only the governed marketplace
  writes certification after explicit current-version checks pass.

## Organizational metadata

`owners` and `approval_status` belong in `SKILL.md` metadata, not `discovery.json`.
When the user names a target governed marketplace, read its published governance and
use the exact assigned owner identities and intake status. These values make the
generated package submission-ready for that specific marketplace.

When there is no known target marketplace, do not invent an organization, department,
owner, approver, or approval status. Marketplace intake is the authority that assigns
those values. Compatibility certification follows the same boundary: creation may
declare compatibility, but only marketplace verification may certify it.
