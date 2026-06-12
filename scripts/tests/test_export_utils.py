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

from export_utils import export_skill  # noqa: E402

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
            capture_output=True, text=True, timeout=120,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        expected = self.out / "demo-export-skill-desktop-v9.9.9.zip"
        self.assertTrue(
            expected.exists(),
            f"expected {expected}, found: {sorted(p.name for p in self.out.iterdir())}",
        )


class TestExportSkillFailurePath(unittest.TestCase):
    def test_invalid_skill_dir_returns_failure(self):
        with tempfile.TemporaryDirectory() as tmp:
            results = export_skill(os.path.join(tmp, "does-not-exist"), ["desktop"])
            self.assertFalse(results["success"])
            self.assertTrue(results.get("issues"))


if __name__ == "__main__":
    unittest.main()
