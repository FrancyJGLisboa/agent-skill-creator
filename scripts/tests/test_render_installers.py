from __future__ import annotations

import os
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

from render_installers import render  # noqa: E402


def test_renders_both_installers_with_skill_identity_and_version(tmp_path: Path) -> None:
    skill = tmp_path / "weather-brief-skill"
    skill.mkdir()
    (skill / "SKILL.md").write_text(
        "---\nname: weather-brief-skill\nversion: 2.3.4\nmetadata:\n  version: 2.3.4\n---\nbody\n",
        encoding="utf-8",
    )
    shell, powershell = render(skill)
    assert '{{SKILL_NAME}}' not in shell.read_text()
    assert 'SKILL_NAME="weather-brief-skill"' in shell.read_text()
    assert 'VERSION="2.3.4"' in shell.read_text()
    assert '$SkillName = "weather-brief-skill"' in powershell.read_text()
    assert '$Version = "2.3.4"' in powershell.read_text()
    assert os.access(shell, os.X_OK)


def test_rejects_factory_identity_as_generated_skill(tmp_path: Path) -> None:
    skill = tmp_path / "bad"
    skill.mkdir()
    (skill / "SKILL.md").write_text(
        "---\nname: agent-skill-creator\nversion: 1.0.0\n---\nbody\n", encoding="utf-8"
    )
    with pytest.raises(ValueError, match=r"\*-skill"):
        render(skill)
