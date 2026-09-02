#!/usr/bin/env python3
"""Run the deterministic Semantic Recon portion of factory Phase 1."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from emit_semantic_recon_sources import emit
from semantic_recon_orchestrator import orchestrate


def run(skill_dir: str | Path, runner: str | None = None) -> dict:
    """Emit source scope, then resume only when required contracts are healthy."""
    root = Path(skill_dir)
    discovery = root / "discovery.json"
    if not discovery.is_file():
        return {"status": "BLOCKED_NO_DISCOVERY", "detail": str(discovery)}
    emit(discovery)
    return orchestrate(root, runner)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("skill_dir")
    parser.add_argument("--runner")
    args = parser.parse_args()
    print(json.dumps(run(args.skill_dir, args.runner), indent=2))
