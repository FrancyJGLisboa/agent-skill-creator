"""Tests for scripts.security_scan token detection.

Fake tokens are built by concatenation so this test file itself never
contains a contiguous token-shaped string.
"""

import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

from security_scan import security_scan  # noqa: E402


def make_skill_with_content(base: Path, content: str) -> Path:
    skill = base / "demo-scan-skill"
    (skill / "scripts").mkdir(parents=True)
    (skill / "SKILL.md").write_text(
        "---\nname: demo-scan-skill\ndescription: demo\n---\n# demo\n",
        encoding="utf-8",
    )
    (skill / "scripts" / "main.py").write_text(content, encoding="utf-8")
    return skill


class TestGitHubTokenDetection(unittest.TestCase):
    def _patterns_found(self, content):
        with tempfile.TemporaryDirectory() as tmp:
            skill = make_skill_with_content(Path(tmp), content)
            result = security_scan(str(skill))
            return {issue["pattern"] for issue in result["issues"]}

    def test_classic_pat_detected(self):
        token = "ghp_" + "a1B2" * 9  # 36 chars after prefix
        found = self._patterns_found(f'TOKEN = "{token}"\n')
        self.assertIn("GitHub Personal Access Token", found)

    def test_fine_grained_pat_detected(self):
        token = "github_pat_" + "11AAAAAAA0" * 6  # 60 chars after prefix
        found = self._patterns_found(f'TOKEN = "{token}"\n')
        self.assertIn("GitHub Fine-Grained Personal Access Token", found)

    def test_oauth_token_detected(self):
        token = "gho_" + "a1B2" * 9
        found = self._patterns_found(f'TOKEN = "{token}"\n')
        self.assertIn("GitHub OAuth/App Token", found)

    def test_benign_content_clean(self):
        with tempfile.TemporaryDirectory() as tmp:
            skill = make_skill_with_content(
                Path(tmp), 'import os\nTOKEN = os.environ["GITHUB_TOKEN"]\n'
            )
            result = security_scan(str(skill))
            self.assertTrue(result["clean"], result["issues"])


if __name__ == "__main__":
    unittest.main()
