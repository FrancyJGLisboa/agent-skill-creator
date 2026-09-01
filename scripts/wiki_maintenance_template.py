#!/usr/bin/env python3
"""Persistent knowledge maintenance shipped with generated skills.

This tool deliberately does *not* edit SKILL.md. It keeps the evidence and
learning record separate from executable instructions:

    raw/                 immutable local copies of run evidence
    wiki/patterns/       draft, evidence-linked observations
    wiki/skill-impact.md validation decisions for candidate changes

Use an LLM or a reviewer to turn a draft pattern into one atomic skill change,
then use scripts/run_evals.py to decide whether that change is accepted.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path


SAFE_ID = re.compile(r"^[a-z0-9][a-z0-9-]{0,62}$")


def stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def root_for(script: Path) -> Path:
    return script.resolve().parent.parent


def require_id(value: str, label: str) -> str:
    if not SAFE_ID.fullmatch(value):
        raise ValueError(f"{label} must be lowercase kebab-case (1-63 characters)")
    return value


def initialize(root: Path) -> list[str]:
    """Create the wiki layout without replacing any existing knowledge."""
    files = {
        "wiki/index.md": "# Pattern index\n\nEvidence-linked draft patterns for skill maintenance. Do not load this file at runtime.\n\n## Patterns\n\nNone recorded.\n",
        "wiki/logs.md": "# Wiki maintenance log\n\nAppend-only record of pattern maintenance.\n",
        "wiki/skill-impact.md": "# Skill impact ledger\n\nCandidate changes are recorded here after validation. A rejected change is knowledge, not an active skill update.\n",
        "wiki/README.md": "# Maintenance wiki\n\nThis directory is for maintainers and proposers only. Runtime agents receive approved skill files, not this wiki.\n\nLifecycle: `raw evidence → draft pattern → atomic candidate → eval/security gate → accepted or rejected ledger entry`.\n",
    }
    (root / "raw").mkdir(exist_ok=True)
    (root / "wiki" / "patterns").mkdir(parents=True, exist_ok=True)
    made = []
    for relative, content in files.items():
        path = root / relative
        if not path.exists():
            path.write_text(content, encoding="utf-8")
            made.append(relative)
    return made


def capture(root: Path, source: Path, classification: str) -> str:
    if classification not in {"public", "internal", "restricted"}:
        raise ValueError("classification must be public, internal, or restricted")
    if not source.is_file():
        raise ValueError(f"source is not a file: {source}")
    initialize(root)
    payload = source.read_bytes()
    digest = hashlib.sha256(payload).hexdigest()
    suffix = source.suffix if source.suffix else ".txt"
    target = root / "raw" / f"{stamp().replace(':', '')}-{digest[:12]}{suffix}"
    if not target.exists():
        shutil.copyfile(source, target)
        target.chmod(0o444)
    manifest = target.with_suffix(target.suffix + ".json")
    manifest.write_text(json.dumps({
        "captured_at": stamp(), "source_name": source.name,
        "sha256": digest, "classification": classification,
        "immutable_copy": target.name,
    }, indent=2) + "\n", encoding="utf-8")
    manifest.chmod(0o444)
    return target.relative_to(root).as_posix()


def add_pattern(root: Path, pattern_id: str, title: str, finding: str, evidence: list[str]) -> str:
    require_id(pattern_id, "pattern id")
    if not title.strip() or not finding.strip():
        raise ValueError("title and finding must not be empty")
    initialize(root)
    normalized = []
    for item in evidence:
        path = Path(item)
        if path.is_absolute() or path.parts[:1] != ("raw",) or not (root / path).is_file():
            raise ValueError(f"evidence must name an existing raw/ file: {item}")
        normalized.append(path.as_posix())
    if not normalized:
        raise ValueError("at least one --evidence raw/... file is required")
    path = root / "wiki" / "patterns" / f"{pattern_id}.md"
    if path.exists():
        raise ValueError(f"pattern already exists: {path.relative_to(root)}")
    path.write_text(
        f"# {title.strip()}\n\n"
        f"Status: draft — not executable guidance.\n\n"
        f"## Finding\n\n{finding.strip()}\n\n"
        "## Evidence\n\n" + "".join(f"- `{item}`\n" for item in normalized) +
        "\n## Proposed next experiment\n\nDefine one atomic candidate change and validate it on held-out cases.\n",
        encoding="utf-8",
    )
    index = root / "wiki" / "index.md"
    text = index.read_text(encoding="utf-8")
    text = text.replace("None recorded.\n", "")
    index.write_text(text.rstrip() + f"\n- [{pattern_id}](patterns/{pattern_id}.md) — draft\n", encoding="utf-8")
    with (root / "wiki" / "logs.md").open("a", encoding="utf-8") as log:
        log.write(f"\n## {stamp()} — pattern added\n\n- `{pattern_id}`\n")
    return path.relative_to(root).as_posix()


def record_impact(root: Path, proposal_id: str, target: str, score: float, decision: str, evidence: list[str]) -> None:
    require_id(proposal_id, "proposal id")
    if decision not in {"accepted", "rejected"}:
        raise ValueError("decision must be accepted or rejected")
    if not 0 <= score <= 1:
        raise ValueError("validation score must be between 0 and 1")
    initialize(root)
    if not evidence:
        raise ValueError("at least one --evidence wiki/patterns/... page is required")
    for item in evidence:
        path = Path(item)
        if path.is_absolute() or path.parts[:2] != ("wiki", "patterns") or not (root / path).is_file():
            raise ValueError(f"evidence must name an existing wiki/patterns/ page: {item}")
    with (root / "wiki" / "skill-impact.md").open("a", encoding="utf-8") as ledger:
        ledger.write(
            f"\n## {stamp()} — {decision}\n\n"
            f"- Proposal: `{proposal_id}`\n- Target: `{target}`\n"
            f"- Held-out validation score: `{score:.4f}`\n"
            + "".join(f"- Pattern: `{item}`\n" for item in evidence)
        )


def validate(root: Path) -> list[str]:
    errors = []
    required = ("raw", "wiki/index.md", "wiki/logs.md", "wiki/skill-impact.md", "wiki/patterns")
    for relative in required:
        if not (root / relative).exists():
            errors.append(f"missing {relative}")
    for pattern in (root / "wiki" / "patterns").glob("*.md") if (root / "wiki" / "patterns").exists() else ():
        content = pattern.read_text(encoding="utf-8")
        if "Status: draft — not executable guidance." not in content:
            errors.append(f"{pattern.relative_to(root)} lacks draft status")
        for item in re.findall(r"`(raw/[^`]+)`", content):
            if not (root / item).is_file():
                errors.append(f"{pattern.relative_to(root)} references missing {item}")
    return errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Maintain a persistent, non-runtime skill wiki")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("init")
    cap = sub.add_parser("capture")
    cap.add_argument("--source", required=True, type=Path)
    cap.add_argument("--classification", required=True)
    pattern = sub.add_parser("add-pattern")
    pattern.add_argument("--id", required=True)
    pattern.add_argument("--title", required=True)
    pattern.add_argument("--finding", required=True)
    pattern.add_argument("--evidence", action="append", default=[])
    impact = sub.add_parser("record-impact")
    impact.add_argument("--proposal-id", required=True)
    impact.add_argument("--target", required=True)
    impact.add_argument("--validation-score", required=True, type=float)
    impact.add_argument("--decision", required=True)
    impact.add_argument("--evidence", action="append", default=[])
    sub.add_parser("validate")
    args = parser.parse_args(argv)
    root = root_for(Path(__file__))
    try:
        if args.command == "init":
            made = initialize(root)
            print("wiki: initialized" + (f" ({', '.join(made)})" if made else " (already present)"))
        elif args.command == "capture":
            print(f"wiki: captured {capture(root, args.source, args.classification)}")
        elif args.command == "add-pattern":
            print(f"wiki: added {add_pattern(root, args.id, args.title, args.finding, args.evidence)}")
        elif args.command == "record-impact":
            record_impact(root, args.proposal_id, args.target, args.validation_score, args.decision, args.evidence)
            print(f"wiki: recorded {args.decision} decision")
        else:
            errors = validate(root)
            if errors:
                print("wiki: INVALID\n" + "\n".join(f"- {error}" for error in errors), file=sys.stderr)
                return 1
            print("wiki: valid")
    except ValueError as exc:
        print(f"wiki: error: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
