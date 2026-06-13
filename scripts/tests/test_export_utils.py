"""Tests for scripts.export_utils.

The CLI regression tests pin the export_skill call signature: passing
--version and --output-dir through the CLI must reach version_override and
output_dir (a positional-argument mismatch once routed --version into a dead
``platform`` parameter and --output-dir into the version string).
"""

import os
import subprocess
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path

ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

from export_utils import (  # noqa: E402
    create_export_package,
    export_skill,
    get_skill_version,
    should_include_file,
)

EXPORT_CLI = ROOT / "scripts" / "export_utils.py"


def make_skill(base: Path, name: str = "demo-export-skill") -> Path:
    """Create a minimal skill directory that passes validate.validate_skill."""
    skill = base / name
    (skill / "scripts").mkdir(parents=True)
    (skill / "SKILL.md").write_text(
        f"""---
name: {name}
description: >-
  Demo skill used by export_utils tests.
license: MIT
metadata:
  author: test
  version: 1.2.3
---
# /{name}

Demo body.
""",
        encoding="utf-8",
    )
    (skill / "scripts" / "main.py").write_text("print('ok')\n", encoding="utf-8")
    return skill


class TestExportSkillRegression(unittest.TestCase):
    """Regression: --version / --output-dir must land in the right parameters."""

    def setUp(self):
        self._cwd = os.getcwd()
        self._tmp = tempfile.TemporaryDirectory()
        self.base = Path(self._tmp.name)
        self.skill = make_skill(self.base)
        self.out = self.base / "out"
        self.out.mkdir()

    def tearDown(self):
        os.chdir(self._cwd)
        self._tmp.cleanup()

    def test_export_skill_honors_version_override(self):
        results = export_skill(
            str(self.skill), ["desktop"],
            version_override="9.9.9", output_dir=str(self.out),
        )
        self.assertTrue(results["success"], results)
        self.assertEqual(results["version"], "v9.9.9")
        zip_path = results["packages"]["desktop"]["zip_path"]
        self.assertIn("v9.9.9", os.path.basename(zip_path))

    def test_export_skill_honors_output_dir(self):
        results = export_skill(
            str(self.skill), ["desktop"],
            version_override="9.9.9", output_dir=str(self.out),
        )
        zip_path = Path(results["packages"]["desktop"]["zip_path"])
        self.assertEqual(zip_path.parent, self.out)
        self.assertTrue(zip_path.exists())
        # Nothing should leak into the default sibling exports/ directory
        self.assertFalse((self.base / "exports").exists())

    def test_cli_flags_end_to_end(self):
        result = subprocess.run(
            [
                sys.executable, str(EXPORT_CLI), str(self.skill),
                "--variant", "desktop",
                "--version", "9.9.9",
                "--output-dir", str(self.out),
            ],
            # The CLI emits UTF-8 (emoji status output); decode it as UTF-8 so
            # capture works regardless of the platform's default code page.
            capture_output=True, text=True, encoding="utf-8", timeout=120,
        )
        self.assertEqual(result.returncode, 0, (result.stdout or "") + (result.stderr or ""))
        expected = self.out / "demo-export-skill-desktop-v9.9.9.zip"
        self.assertTrue(
            expected.exists(),
            f"expected {expected}, found: {sorted(p.name for p in self.out.iterdir())}",
        )


class TestGetSkillVersion(unittest.TestCase):
    def setUp(self):
        self._cwd = os.getcwd()
        self._tmp = tempfile.TemporaryDirectory()
        self.base = Path(self._tmp.name)

    def tearDown(self):
        os.chdir(self._cwd)
        self._tmp.cleanup()

    def test_override_takes_precedence_and_normalizes_v_prefix(self):
        skill = make_skill(self.base)
        self.assertEqual(get_skill_version(str(skill), "2.0.1"), "v2.0.1")
        self.assertEqual(get_skill_version(str(skill), "v3.0.0"), "v3.0.0")

    def test_falls_back_to_skill_md_frontmatter(self):
        skill = make_skill(self.base)
        self.assertEqual(get_skill_version(str(skill)), "v1.2.3")

    def test_defaults_when_no_version_source(self):
        bare = self.base / "bare-skill"
        bare.mkdir()
        self.assertEqual(get_skill_version(str(bare)), "v1.0.0")


