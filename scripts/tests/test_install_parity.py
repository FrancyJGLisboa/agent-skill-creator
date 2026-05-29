"""Parity tests for the bash <-> PowerShell install-script pairs.

The repo carries three pairs of install scripts that re-implement the same
logic in two shells:
  install-template.sh  <-> install-template.ps1
  install-skill.sh     <-> install-skill.ps1
  bootstrap.sh         <-> bootstrap.ps1

This file parses both members of each pair and asserts they enumerate the
same supported platforms and (where applicable) map each platform to the
same install paths. Catches the silent drift that produced the same kind
of bug fixed in scripts/platforms.py.

Paths are normalized for comparison:
  ``${HOME}`` (sh) and ``$HomeDir`` (ps1)   -> ``~``
  Windows ``\\`` separator                  -> ``/``
"""

import re
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(ROOT / "scripts"))


# --- Path normalisation -----------------------------------------------------

def _norm_sh(path: str) -> str:
    return path.replace("${HOME}", "~")


def _norm_ps1(path: str) -> str:
    return path.replace("$HomeDir", "~").replace("\\", "/")


# --- install-template.sh / .ps1 parsers ------------------------------------

_SH_CASE_ARM = re.compile(r'^\s*([\w-]+)\)\s*base="([^"]+)"\s*;;')
_SH_SUPPORTED = re.compile(r'^SUPPORTED_PLATFORMS="([^"]+)"')


def _parse_install_template_sh(text: str) -> tuple[list[str], dict[str, str], dict[str, str]]:
    supported: list[str] = []
    project: dict[str, str] = {}
    user: dict[str, str] = {}
    section: str | None = None
    for line in text.splitlines():
        m = _SH_SUPPORTED.match(line)
        if m:
            supported = [s.strip() for s in m.group(1).split(",")]
            continue
        if "Project-level: paths are relative" in line:
            section = "project"
            continue
        if "User-level: paths are under" in line:
            section = "user"
            continue
        arm = _SH_CASE_ARM.match(line)
        if arm and section:
            name, raw = arm.group(1), arm.group(2)
            (project if section == "project" else user)[name] = _norm_sh(raw)
    return supported, project, user


_PS1_ARM_PROJECT = re.compile(r'^\s*"([\w-]+)"\s*\{\s*"([^"]+)"\s*\}')
_PS1_ARM_USER = re.compile(r'^\s*"([\w-]+)"\s*\{\s*Join-Path\s+\$HomeDir\s+"([^"]+)"\s*\}')
_PS1_SUPPORTED_BLOCK = re.compile(r'\$SupportedPlatforms\s*=\s*@\(([^)]+)\)', re.DOTALL)
_PS1_QUOTED = re.compile(r'"([\w-]+)"')


def _parse_install_template_ps1(text: str) -> tuple[list[str], dict[str, str], dict[str, str]]:
    sup_match = _PS1_SUPPORTED_BLOCK.search(text)
    supported = _PS1_QUOTED.findall(sup_match.group(1)) if sup_match else []
    project: dict[str, str] = {}
    user: dict[str, str] = {}
    for line in text.splitlines():
        m = _PS1_ARM_USER.match(line)  # check User form first (more specific)
        if m:
            # Join-Path $HomeDir "X" -> "~/X" (the captured path lacks the home prefix)
            user[m.group(1)] = "~/" + _norm_ps1(m.group(2)).lstrip("/")
            continue
        m = _PS1_ARM_PROJECT.match(line)
        if m:
            value = _norm_ps1(m.group(2))
            # Filter out display-name switch blocks (e.g. "Claude Code") -- only
            # path-like values (starting with '.') are project install paths.
            if value.startswith("."):
                project[m.group(1)] = value
    return supported, project, user


# --- bootstrap.sh / .ps1 parsers -------------------------------------------

_SH_BOOTSTRAP_DETECT = re.compile(r'platforms="\$platforms\s+([\w-]+)"')
# Match Name= only inside a dict entry (preceded by ';'), so $SkillName = "..."
# variable assignments are NOT caught.
_PS1_DICT_ENTRY = re.compile(r';\s*Name\s*=\s*"([\w-]+)"')

# Platforms that legitimately appear in only one shell because the detection
# is OS-specific (AppData/, etc.). Filtered before comparison.
_BOOTSTRAP_OS_SPECIFIC: set[str] = {"claude-desktop"}


def _parse_bootstrap_platforms_sh(text: str) -> set[str]:
    """Pull every platform appended to the `platforms` variable during detection."""
    return set(_SH_BOOTSTRAP_DETECT.findall(text)) - _BOOTSTRAP_OS_SPECIFIC


