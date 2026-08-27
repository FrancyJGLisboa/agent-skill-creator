#!/usr/bin/env python3
"""
Evolve loop shipped inside every generated skill as scripts/evolve.py.

One command that closes the maintenance loop from the skill's own root:

    python3 scripts/evolve.py            # detect -> record -> re-verify
    python3 scripts/evolve.py --judge    # also grade llm-judge criteria
    python3 scripts/evolve.py --correct "<what the skill got wrong>"

Steps (default mode):
  1. staleness_check --check-deps --check-drift --record
     (review-interval, dependency health, schema drift; failures append raw
     evidence to EVOLUTION.md)
  2. run_evals --rollout [--judge]
     (runs the skill on its golden inputs; command checks + baseline regression
     gate + optional pinned judge; failures append raw evidence to EVOLUTION.md)

`--correct` is a different kind of input, and the most valuable one this loop
takes. Steps 1 and 2 catch what a machine can check: dates, reachability, output
drift. They cannot catch the class of knowledge that only exists in someone's
head -- the region that files late, the code that means something local, the
month the process runs differently.

That knowledge is not obtainable by asking up front. People cannot articulate a
workflow they run from muscle memory, which is why this factory reads artifacts
instead of interviewing. But the same person who could not describe the rule will
recognize its violation instantly, the moment the skill produces something wrong.
`--correct` is the capture point for that moment: it takes the sentence they would
have said out loud, writes it verbatim to EVOLUTION.md as evidence, and adds it to
the skill's `## Gotchas` so the next run already knows.

Exit codes:
    0 - fresh and green (or: correction recorded)
    1 - one or more steps failed; EVOLUTION.md holds the evidence
    2 - bad usage
"""

from __future__ import annotations

import re
import hashlib
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

from success_ledger import record_event

GOTCHAS_HEADING = re.compile(r"^([ \t]{0,3})(#{1,6})[ \t]+gotchas\b.*$", re.IGNORECASE | re.MULTILINE)
# A placeholder body meaning "there are none yet" -- replaced rather than appended to.
NONE_KNOWN = re.compile(r"^\s*(none known|none|n/a)\.?\s*$", re.IGNORECASE)
# Sections a Gotchas block should precede when one has to be created from scratch.
FALLBACK_ANCHORS = ("## Keywords", "## Usage Examples", "## References", "## Anti-goals")


def _utc_stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _correction_id(stamp: str, text: str) -> str:
    """Return a stable, filesystem-safe ID for one correction record."""
    compact_stamp = stamp.replace("-", "").replace(":", "").replace("T", "-").replace("Z", "")
    digest = hashlib.sha256(text.encode("utf-8")).hexdigest()[:10]
    return f"correction-{compact_stamp}-{digest}"


def _write_correction_regression(skill_dir: Path, correction_id: str, stamp: str, text: str) -> Path:
    """Create an executable knowledge-retention regression for a correction.

    The correction itself is authoritative evidence. The generated assertion makes
    removing that knowledge from the skill an eval failure until an explicit,
    reviewed replacement is made.
    """
    corrections = skill_dir / "evals" / "corrections"
    corrections.mkdir(parents=True, exist_ok=True)
    path = corrections / f"{correction_id}.json"
    record = {
        "id": correction_id,
        "reported_at": stamp,
        "correction": text,
        "proposed_skill_edit": {
            "file": "SKILL.md",
            "section": "Gotchas",
            "change": f"Add the reported behavior: {text}",
        },
        "regression_test": {
            "type": "knowledge-retention",
            "file": "SKILL.md",
            "must_contain": text,
        },
        "version": {
            "recommended_bump": "patch",
            "reason": "Correction from real use; preserve the corrected behavior and prevent its removal without review.",
        },
    }
    path.write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
    return path


def _record_lifecycle(event: str, skill_dir: Path) -> None:
    """Record product health locally without making maintenance depend on metrics."""
    try:
        record_event(event, skill=skill_dir.name)
    except (OSError, ValueError) as exc:
        print(f"warning: success ledger did not record {event}: {exc}", file=sys.stderr)


