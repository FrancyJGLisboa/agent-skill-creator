# Marketplace discovery metadata

Every generated skill includes `discovery.json`. The file describes the job a user
can complete, not implementation keywords. The governed marketplace validates it,
uses it for outcome-first search, and generates a structured skill page.

Every factory-generated skill also preserves the ready `interview.json` that produced
this contract. The interview is the evidence and authority trail; `discovery.json` is
the compiled marketplace representation. Do not ask users to author either schema.
Use `scripts/structured_interview.py` and read `references/structured-interview.md`.

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
  "environment": {
    "documentation_sources": ["Finance API OpenAPI document at the configured URL"],
    "data_sources": ["Monthly revenue CSV supplied by the user"],
    "required_capabilities": ["Read local CSV files"],
    "readiness_checks": ["The input exists and contains the required columns"]
  },
  "risk": {
    "tier": "low",
    "permissions": ["Read the user-supplied CSV"],
    "mutation_boundary": "read-only",
    "approval_required": []
  },
  "software_mutation": {
    "applies": false
  },
  "data_interfaces": {
    "applies": true,
    "interface_types": ["structured-file"],
    "authoritative_sources": ["Approved revenue CSV schema"],
    "entities": ["Revenue record"],
    "identifiers": ["Revenue record.id"],
    "relationships": ["Revenue record.account_id identifies the owning account"],
    "field_semantics": ["amount is decimal currency in account currency"],
    "invariants": ["Every record has one account_id"],
    "freshness_and_pagination": ["One complete monthly snapshot; no pagination"],
    "nullability": ["amount and account_id are required"],
    "readiness_checks": ["One safe sample matches the approved schema"]
  },
  "semantic_contract": {
    "applies": true,
    "definitions": [{
      "id": "recognized-revenue",
      "version": "1.0.0",
      "definition": "Revenue recognized under the approved finance policy",
      "scope": "Monthly management reporting",
      "grain": "revenue_record_id",
      "unit": "account currency",
      "source_precedence": ["approved revenue ledger", "CRM opportunity"],
      "owner": "commercial-analytics",
      "valid_from": "2026-07-01",
      "last_reviewed": "2026-08-18",
      "review_interval_days": 30
    }],
    "dependencies": [{"id": "recognized-revenue", "version": "1.0.0"}],
    "ambiguity": {
      "allowed_outcomes": ["answer", "ask", "refuse_unknown"],
      "unresolved_action": "ask",
      "clarification": "Do you mean recognized revenue or CRM pipeline value?"
    }
  },
  "routing_tests": {
    "should_trigger": ["Review monthly revenue", "Why did revenue miss plan?", "Prepare the revenue variance review"],
    "should_not_trigger": ["Write a sales email", "Forecast next year's hiring", "Delete the revenue ledger"]
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
- `environment` names the documentation, data, capabilities, and blocking readiness
  checks the skill must inspect before useful work. Use explicit `None required`
  entries when a category genuinely has no dependency; never omit the category.
- `risk` declares least-privilege access and the mutation boundary. Low-risk skills
  are read-only. High- and critical-risk mutations must name their approval gate.
- `software_mutation.applies` is required. Set it to `true` only when the skill
  creates or changes application code, schemas, models, persistence, serialization,
  caches, synchronization, migrations, or stateful features. A true value requires a
  representation review before implementation:

```json
{
  "software_mutation": {
    "applies": true,
    "affected_structures": ["Seat", "SeatState"],
    "invariants": ["A seat has exactly one state"],
    "sources_of_truth": ["Seat state: Seat.state"],
    "invalid_states_prevented": ["A seat cannot be held and sold simultaneously"],
    "state_transitions": ["open -> held", "held -> open", "held -> sold"]
  }
}
```

  Each review list must be non-empty. Missing invariants block implementation. Keep
  derived values derived rather than declaring another source of truth. For a
  non-software workflow, use only `{"applies": false}`; do not invent structures.
- `data_interfaces.applies` is required. Set it to `true` when the skill consumes an
  API, MCP tool/resource, database, structured file, event stream, or schema registry.
  Allowed interface types are `api`, `mcp-tool`, `mcp-resource`, `database`,
  `structured-file`, `event-stream`, and `schema-registry`. A true value requires
  non-empty `authoritative_sources`, `entities`, `identifiers`, `relationships`,
  `field_semantics`, `invariants`, `freshness_and_pagination`, `nullability`, and
  `readiness_checks`. Inspect authoritative documentation and one safe representative
  sample when accessible. A connection or successful authentication does not prove
  semantic readiness. Unresolved field meaning, identity, or relationship ambiguity
  blocks useful execution. For unstructured inputs with no structured interface, use
  only `{"applies": false}`.
- `semantic_contract.applies` is required. Set it to `true` when correctness depends
  on organizational meaning, source precedence, business scope, grain, units, or time
  interpretation. Each definition has a safe ID, exact semantic version, human owner,
  ordered sources, validity date, review date, and positive review interval. Declare
  exact dependencies and all three legitimate outcomes: `answer`, `ask`, and
  `refuse_unknown`. Unresolved meaning must ask a declared clarification or refuse;
  it must never silently choose. Use only `{"applies": false}` when no organizational
  interpretation is required. Marketplace release checks block overdue definitions.
- `routing_tests` supplies at least three positive and three negative queries for
  portfolio coexistence evaluation.

## Organizational metadata

`owners` and `approval_status` belong in `SKILL.md` metadata, not `discovery.json`.
When the user names a target governed marketplace, read its published governance and
use the exact assigned owner identities and intake status. These values make the
generated package submission-ready for that specific marketplace.

When there is no known target marketplace, do not invent an organization, department,
owner, approver, or approval status. Marketplace intake is the authority that assigns
those values. Compatibility certification follows the same boundary: creation may
declare compatibility, but only marketplace verification may certify it.
