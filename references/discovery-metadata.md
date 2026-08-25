# Marketplace discovery metadata

Every generated skill includes `discovery.json`. The file describes the job a user
can complete, not implementation keywords. The governed marketplace validates it,
uses it for outcome-first search, and generates a structured skill page.

```json
{
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

- `outcome` states the inspectable result the skill produces.
- Each example invocation begins with the exact `/skill-name`.
- `permissions_systems` names concrete access rather than saying “standard access.”
- `support_tier` is `supported`, `community`, or `deprecated`.
- `compatibility.declared` uses canonical names from `scripts/platforms.py`.
- `compatibility.certified` is empty at creation. Only the governed marketplace
  writes certification after explicit current-version checks pass.