def _parse_bootstrap_platforms_ps1(text: str) -> set[str]:
    """Pull every platform Name in the detection dictionary."""
    return set(_PS1_DICT_ENTRY.findall(text)) - _BOOTSTRAP_OS_SPECIFIC


# --- install-skill.sh / .ps1 parsers ---------------------------------------
# install-skill's paths include skill-name suffix variants we don't want to
# normalize for parity; we check platform-set parity only.

_SH_INSTALL_SKILL_ECHO = re.compile(r'^\s*([\w-]+)\)\s*echo\s+"')


def _parse_install_skill_platforms_sh(text: str) -> set[str]:
    """Union of every platform referenced (detection or case arm)."""
    detection = set(_SH_BOOTSTRAP_DETECT.findall(text))
    case_arms = set(_SH_INSTALL_SKILL_ECHO.findall(text))
    return detection | case_arms


_PS1_INSTALL_SKILL_ARM = re.compile(r'^\s*"([\w-]+)"\s*\{')


def _parse_install_skill_platforms_ps1(text: str) -> set[str]:
    """Union of every platform referenced (dict entries + switch arms)."""
    return set(_PS1_DICT_ENTRY.findall(text)) | set(_PS1_INSTALL_SKILL_ARM.findall(text))


# --- Tests -----------------------------------------------------------------


class InstallTemplateParityTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        sh_text = (ROOT / "scripts" / "install-template.sh").read_text(encoding="utf-8")
        ps1_text = (ROOT / "scripts" / "install-template.ps1").read_text(encoding="utf-8")
        cls.sh_sup, cls.sh_project, cls.sh_user = _parse_install_template_sh(sh_text)
        cls.ps1_sup, cls.ps1_project, cls.ps1_user = _parse_install_template_ps1(ps1_text)

    def test_supported_platforms_match(self) -> None:
        self.assertEqual(
            sorted(self.sh_sup),
            sorted(self.ps1_sup),
            "install-template.sh SUPPORTED_PLATFORMS drifted from install-template.ps1 $SupportedPlatforms",
        )

    def test_project_paths_match(self) -> None:
        for plat in self.sh_sup:
            self.assertEqual(
                self.sh_project.get(plat),
                self.ps1_project.get(plat),
                f"{plat}: project-level install paths drifted between install-template.sh and .ps1",
            )

    def test_user_paths_match(self) -> None:
        for plat in self.sh_sup:
            self.assertEqual(
                self.sh_user.get(plat),
                self.ps1_user.get(plat),
                f"{plat}: user-level install paths drifted between install-template.sh and .ps1",
            )


class InstallSkillParityTest(unittest.TestCase):
    """Platform-set parity only -- install-skill's paths embed `$name`/`$SkillName`
    in varying positions that aren't worth byte-level parity."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.sh_plats = _parse_install_skill_platforms_sh(
            (ROOT / "scripts" / "install-skill.sh").read_text(encoding="utf-8")
        )
        cls.ps1_plats = _parse_install_skill_platforms_ps1(
            (ROOT / "scripts" / "install-skill.ps1").read_text(encoding="utf-8")
        )

    def test_same_platform_set(self) -> None:
        self.assertEqual(
            self.sh_plats,
            self.ps1_plats,
            "install-skill.sh and install-skill.ps1 enumerate different platforms",
        )


class BootstrapParityTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.sh_plats = _parse_bootstrap_platforms_sh(
            (ROOT / "scripts" / "bootstrap.sh").read_text(encoding="utf-8")
        )
        cls.ps1_plats = _parse_bootstrap_platforms_ps1(
            (ROOT / "scripts" / "bootstrap.ps1").read_text(encoding="utf-8")
        )

    def test_detected_platforms_match(self) -> None:
        """Hard parity gate. Filter `_BOOTSTRAP_OS_SPECIFIC` covers Windows-only
        entries (claude-desktop AppData detection)."""
        self.assertEqual(self.sh_plats, self.ps1_plats)

    def test_bootstrap_sh_subset_of_ps1(self) -> None:
        """Stronger regression gate: bootstrap.sh's detected platforms must all
        be a subset of bootstrap.ps1's. New drift where bootstrap.sh gains a
        platform that .ps1 lacks would fail here even while the known cursor
        finding is still xfail above."""
        self.assertTrue(
            self.sh_plats.issubset(self.ps1_plats),
            f"bootstrap.sh detects platforms .ps1 does not: {self.sh_plats - self.ps1_plats}",
        )


if __name__ == "__main__":
    unittest.main()
