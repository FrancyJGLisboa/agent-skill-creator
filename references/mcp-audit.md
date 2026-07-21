# MCP Capability Audit — the `--mcp-audit` front door

The user pays a data vendor whose product is exposed as an MCP server, and wants
to know **which skills can be built on top of it — and which cannot**. That is a
different job from building a skill: the deliverable is a *feasibility map*, not
code. This front door produces it, gated by a deterministic validator so the map
cannot be hand-waved.

Fire this when the input carries `--mcp-audit`, or naturally:

- "We pay for data from vendor X, exposed via their MCP — what skills can we build on it?"
- "Audit this MCP server: <url / repo / docs>"
- "What is and isn't possible on top of <vendor>'s MCP?"

Input is one of: a **live MCP connection** (best), the **server's repo**, or its
**docs**. If the user gives only marketing pages, stop and ask for one of the
three — an audit without a tool inventory is fiction.

## The constraint that decides "possible vs not" (read first)

MCP tools are invoked by the **agent host**, not by arbitrary code. The factory's
generated `run_pipeline.py` scripts run as plain subprocesses — **they cannot
call MCP tools at runtime**. So every buildable candidate falls in one of two
classes, and the audit must say which:

- **`agent`-orchestrated** — the SKILL.md instructs the agent to call the
  vendor's MCP tools and compose their outputs. Deterministic scripts may still
  post-process files the agent hands over. This is the natural fit for MCP.
- **`script`-orchestrated** — the pipeline needs data at script-time, which MCP
  cannot provide. Only buildable if the candidate declares a real non-MCP data
  path: `rest` (vendor also has a REST API), `export` (bulk files), or
  `agent-handoff` (agent fetches via MCP, writes files, scripts consume them).

Corollary for evals: golden-case rollouts of agent-orchestrated skills need
**recorded MCP fixtures**, not live calls. Flag this in each candidate's notes.

## Procedure

### 1 — Enumerate (provenance, not summary)

- Live connection: call `tools/list`, `resources/list`, `prompts/list`. Embed
  the **raw `tools/list` JSON verbatim** in the report as
  `inventory.raw_tools_list`.
- Repo only: locate every tool registration in the source and record
  `inventory.static_evidence` as `{tool, file, line}` citations.
- Never build the inventory from prose docs alone — docs describe intent;
  the registered tools are the truth.

### 2 — Map the data surface

Per tool: inputs (from the schema), outputs, granularity (per-symbol? daily?
historical depth?), and limits (rate, pagination, auth scope) from docs. This
table is what feasibility verdicts cite.

### 3 — Harvest candidate workflows

Cross the surface with the user's *real recurring work* — reuse the Phase 0
harvest discipline (`references/spec-ideation.md`): never invent chores, prefer
the boring weekly task over the clever idea. If the user hasn't named workflows,
ask for their recurring vendor-data tasks before ranking anything.

### 4 — Split: buildable vs not-buildable

- **Buildable**: every pipeline step maps to a named inventory tool or is an
  explicit `local` step; at least one step uses an MCP tool; orchestration
  class assigned per the constraint above. Rank by value-to-effort — ranks
  must be unique; ties dodge the prioritization the user is paying for.
- **Not buildable**: name the **exact missing primitive** (field, endpoint,
  granularity, history depth, rate ceiling) and cite the *closest existing
  tool* (or null). "Insufficient data" is not a verdict; it is the failure
  mode this audit exists to prevent.

### 5 — Write the two outputs and gate them

1. `mcp_audit.json` — the machine-checkable report (schema below).
2. `MCP_AUDIT.md` — the human version: surface map, ranked buildable list with
   per-step tool mapping, not-buildable list with named gaps.

Then run the gate and fix findings until it exits 0:

```bash
python3 scripts/mcp_audit_validate.py mcp_audit.json
```

### 6 — Hand off

The user picks a buildable candidate → it enters Phase 1 as a normal build,
with the audit's tool mapping as the discovery evidence.

## Report schema (`mcp_audit.json`)

```json
{
  "server": {"name": "vendor-data", "source": "https://mcp.vendor.example"},
  "inventory": {
    "raw_tools_list": { "tools": [ {"name": "query_prices", "inputSchema": {}},
                                   {"name": "list_symbols", "inputSchema": {}} ] },
    "tools": [ {"name": "query_prices", "description": "EOD prices by symbol"},
               {"name": "list_symbols", "description": "Symbol universe"} ]
  },
  "buildable": [
    {
      "skill_name": "daily-price-brief",
      "rank": 1,
      "orchestration": "agent",
      "steps": [
        {"step": "fetch prices", "tool": "query_prices"},
        {"step": "format brief", "local": true}
      ]
    },
    {
      "skill_name": "symbol-coverage-report",
      "rank": 2,
      "orchestration": "script",
      "data_access": "export",
      "steps": [ {"step": "pull universe", "tool": "list_symbols"} ]
    }
  ],
  "not_buildable": [
    {
      "idea": "intraday tick alerting",
      "missing_primitive": "no tool exposes intraday data; query_prices is EOD only",
      "closest_tool": "query_prices"
    }
  ],
  "holdout": {
    "procedure": "human spot-checks 3 random buildable mappings against vendor docs"
  }
}
```

Static-audit variant: replace `raw_tools_list` with
`"static_evidence": [ {"tool": "query_prices", "file": "src/server.ts", "line": 42} ]`.

## What the validator enforces (and what it deliberately doesn't)

| # | Check | Kills |
|---|---|---|
| C1 | Inventory matches raw `tools/list` / static citations exactly | docs-summarized or curated inventories |
| C2 | Every buildable step names a real tool or is explicit `local`; ≥1 MCP step; unique ranks | hallucinated tool names, padding |
| C3 | Every not-buildable names the missing primitive + closest real tool | vague "insufficient data" refusals |
| C4 | Orchestration classified; `script` requires `rest`/`export`/`agent-handoff` | promising script pipelines MCP can't feed |
| C5 | Holdout block exists — content **never graded** by the validator | the loop optimizing against 100% of its checks |

C5 is the held-out check: a human spot-checks 3 randomly chosen buildable
mappings against the vendor's docs. The audit loop never sees or grades that
step — it is the defense that survives after every machine check is satisfied.
