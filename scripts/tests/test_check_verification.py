import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

from check_verification import changed_skill_dirs  # noqa: E402


def test_changed_skill_dirs_returns_no_skills_when_diff_is_empty() -> None:
    assert changed_skill_dirs("HEAD", "HEAD") == []
