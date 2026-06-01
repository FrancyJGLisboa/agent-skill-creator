#!/usr/bin/env python3
"""Deterministic entry-point for the weekly-crm-report skill.

Reads a CRM-export CSV, drops exact-duplicate rows, totals `amount` per `region`,
and writes a JSON summary. Stdlib-only — runs with no third-party dependencies, so
the eval rollout works out of the box.

    python3 scripts/run_pipeline.py --input export.csv --output summary.json
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path


def summarize(rows: list[dict]) -> dict:
    """Dedup identical rows, total `amount` per `region`, return the summary dict."""
    seen: set[tuple] = set()
    deduped: list[dict] = []
    for row in rows:
        key = tuple(sorted(row.items()))
        if key not in seen:
            seen.add(key)
            deduped.append(row)

    regions: dict[str, float] = {}
    for row in deduped:
        region = (row.get("region") or "").strip()
        if not region:
            continue
        try:
            amount = float(row.get("amount", "") or 0)
        except ValueError:
            amount = 0.0
        regions[region] = round(regions.get(region, 0.0) + amount, 2)

    return {
        "rows_in": len(rows),
        "rows_after_dedup": len(deduped),
        "regions": regions,
        "grand_total": round(sum(regions.values()), 2),
    }


def run_pipeline(input_path: Path, output_path: Path) -> Path:
    """Read the CSV, build the summary, write JSON. Return the output path."""
    with input_path.open(newline="", encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))
    output_path.write_text(json.dumps(summarize(rows), indent=2), encoding="utf-8")
    return output_path


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Summarize a weekly CRM export.")
    parser.add_argument("--input", required=True, help="CRM export CSV.")
    parser.add_argument("--output", required=True, help="Where to write summary JSON.")
    args = parser.parse_args(argv)
    try:
        run_pipeline(Path(args.input), Path(args.output))
    except (OSError, ValueError) as exc:
        print(json.dumps({"error": str(exc), "error_type": "runtime"}), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
