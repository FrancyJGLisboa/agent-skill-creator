#!/usr/bin/env python3
"""
Validator for --mcp-audit reports (mcp_audit.json).

The MCP capability audit answers "which skills can we build on this vendor's
MCP server, and which can we not". This gate makes the answer accountable:

  C1  Inventory provenance — every tool in the report exists in the embedded
      raw tools/list output (live audit) or in cited code evidence (static
      audit). No summarized-from-docs inventories.
  C2  Every buildable candidate maps each step to a named inventory tool or
      declares it an explicit local step, and uses at least one MCP tool.
      Kills hallucinated tool names.
  C3  Every not-buildable verdict names the specific missing primitive and
      cites the closest existing tool (or null). Kills vague "insufficient
      data" refusals.
  C4  Every candidate is classified agent- or script-orchestrated. Scripts
      cannot call MCP tools at runtime, so script-orchestrated candidates
      must declare a non-MCP data path (rest / export / agent-handoff).
  C5  A human-holdout block exists. Its content is deliberately NOT graded
      here — the holdout is the check the loop never optimizes against.

Usage:
    python3 scripts/mcp_audit_validate.py <mcp_audit.json> [--json]

Exit codes: 0 valid, 1 findings, 2 unreadable input.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

ORCHESTRATION_MODES = {"agent", "script"}
SCRIPT_DATA_ACCESS = {"rest", "export", "agent-handoff"}
# Verdicts that name nothing are the exact failure C3 exists to catch.
VAGUE_PRIMITIVES = {
    "insufficient data",
    "not possible",
    "not supported",
    "no data",
    "unavailable",
}


def _err(message: str, detail: str = "") -> dict:
    return {"level": "error", "message": message, "detail": detail}


def _inventory_tool_names(inventory: dict) -> tuple[set[str], list[dict]]:
    """Return (declared tool names, provenance issues) for C1."""
    issues: list[dict] = []
    declared = {
        t.get("name", "") for t in inventory.get("tools", []) if t.get("name")
    }

    raw = inventory.get("raw_tools_list")
    static = inventory.get("static_evidence")
    if raw is not None:
        source = {t.get("name", "") for t in raw.get("tools", []) if t.get("name")}
    elif static is not None:
        source = {e.get("tool", "") for e in static if e.get("tool")}
        for entry in static:
            if not (entry.get("file") and entry.get("line")):
                issues.append(_err(
                    f"static_evidence for '{entry.get('tool', '?')}' lacks file/line",
                    "Static audits must cite where each tool is registered.",
                ))
    else:
        issues.append(_err(
            "inventory has no provenance",
            "Embed the raw tools/list result (live audit) or static_evidence "
            "with file/line citations (repo audit).",
        ))
        return declared, issues

    if not declared and not source:
        issues.append(_err(
            "inventory is empty",
            "An audit of a server with zero tools is not an audit; "
            "record why enumeration returned nothing instead.",
        ))
    for name in sorted(declared - source):
        issues.append(_err(
            f"inventory tool '{name}' is not in the provenance source",
            "Every reported tool must appear verbatim in tools/list or static evidence.",
        ))
    for name in sorted(source - declared):
        issues.append(_err(
            f"provenance tool '{name}' is missing from the inventory",
            "The inventory must be complete, not a curated subset.",
        ))
    return declared, issues


def _check_buildable(candidates: list[dict], tools: set[str]) -> list[dict]:
    """C2 + C4: step→tool mapping, orchestration classification, unique ranks."""
    issues: list[dict] = []
    ranks: list = []
    for cand in candidates:
        name = cand.get("skill_name", "?")
        ranks.append(cand.get("rank"))

        uses_mcp = False
        for step in cand.get("steps", []):
            tool = step.get("tool")
            if tool:
                if tool in tools:
                    uses_mcp = True
                else:
                    issues.append(_err(
                        f"'{name}' step names unknown tool '{tool}'",
                        "Every step's tool must exist in the audited inventory.",
                    ))
            elif not step.get("local"):
                issues.append(_err(
                    f"'{name}' step '{step.get('step', '?')}' names no tool and is not local",
                    "Each step either calls a named MCP tool or is an explicit local step.",
                ))
        if not uses_mcp:
            issues.append(_err(
                f"'{name}' uses no MCP tool in any step",
                "A candidate with no MCP dependency does not belong in an MCP audit.",
            ))

        mode = cand.get("orchestration")
        if mode not in ORCHESTRATION_MODES:
            issues.append(_err(
                f"'{name}' has invalid or missing orchestration '{mode}'",
                f"Must be one of: {', '.join(sorted(ORCHESTRATION_MODES))}.",
            ))
        elif mode == "script" and cand.get("data_access") not in SCRIPT_DATA_ACCESS:
            issues.append(_err(
                f"'{name}' is script-orchestrated without a valid data_access",
                "Scripts cannot call MCP tools at runtime; declare one of: "
                f"{', '.join(sorted(SCRIPT_DATA_ACCESS))}.",
            ))

    if len(ranks) != len(set(ranks)):
        issues.append(_err(
            "buildable ranks are not unique",
            "Ranking is the deliverable; ties dodge the prioritization.",
        ))
    return issues


def _check_not_buildable(verdicts: list[dict], tools: set[str]) -> list[dict]:
    """C3: named missing primitive, closest tool grounded in inventory."""
    issues: list[dict] = []
    for verdict in verdicts:
        idea = verdict.get("idea", "?")
        primitive = (verdict.get("missing_primitive") or "").strip()
        if not primitive or primitive.lower() in VAGUE_PRIMITIVES:
            issues.append(_err(
                f"'{idea}' has an empty or vague missing_primitive",
                "Name the exact missing field/endpoint/granularity, "
                "not a generic refusal.",
            ))
        closest = verdict.get("closest_tool")
        if closest is not None and closest not in tools:
            issues.append(_err(
                f"'{idea}' cites closest_tool '{closest}' not in the inventory",
                "closest_tool must be a real audited tool, or null if none is close.",
            ))
    return issues


def validate_report(report: dict) -> list[dict]:
    """Validate an mcp_audit.json dict. Returns a list of issue dicts."""
    issues: list[dict] = []

    tools, inventory_issues = _inventory_tool_names(report.get("inventory", {}))
    issues.extend(inventory_issues)
    issues.extend(_check_buildable(report.get("buildable", []), tools))
    issues.extend(_check_not_buildable(report.get("not_buildable", []), tools))

    holdout = report.get("holdout") or {}
    if not (holdout.get("procedure") or "").strip():
        issues.append(_err(
            "holdout block is missing or has no procedure",
            "Describe the human spot-check that the audit loop never grades itself.",
        ))
    return issues


def main() -> int:
    args = [a for a in sys.argv[1:] if a != "--json"]
    use_json = "--json" in sys.argv[1:]
    if len(args) != 1:
        print(__doc__, file=sys.stderr)
        return 2

    path = Path(args[0])
    try:
        report = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"Error reading {path}: {exc}", file=sys.stderr)
        return 2

    issues = validate_report(report)
    if use_json:
        print(json.dumps({"valid": not issues, "issues": issues}, indent=2))
    else:
        if issues:
            print(f"MCP audit report FAILED {len(issues)} check(s):")
            for issue in issues:
                print(f"  [ERROR] {issue['message']}")
                if issue["detail"]:
                    print(f"          {issue['detail']}")
        else:
            print("MCP audit report: all checks passed.")
    return 1 if issues else 0


if __name__ == "__main__":
    raise SystemExit(main())
