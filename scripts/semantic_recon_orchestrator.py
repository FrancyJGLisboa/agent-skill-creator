#!/usr/bin/env python3
"""Resume a skill build only after required Semantic Recon contracts are healthy.

The configured runner receives ``--source-json`` and ``--result-json``.  Its result
must name a PASS/PASS_WITH_UNRESOLVED_ITEMS contract; this keeps agent execution
outside this deterministic coordinator while making its handoff machine-checkable.
"""

from __future__ import annotations
import argparse
import json
import os
import shlex
import subprocess
import tempfile
from pathlib import Path
from typing import Any
from semantic_recon_gate import check_contracts, evaluate

PASS = {"PASS", "PASS_WITH_UNRESOLVED_ITEMS"}


def orchestrate(skill_dir: str | Path, runner: str | None = None) -> dict[str, Any]:
    root = Path(skill_dir)
    path = root / "discovery.json"
    discovery = json.loads(path.read_text())
    decision = evaluate(discovery)
    if decision["status"] == "NOT_REQUIRED":
        return {"status": "RESUMED", "reason": "Semantic Recon not required"}
    if decision["status"] != "REQUIRED":
        return {"status": "BLOCKED", "reasons": decision["reasons"]}
    if runner is None:
        runner = (
            os.environ.get("SEMANTIC_RECON_RUNNER")
            or f"{os.sys.executable} {Path(__file__).with_name('semantic_recon_runner.py')}"
        )
    pending = check_contracts(decision)
    if pending and not runner:
        return {"status": "BLOCKED_NO_RUNNER", "reasons": pending}
    for source in decision["sources"]:
        if source.get("contract_path") and not check_contracts({"sources": [source]}):
            continue
        with tempfile.TemporaryDirectory() as temp:
            source_path = Path(temp) / "source.json"
            result_path = Path(temp) / "result.json"
            source_path.write_text(json.dumps(source))
            command = shlex.split(runner) + [
                "--source-json",
                str(source_path),
                "--result-json",
                str(result_path),
            ]
            completed = subprocess.run(
                command, capture_output=True, text=True, check=False
            )
            if not result_path.exists():
                return {
                    "status": "BLOCKED_RUNNER_FAILED",
                    "source": source["id"],
                    "detail": completed.stderr or completed.stdout,
                }
            result = json.loads(result_path.read_text())
        if result.get("status") not in PASS:
            return {
                "status": "BLOCKED_CONTRACT",
                "source": source["id"],
                "detail": result,
            }
        source["contract_id"] = result.get("contract_id")
        source["contract_path"] = result.get("contract_path")
        # Keep a successful recon handoff even if a subsequent deterministic
        # health gate blocks resumption.  A repaired contract can then resume
        # without paying for a duplicate live reconnaissance run.
        discovery.setdefault("semantic_recon", {})["sources"] = decision["sources"]
        path.write_text(json.dumps(discovery, indent=2) + "\n")
    errors = check_contracts(decision)
    if errors:
        return {"status": "BLOCKED_CONTRACT", "reasons": errors}
    # Re-evaluate the factory's blocking graph before handing control back.
    from skill_graph import build_graph, check_graph

    graph = check_graph(build_graph(root))
    if not graph["valid"]:
        return {
            "status": "BLOCKED_GRAPH",
            "sources": decision["sources"],
            "graph_errors": graph["errors"],
        }
    return {"status": "RESUMED", "sources": decision["sources"]}


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("skill_dir")
    parser.add_argument("--runner")
    args = parser.parse_args()
    print(json.dumps(orchestrate(args.skill_dir, args.runner), indent=2))
