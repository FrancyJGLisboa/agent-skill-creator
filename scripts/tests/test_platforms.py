"""Tests for scripts.platforms — the canonical install-target registry.

Two layers:
1. Sanity tests on the registry itself (well-formed, no duplicates).
2. Drift detection: parse scripts/install-template.sh and assert its
   SUPPORTED_PLATFORMS list and project/user case arms match the registry.
   Catches the situation where someone updates the shell installer but forgets
   to update platforms.py (or vice versa) -- the source of the Windsurf bug
   this module was built to prevent.
"""

import re
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

from platforms import PLATFORMS, get_platform, list_supported_platforms  # noqa: E402

INSTALL_TEMPLATE = ROOT / "scripts" / "install-template.sh"

_CASE_ARM = re.compile(r'^\s*([\w-]+)\)\s*base="([^"]+)"\s*;;')
_SUPPORTED = re.compile(r'^SUPPORTED_PLATFORMS="([^"]+)"')


def _parse_install_template() -> tuple[list[str], dict[str, str], dict[str, str]]:
    """Return (supported, project_arms, user_arms) parsed from install-template.sh."""
    text = INSTALL_TEMPLATE.read_text(encoding="utf-8")
    supported: list[str] = []
    project_arms: dict[str, str] = {}
    user_arms: dict[str, str] = {}
    section = None  # "project" | "user" | None
    for line in text.splitlines():
        sup = _SUPPORTED.match(line)
        if sup:
            supported = [s.strip() for s in sup.group(1).split(",")]
            continue
        if "Project-level: paths are relative" in line:
            section = "project"
            continue
        if "User-level: paths are under" in line:
            section = "user"
            continue
        arm = _CASE_ARM.match(line)
        if arm and section:
            name, path = arm.group(1), arm.group(2)
            target = project_arms if section == "project" else user_arms
            target[name] = path.replace("${HOME}", "~")
    return supported, project_arms, user_arms


class RegistrySanityTest(unittest.TestCase):
    def test_at_least_one_platform(self) -> None:
        self.assertGreater(len(PLATFORMS), 0)

    def test_names_unique(self) -> None:
        names = [p.name for p in PLATFORMS]
        self.assertEqual(len(names), len(set(names)))

    def test_get_platform_round_trip(self) -> None:
        for p in PLATFORMS:
            self.assertEqual(get_platform(p.name), p)

    def test_unknown_returns_none(self) -> None:
        self.assertIsNone(get_platform("does-not-exist"))

    def test_user_and_project_paths_non_empty(self) -> None:
        for p in PLATFORMS:
            self.assertTrue(p.user_path, f"{p.name} missing user_path")
            self.assertTrue(p.project_path, f"{p.name} missing project_path")


class InstallTemplateDriftTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.supported, cls.project_arms, cls.user_arms = _parse_install_template()

    def test_supported_list_matches_registry(self) -> None:
        self.assertEqual(
            sorted(self.supported),
            sorted(list_supported_platforms()),
            "install-template.sh SUPPORTED_PLATFORMS drifted from scripts/platforms.py",
        )

    def test_project_paths_match_registry(self) -> None:
        for p in PLATFORMS:
            self.assertEqual(
                self.project_arms.get(p.name),
                p.project_path,
                f"{p.name}: install-template.sh project path drifted from platforms.py",
            )

    def test_user_paths_match_registry(self) -> None:
        for p in PLATFORMS:
            self.assertEqual(
                self.user_arms.get(p.name),
                p.user_path,
                f"{p.name}: install-template.sh user path drifted from platforms.py",
            )


if __name__ == "__main__":
    unittest.main()
