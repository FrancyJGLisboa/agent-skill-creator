#!/usr/bin/env python3
"""Check public docs for broken local links, command paths, and policy drift."""
import re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOCS = [ROOT / "README.md", ROOT / "docs/index.html"]
COMMAND_PATHS = ["scripts/team_marketplace.py", "scripts/bootstrap.sh", "docs/INSTALL.md"]
REQUIRED = [
    "Semantic Recon",
    "--without-semantic-recon",
    "agent-skills-platform",
]

def main() -> int:
    errors, checked = [], []
    for doc in DOCS:
        text = doc.read_text(encoding="utf-8")
        normalized = " ".join(text.split())
        checked.append(str(doc.relative_to(ROOT)))
        for target in re.findall(r"\[[^]]+\]\(([^)]+)\)|href=[\"']([^\"']+)", text):
            target = next(x for x in target if x)
            if target.startswith(("http:", "https:", "#", "mailto:")): continue
            raw_path = target.split("#",1)[0]
            path = (doc.parent / raw_path).resolve()
            if not path.exists() and raw_path.endswith(".html"):
                path = path.with_suffix(".md")
            if not path.exists(): errors.append(f"{doc.relative_to(ROOT)}: missing link {target}")
        for command_path in COMMAND_PATHS:
            if command_path in text and not (ROOT / command_path).exists():
                errors.append(f"{doc.relative_to(ROOT)}: command path missing {command_path}")
        for phrase in REQUIRED:
            if phrase not in normalized: errors.append(f"{doc.relative_to(ROOT)}: missing policy phrase {phrase}")
    if errors:
        print("PUBLIC DOCS: FAIL")
        print("\n".join(f"- {e}" for e in errors)); return 1
    print("PUBLIC DOCS: PASS")
    print("checked: " + ", ".join(checked))
    print("local links, command paths, and Semantic Recon policy phrases are valid")
    return 0
if __name__ == "__main__": raise SystemExit(main())
