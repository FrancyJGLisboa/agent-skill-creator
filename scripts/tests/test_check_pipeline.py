"""Tests for scripts.check_pipeline — the generated-skill pipeline verifier."""

import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

from check_pipeline import check, main  # noqa: E402

STEP = "def main():\n    pass\n\n\nif __name__ == '__main__':\n    main()\n"


def _skill(tmp: Path, files: dict[str, str], requirements: str | None = None) -> Path:
    """Create a skill dir. `files` maps relative paths (under the skill) to text."""
    skill = tmp / "demo-skill"
    for rel, text in files.items():
        p = skill / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text, encoding="utf-8")
    if requirements is not None:
        (skill / "requirements.txt").write_text(requirements, encoding="utf-8")
    skill.mkdir(parents=True, exist_ok=True)
    return skill


class CompileCheckTest(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.tmp = Path(self._tmp.name)

    def tearDown(self) -> None:
        self._tmp.cleanup()

    def test_clean_script_passes(self) -> None:
        skill = _skill(self.tmp, {"scripts/main.py": "import json\nprint(json.dumps({}))\n"})
        result = check(skill)
        self.assertEqual(result["errors"], [])

    def test_syntax_error_is_an_error(self) -> None:
        skill = _skill(self.tmp, {"scripts/broken.py": "def main(:\n    pass\n"})
        result = check(skill)
        self.assertTrue(any("does not compile" in e for e in result["errors"]))
        self.assertEqual(main([str(skill)]), 1)


class DependencyCheckTest(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.tmp = Path(self._tmp.name)

    def tearDown(self) -> None:
        self._tmp.cleanup()

    def test_third_party_without_requirements_is_error(self) -> None:
        skill = _skill(self.tmp, {"scripts/fetch.py": "import requests\n"})
        result = check(skill)
        self.assertTrue(any("not declared" in e for e in result["errors"]))

    def test_third_party_with_requirements_ok(self) -> None:
        skill = _skill(
            self.tmp,
            {"scripts/fetch.py": "import requests\n"},
            requirements="requests>=2.0\n",
        )
        self.assertEqual(check(skill)["errors"], [])

    def test_stdlib_only_needs_no_requirements(self) -> None:
        skill = _skill(self.tmp, {"scripts/main.py": "import json, os, re\nfrom pathlib import Path\n"})
        self.assertEqual(check(skill)["errors"], [])

    def test_local_sibling_import_not_flagged(self) -> None:
        skill = _skill(
            self.tmp,
            {
                "scripts/main.py": "from helpers import go\n",
                "scripts/helpers.py": "def go():\n    pass\n",
            },
        )
        self.assertEqual(check(skill)["errors"], [])


class EntrypointWarningTest(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.tmp = Path(self._tmp.name)

    def tearDown(self) -> None:
        self._tmp.cleanup()

    def test_two_steps_without_orchestrator_warns(self) -> None:
        skill = _skill(self.tmp, {"scripts/fetch.py": STEP, "scripts/parse.py": STEP})
        result = check(skill)
        self.assertEqual(result["errors"], [])
        self.assertTrue(any("orchestrator" in w or "sequence" in w for w in result["warnings"]))
        self.assertEqual(main([str(skill)]), 0)  # warning, not error

    def test_two_steps_with_orchestrator_no_warning(self) -> None:
        skill = _skill(
            self.tmp,
            {
                "scripts/fetch.py": STEP,
                "scripts/parse.py": STEP,
                "scripts/run_pipeline.py": STEP,
            },
        )
        self.assertEqual(check(skill)["warnings"], [])

    def test_single_step_no_warning(self) -> None:
        skill = _skill(self.tmp, {"scripts/main.py": STEP})
        self.assertEqual(check(skill)["warnings"], [])


class MainExitTest(unittest.TestCase):
    def test_missing_dir_exits_two(self) -> None:
        self.assertEqual(main(["/no/such/skill/dir/xyz"]), 2)


if __name__ == "__main__":
    unittest.main()
