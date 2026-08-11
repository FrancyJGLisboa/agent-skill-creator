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


# --- root install.sh / install.ps1 parsers ---------------------------------
#
# The repo's OWN self-installers, as opposed to the templates that ship into
# generated skills. They were the one shell pair nothing compared, which is how
# Cursor came to be listed in install.ps1 and missing from install.sh: `--all`
# installed for Cursor on Windows and silently skipped it everywhere else.

_ROOT_SH_ENTRY = re.compile(r'^\$HOME/(\S+?)\|\$HOME/(\S+?)/\$SKILL_NAME\|(.+)$')
_ROOT_PS1_ENTRY = re.compile(
    r'DetectDir\s*=\s*"([^"]+)"\s*;\s*InstallPath\s*=\s*"([^"]+)\\\$SkillName"\s*;\s*Display\s*=\s*"([^"]+)"'
)


def _parse_root_install_sh(text: str) -> dict[str, tuple[str, str]]:
    """Display name -> (detection dir, install dir), from the heredoc table."""
    out: dict[str, tuple[str, str]] = {}
    for line in text.splitlines():
        m = _ROOT_SH_ENTRY.match(line.strip())
        if m:
            out[m.group(3).strip()] = (m.group(1), m.group(2))
    return out


def _parse_root_install_ps1(text: str) -> dict[str, tuple[str, str]]:
    """Same shape from the PowerShell hashtable list, backslashes normalised."""
    out: dict[str, tuple[str, str]] = {}
    for detect, install, display in _ROOT_PS1_ENTRY.findall(text):
        out[display.strip()] = (detect.replace("\\", "/"), install.replace("\\", "/"))
    return out


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
        platform that .ps1 lacks would fail here."""
        self.assertTrue(
            self.sh_plats.issubset(self.ps1_plats),
            f"bootstrap.sh detects platforms .ps1 does not: {self.sh_plats - self.ps1_plats}",
        )


class RootInstallerParityTest(unittest.TestCase):
    """The repo's own install.sh / install.ps1 must offer the same platforms.

    Every other shell pair in the repo was already compared; this one was not,
    and it drifted. `--all` is the user-visible symptom: a platform present in
    only one script is installed on one OS and silently skipped on the other.
    """

    @classmethod
    def setUpClass(cls) -> None:
        cls.sh = _parse_root_install_sh((ROOT / "install.sh").read_text(encoding="utf-8"))
        cls.ps1 = _parse_root_install_ps1((ROOT / "install.ps1").read_text(encoding="utf-8"))

    def test_parsers_found_entries(self) -> None:
        """Guard the regexes: a table reformat must fail loudly, not silently
        compare two empty dicts and pass."""
        self.assertGreaterEqual(len(self.sh), 10, "install.sh table did not parse")
        self.assertGreaterEqual(len(self.ps1), 10, "install.ps1 table did not parse")

    def test_same_platform_set(self) -> None:
        self.assertEqual(
            set(self.sh),
            set(self.ps1),
            "install.sh and install.ps1 offer different platforms for --all",
        )

    def test_paths_match(self) -> None:
        for display, sh_paths in self.sh.items():
            with self.subTest(platform=display):
                self.assertEqual(
                    sh_paths,
                    self.ps1.get(display),
                    f"{display}: detection or install path drifted between "
                    f"install.sh and install.ps1",
                )


if __name__ == "__main__":
    unittest.main()
