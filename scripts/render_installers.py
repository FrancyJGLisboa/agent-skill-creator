#!/usr/bin/env python3
"""Render generated-skill installers from canonical parameterized templates."""

from __future__ import annotations

import argparse
import re
from pathlib import Path

from skill_document import SkillDoc

ROOT = Path(__file__).resolve().parent
NAME = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*-skill$")
SEMVER = re.compile(r"^(?:0|[1-9]\d*)\.(?:0|[1-9]\d*)\.(?:0|[1-9]\d*)$")


def render(skill_dir: Path) -> tuple[Path, Path]:
    skill_dir = skill_dir.resolve()
    doc = SkillDoc.from_path(skill_dir / "SKILL.md")
    name = (doc.name or "").strip()
    version = (doc.metadata.get("version") or doc.field("version") or "").strip()
    if not NAME.fullmatch(name):
        raise ValueError("generated skill name must be a lowercase *-skill slug")
    if not SEMVER.fullmatch(version):
        raise ValueError("generated skill version must use MAJOR.MINOR.PATCH")
    outputs: list[Path] = []
    for template_name, output_name in (
        ("install-template.sh", "install.sh"),
        ("install-template.ps1", "install.ps1"),
    ):
        content = (ROOT / template_name).read_text(encoding="utf-8")
        content = content.replace("{{SKILL_NAME}}", name)
        content = re.sub(r'(?m)^VERSION="[^"]*"$', f'VERSION="{version}"', content)
        content = re.sub(r'(?m)^\$Version\s*=\s*"[^"]*"$', f'$Version = "{version}"', content)
        destination = skill_dir / output_name
        destination.write_text(content, encoding="utf-8")
        outputs.append(destination)
    outputs[0].chmod(0o755)
    return outputs[0], outputs[1]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("skill_dir", type=Path)
    args = parser.parse_args()
    try:
        for path in render(args.skill_dir):
            print(path)
        return 0
    except (OSError, ValueError) as exc:
        parser.error(str(exc))
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
