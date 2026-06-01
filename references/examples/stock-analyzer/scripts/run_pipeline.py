#!/usr/bin/env python3
"""Deterministic entry-point for the stock-analyzer skill.

Wires the skill's happy path into a single command so an agent (or the eval
rollout harness) runs ONE command instead of sequencing calls from prose:

    python3 scripts/run_pipeline.py --input <case.json> --output <result.json>

The input is a small JSON request: {"ticker": "AAPL", "indicators": ["RSI", "MACD"]}.
The output is the analysis result as JSON. This wrapper is stdlib-only — it drives
the bundled StockAnalyzer (itself a dependency-free reference implementation), so
the eval rollout runs without installing yfinance/pandas/ta-lib.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

# Running this file puts its own directory (scripts/) on sys.path[0], so the
# sibling module imports directly.
from main import StockAnalyzer  # noqa: E402


def run_pipeline(input_path: Path, output_path: Path) -> Path:
    """Read a JSON request, run the analysis, write the result JSON. Return out."""
    request = json.loads(input_path.read_text(encoding="utf-8"))
    ticker = request.get("ticker")
    if not ticker:
        raise ValueError("input request must include a 'ticker'")
    indicators = request.get("indicators") or ["RSI", "MACD"]

    analyzer = StockAnalyzer()
    result = analyzer.analyze(ticker, indicators)

    output_path.write_text(json.dumps(result, indent=2), encoding="utf-8")
    return output_path


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run the stock-analyzer happy path.")
    parser.add_argument("--input", required=True, help="JSON request file (ticker + indicators).")
    parser.add_argument("--output", required=True, help="Where to write the result JSON.")
    args = parser.parse_args(argv)

    try:
        run_pipeline(Path(args.input), Path(args.output))
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(json.dumps({"error": str(exc), "error_type": "runtime"}), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
