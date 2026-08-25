"""Custom installer destinations must not leak writes into the user's home."""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

import pytest


ROOT = Path(__file__).parent.parent.parent


@pytest.mark.skipif(sys.platform == "win32", reason="POSIX shell installer")
def test_posix_custom_path_is_the_only_install_destination(tmp_path: Path) -> None:
    skill = tmp_path / "contained-skill"
    skill.mkdir()
    template = (ROOT / "scripts/install-template.sh").read_text(encoding="utf-8")
    installer = skill / "install.sh"
    installer.write_text(template.replace("{{SKILL_NAME}}", "contained-skill"), encoding="utf-8")
    installer.chmod(0o755)
    (skill / "SKILL.md").write_text(
        "---\nname: contained-skill\ndescription: Verify custom install containment.\n---\n",
        encoding="utf-8",
    )
    isolated_home = tmp_path / "home"
    isolated_home.mkdir()
    destination = tmp_path / "only-destination"

    result = subprocess.run(
        [str(installer), "--platform", "claude-code", "--path", str(destination)],
        cwd=skill,
        env={**os.environ, "HOME": str(isolated_home)},
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stdout + result.stderr
    assert (destination / "SKILL.md").exists()
    assert not (isolated_home / ".agents").exists()


@pytest.mark.skipif(sys.platform == "win32", reason="POSIX shell installer")
def test_posix_custom_path_rejects_all_platforms(tmp_path: Path) -> None:
    skill = tmp_path / "contained-skill"
    skill.mkdir()
    template = (ROOT / "scripts/install-template.sh").read_text(encoding="utf-8")
    installer = skill / "install.sh"
    installer.write_text(template.replace("{{SKILL_NAME}}", "contained-skill"), encoding="utf-8")
    installer.chmod(0o755)
    (skill / "SKILL.md").write_text(
        "---\nname: contained-skill\ndescription: Verify custom install containment.\n---\n",
        encoding="utf-8",
    )

    result = subprocess.run(
        [str(installer), "--all", "--path", str(tmp_path / "destination")],
        cwd=skill,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 1
    assert "cannot be combined" in result.stderr
