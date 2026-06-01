#!/usr/bin/env python3
"""Deterministic entry-point for the pr-blocker-summarizer skill.

Reads a JSON array of open PRs, classifies each as blocked or ready, and writes a
blockers-first digest. Stdlib-only.

    python3 scripts/run_pipeline.py --input prs.json --output digest.json
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

STALE_DAYS = 7


def blockers_for(pr: dict) -> list[str]:
    """Return the list of reasons a PR is blocked (empty list = not blocked)."""
    reasons: list[str] = []
    if pr.get("checks") == "failing":
        reasons.append("failing checks")
    if pr.get("review") == "changes_requested":
        reasons.append("changes requested")
    if pr.get("review") == "pending":
        reasons.append("awaiting review")
    try:
        if int(pr.get("age_days", 0)) >= STALE_DAYS:
            reasons.append(f"stale ({pr['age_days']}d)")
    except (TypeError, ValueError):
        pass
    return reasons


def summarize(prs: list[dict]) -> dict:
    """Split PRs into blocked vs. ready and build a one-line summary."""
    blocked: list[dict] = []
    ready: list[str] = []
    for pr in prs:
        title = pr.get("title", "(untitled)")
        reasons = blockers_for(pr)
        if reasons:
            blocked.append({"title": title, "reasons": reasons})
        elif pr.get("checks") == "passing" and pr.get("review") == "approved":
            ready.append(title)
    return {
        "total": len(prs),
        "blocked": blocked,
        "ready": ready,
        "summary": f"{len(prs)} open · {len(blocked)} blocked · {len(ready)} ready to merge",
    }


def run_pipeline(input_path: Path, output_path: Path) -> Path:
    """Read the PR JSON array, build the digest, write JSON. Return output path."""
    prs = json.loads(input_path.read_text(encoding="utf-8"))
    if not isinstance(prs, list):
        raise ValueError("input must be a JSON array of pull requests")
    output_path.write_text(json.dumps(summarize(prs), indent=2), encoding="utf-8")
    return output_path


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Summarize open PRs into a digest.")
    parser.add_argument("--input", required=True, help="JSON array of PRs.")
    parser.add_argument("--output", required=True, help="Where to write digest JSON.")
    args = parser.parse_args(argv)
    try:
        run_pipeline(Path(args.input), Path(args.output))
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(json.dumps({"error": str(exc), "error_type": "runtime"}), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
