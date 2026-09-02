#!/usr/bin/env python3
"""Deterministically decide whether source reconnaissance blocks skill creation."""

from __future__ import annotations
import json
import subprocess
import sys
from pathlib import Path
from typing import Any, Mapping

STRUCTURED = {
    "api",
    "mcp-tool",
    "mcp-resource",
    "database",
    "structured-file",
    "event-stream",
    "schema-registry",
    "codebase",
}
IMPACTS = {"moderate", "high", "critical"}


def evaluate(discovery: Mapping[str, Any]) -> dict[str, Any]:
    interfaces = discovery.get("data_interfaces", {})
    if not isinstance(interfaces, Mapping) or not interfaces.get("applies"):
        return {"status": "NOT_REQUIRED", "sources": [], "reasons": []}
    recon = discovery.get("semantic_recon", {})
    sources = recon.get("sources", []) if isinstance(recon, Mapping) else []
    if not isinstance(sources, list) or not sources:
        return {
            "status": "BLOCKED_NEEDS_SCOPE",
            "sources": [],
            "reasons": ["structured source has no semantic_recon.sources declaration"],
        }
    required = []
    blocked = []
    for source in sources:
        if not isinstance(source, Mapping):
            blocked.append("source declaration must be an object")
            continue
        kind = str(source.get("type", "")).lower()
        reuse = str(source.get("reuse", "")).lower()
        impact = str(source.get("impact", "")).lower()
        if (
            kind not in STRUCTURED
            or reuse not in {"one-off", "recurring"}
            or impact not in {"low", *IMPACTS}
        ):
            blocked.append(
                f"{source.get('id', 'source')}: type, reuse and impact are required"
            )
            continue
        # Any declared external/structured source is contract-bound by default.
        # Recurrence and blast-radius metadata remain useful for prioritisation,
        # but they no longer permit silently skipping Semantic Recon.
        if kind in STRUCTURED:
            required.append(dict(source))
    if blocked:
        return {
            "status": "BLOCKED_NEEDS_SCOPE",
            "sources": required,
            "reasons": blocked,
        }
    return {
        "status": "REQUIRED" if required else "NOT_REQUIRED",
        "sources": required,
        "reasons": [],
    }


def check_contracts(decision: Mapping[str, Any]) -> list[str]:
    errors = []
    for source in decision.get("sources", []):
        path = Path(str(source.get("contract_path", ""))).expanduser()
        cid = str(source.get("contract_id", ""))
        if not cid or not path.is_dir() or not (path / ".contract_id").is_file():
            errors.append(
                f"{source.get('id', 'source')}: missing contract_path or .contract_id"
            )
            continue
        if (path / ".contract_id").read_text().strip() != cid:
            errors.append(
                f"{source.get('id', 'source')}: contract_id does not match .contract_id"
            )
        if not (path / "code" / "contract_health.py").is_file():
            errors.append(f"{source.get('id', 'source')}: missing contract_health.py")
        if errors and errors[-1].startswith(f"{source.get('id', 'source')}:"):
            continue
        probe = (
            "import importlib, json; "
            f"m=importlib.import_module({('data_contract_' + cid + '.code.contract_health')!r}); "
            "print(json.dumps(m.report()))"
        )
        completed = subprocess.run(
            [sys.executable, "-c", probe],
            cwd=path.parent,
            text=True,
            capture_output=True,
            check=False,
            timeout=30,
        )
        try:
            report = json.loads(completed.stdout) if completed.returncode == 0 else {}
        except json.JSONDecodeError:
            report = {}
        smoke = (
            report.get("smoke", report.get("smoke_test"))
            if isinstance(report, Mapping)
            else None
        )
        smoke_passed = smoke == "PASS" or (
            isinstance(smoke, Mapping) and smoke.get("status") == "PASS"
        )
        freshness = report.get("freshness") if isinstance(report, Mapping) else None
        fresh = freshness == "FRESH" or (
            isinstance(freshness, Mapping) and freshness.get("status") == "FRESH"
        )
        healthy = (
            isinstance(report, Mapping)
            and fresh
            and (report.get("usable") is True or smoke_passed)
        )
        if not healthy:
            detail = (
                completed.stderr or completed.stdout or "no valid health report"
            ).strip()
            errors.append(
                f"{source.get('id', 'source')}: contract health is not passing ({detail[:300]})"
            )
    return errors


def load(path: str | Path) -> dict[str, Any]:
    return json.loads(Path(path).read_text(encoding="utf-8"))
