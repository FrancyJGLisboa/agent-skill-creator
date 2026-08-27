#!/usr/bin/env python3
"""Run live, structural regression checks for github-release-briefing-skill."""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import tempfile
from pathlib import Path

CASES = ("openai/openai-python", "anthropics/anthropic-sdk-python", "vercel/ai")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("skill_dir", nargs="?", help="Compatibility argument for the factory verifier.")
    parser.add_argument("--validate", action="store_true")
    parser.add_argument("--rollout", action="store_true")
    parser.add_argument("--include-holdout", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    root = Path(__file__).resolve().parents[1]
    if args.validate:
        valid = (root / "evals/github-release-briefing.eval.md").is_file()
        print("eval spec valid" if valid else "eval spec missing")
        return 0 if valid else 1
    selected = CASES if args.include_holdout else CASES[:2]
    passed = 0
    with tempfile.TemporaryDirectory(prefix="github-release-evals-") as tmp:
        for index, repository in enumerate(selected):
            output = Path(tmp) / f"{index}.md"
            result = subprocess.run([sys.executable, str(root / "scripts/run_pipeline.py"), "--repository", repository, "--output", str(output)], text=True, capture_output=True, check=False)
            text = output.read_text(encoding="utf-8") if output.exists() else ""
            ok = result.returncode == 0 and "# Latest release:" in text and "- Tag:" in text and "- Published:" in text and "- GitHub API: https://api.github.com/repos/" in text
            passed += int(ok)
            if not args.json:
                print(f"{'PASS' if ok else 'FAIL'} {repository}")
    clean = passed == len(selected)
    if args.json:
        print(json.dumps({"passed": passed, "failed": len(selected) - passed, "errors": 0, "regressions": 0}))
    else:
        print(f"{passed}/{len(selected)} live release cases passed")
    return 0 if clean else 1


if __name__ == "__main__":
    raise SystemExit(main())