class TestShouldIncludeFile(unittest.TestCase):
    def test_exclusions_and_inclusions(self):
        cases = {
            ".env": False,
            "credentials.json": False,
            ".DS_Store": False,
            "module.pyc": False,
            "debug.log": False,
            "SKILL.md": True,
            "main.py": True,
            "data.csv": True,
        }
        for filename, expected in cases.items():
            self.assertEqual(
                should_include_file(f"/skill/{filename}", filename),
                expected,
                filename,
            )


class TestCreateExportPackage(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.base = Path(self._tmp.name)
        self.skill = make_skill(self.base)
        (self.skill / "references").mkdir()
        (self.skill / "references" / "guide.md").write_text("docs\n", encoding="utf-8")
        (self.skill / "examples").mkdir()
        (self.skill / "examples" / "sample.csv").write_text("a,b\n", encoding="utf-8")
        (self.skill / ".env").write_text("SECRET=1\n", encoding="utf-8")
        self.out = self.base / "out"
        self.out.mkdir()

    def tearDown(self):
        self._tmp.cleanup()

    def _names(self, result):
        with zipfile.ZipFile(result["zip_path"]) as zf:
            # Zip arcnames always use forward slashes; normalize so the
            # assertions below are identical on POSIX and Windows.
            return {name.replace("\\", "/") for name in zf.namelist()}

    def test_desktop_variant_includes_docs_and_excludes_secrets(self):
        result = create_export_package(
            str(self.skill), str(self.out), variant="desktop", version="v1.2.3"
        )
        self.assertTrue(result["success"], result["message"])
        names = self._names(result)
        self.assertIn("SKILL.md", names)
        self.assertIn("references/guide.md", names)
        self.assertNotIn(".env", names)

    def test_api_variant_excludes_extra_docs_and_examples(self):
        result = create_export_package(
            str(self.skill), str(self.out), variant="api", version="v1.2.3"
        )
        self.assertTrue(result["success"], result["message"])
        names = self._names(result)
        self.assertIn("SKILL.md", names)
        self.assertNotIn("references/guide.md", names)
        self.assertNotIn("examples/sample.csv", names)


class TestExportSkillFailurePath(unittest.TestCase):
    def test_invalid_skill_dir_returns_failure(self):
        with tempfile.TemporaryDirectory() as tmp:
            results = export_skill(os.path.join(tmp, "does-not-exist"), ["desktop"])
            self.assertFalse(results["success"])
            self.assertTrue(results.get("issues"))


class TestStrictSecurityFlag(unittest.TestCase):
    """Issue #11: --strict blocks export on high-severity security findings."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.base = Path(self._tmp.name)
        self.skill = make_skill(self.base, "demo-strict-skill")
        # A hardcoded GitHub PAT (built by concatenation so this test file
        # never contains a contiguous token-shaped string) -> high severity.
        token = "ghp_" + "a1B2" * 9
        (self.skill / "scripts" / "leak.py").write_text(
            f'TOKEN = "{token}"\n', encoding="utf-8"
        )
        self.out = self.base / "out"
        self.out.mkdir()

    def tearDown(self):
        self._tmp.cleanup()

    def test_strict_blocks_export_on_high_severity(self):
        results = export_skill(
            str(self.skill), ["desktop"],
            version_override="1.0.0", output_dir=str(self.out), strict=True,
        )
        self.assertFalse(results["success"], results)
        self.assertTrue(results.get("issues"))
        # No package should have been written when strict mode blocks.
        self.assertEqual(list(self.out.iterdir()), [])

    def test_default_does_not_block_on_high_severity(self):
        results = export_skill(
            str(self.skill), ["desktop"],
            version_override="1.0.0", output_dir=str(self.out),
        )
        self.assertTrue(results["success"], results)
        zip_path = Path(results["packages"]["desktop"]["zip_path"])
        self.assertTrue(zip_path.exists())

    def test_cli_strict_flag_blocks(self):
        result = subprocess.run(
            [
                sys.executable, str(EXPORT_CLI), str(self.skill),
                "--variant", "desktop",
                "--version", "1.0.0",
                "--output-dir", str(self.out),
                "--strict",
            ],
            capture_output=True, text=True, encoding="utf-8", timeout=120,
        )
        self.assertEqual(result.returncode, 1, (result.stdout or "") + (result.stderr or ""))
        self.assertEqual(list(self.out.iterdir()), [])


if __name__ == "__main__":
    unittest.main()