def record_correction(skill_dir: Path, text: str) -> list[str]:
    """Write a user correction to EVOLUTION.md and the SKILL.md Gotchas section.

    Verbatim on purpose. The wording a user reaches for when something is wrong
    carries detail a paraphrase drops, and this runs unattended -- rewriting it
    into the wrong-assumption/real-behavior house style is a judgment call for
    whoever next edits the skill, not for this script.

    Args:
        skill_dir: The skill's root (the directory holding SKILL.md).
        text: The correction, as the user phrased it.

    Returns:
        Human-readable lines describing what changed, for printing.

    Raises:
        ValueError: If the text is blank or SKILL.md is missing.
    """
    text = " ".join(text.split())
    if not text:
        raise ValueError("correction text is empty")

    skill_md = skill_dir / "SKILL.md"
    if not skill_md.exists():
        raise ValueError(f"SKILL.md not found in {skill_dir}")

    stamp = _utc_stamp()
    correction_id = _correction_id(stamp, text)
    done: list[str] = []

    # 1. EVOLUTION.md -- the audit trail. Append-only, never rewritten.
    evolution = skill_dir / "EVOLUTION.md"
    if not evolution.exists():
        evolution.write_text(
            "# Evolution log\n\nAppended automatically by scripts/run_evals.py "
            "(and scripts/evolve.py) when a check fails. Each entry is the raw "
            "evidence for a fix/regenerate step.\n\n",
            encoding="utf-8",
        )
    with evolution.open("a", encoding="utf-8") as fh:
        fh.write(
            f"## {stamp} — correction from use\n\n"
            f"Change ID: `{correction_id}`\n\n"
            f"Reported while using the skill, not caught by any automated check.\n\n"
            f"> {text}\n\n"
            f"Proposed skill edit: add the corrected behavior to `SKILL.md` → `## Gotchas`.\n\n"
            f"Regression test: `evals/corrections/{correction_id}.json` must keep this behavior in the skill.\n\n"
            f"Version recommendation: patch — correction from real use.\n\n"
        )
    done.append(f"EVOLUTION.md  <- correction recorded ({stamp})")

    # 2. SKILL.md ## Gotchas -- the part the agent actually reads on the next run.
    content = skill_md.read_text(encoding="utf-8")
    bullet = f"- {text}"
    match = GOTCHAS_HEADING.search(content)

    if match:
        level = len(match.group(2))
        body_start = match.end()
        # The section runs to the next heading at the same level or higher.
        following = re.compile(rf"^[ \t]{{0,3}}#{{1,{level}}}[ \t]+", re.MULTILINE)
        nxt = following.search(content, body_start)
        body_end = nxt.start() if nxt else len(content)
        body = content[body_start:body_end]

        if all(NONE_KNOWN.match(ln) or not ln.strip() for ln in body.splitlines()):
            new_body = f"\n\n{bullet}\n\n"          # replace the placeholder
            note = "replaced 'None known'"
        else:
            new_body = body.rstrip("\n") + f"\n{bullet}\n\n"
            note = "appended"
        content = content[:body_start] + new_body + content[body_end:]
    else:
        section = f"## Gotchas\n\n{bullet}\n\n"
        anchor = next((a for a in FALLBACK_ANCHORS if f"\n{a}" in content), None)
        if anchor:
            content = content.replace(f"\n{anchor}", f"\n{section}{anchor}", 1)
        else:
            content = content.rstrip("\n") + f"\n\n{section}"
        note = "created the section"

    skill_md.write_text(content, encoding="utf-8")
    done.append(f"SKILL.md      <- ## Gotchas ({note})")
    regression = _write_correction_regression(skill_dir, correction_id, stamp, text)
    done.append(f"{regression.relative_to(skill_dir)} <- executable correction regression")
    return done


def main(argv: list[str] | None = None) -> int:
    args = argv if argv is not None else sys.argv[1:]
    root = Path(__file__).resolve().parent.parent

    if "--correct" in args:
        index = args.index("--correct")
        text = " ".join(args[index + 1:])
        if not text.strip():
            print(
                'usage: python3 scripts/evolve.py --correct "<what the skill got wrong>"',
                file=sys.stderr,
            )
            return 2
        try:
            for line in record_correction(root, text):
                print(line)
        except ValueError as exc:
            print(f"error: {exc}", file=sys.stderr)
            return 2
        _record_lifecycle("correction_recorded", root)
        print("\nnext: run scripts/evolve.py to verify the proposed edit and correction regression")
        return 0

    judge = ["--judge"] if "--judge" in args else []

    steps = [
        ("staleness", [
            sys.executable, "scripts/staleness_check.py", str(root),
            "--check-deps", "--check-drift", "--record",
        ]),
        ("evals", [
            sys.executable, "scripts/run_evals.py", str(root), "--rollout", *judge,
        ]),
    ]

    failures: list[tuple[str, int]] = []
    for name, cmd in steps:
        print(f"== evolve: {name} ==")
        proc = subprocess.run(cmd, cwd=root)  # noqa: S603
        if proc.returncode != 0:
            failures.append((name, proc.returncode))

    if failures:
        if any(name == "evals" for name, _ in failures):
            _record_lifecycle("regression_detected", root)
        print("\nevolve: FAILED — raw evidence recorded in EVOLUTION.md")
        for name, rc in failures:
            print(f"  - {name} (exit {rc})")
        print(
            "next: fix the findings (or hand EVOLUTION.md back to "
            "/agent-skill-creator to regenerate), then re-run scripts/evolve.py "
            "until clean"
        )
        return 1

    _record_lifecycle("gates_passed", root)
    print("\nevolve: all checks fresh and green")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
