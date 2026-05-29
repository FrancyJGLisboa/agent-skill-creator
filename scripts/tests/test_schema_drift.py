"""Tests for scripts.schema_drift — expectations parsing + drift detection (mocked)."""

import json
import sys
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch
from urllib.error import URLError

ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

from schema_drift import check_schema_drift, parse_schema_expectations  # noqa: E402
from skill_document import SkillDoc  # noqa: E402


def _doc_with_expectations() -> SkillDoc:
    return SkillDoc.from_text(
        "---\n"
        "name: demo-skill\n"
        "description: x\n"
        "metadata:\n"
        "  schema_expectations:\n"
        "    - url: https://api.example.com/v1/data\n"
        "      method: GET\n"
        "      expected_keys:\n"
        "        - id\n"
        "        - name\n"
        "        - value\n"
        "    - url: https://api2.example.com/v2/items\n"
        "      expected_keys:\n"
        "        - sku\n"
        "        - price\n"
        "---\n"
        "body\n"
    )


def _mock_json_response(payload) -> MagicMock:
    body = json.dumps(payload).encode("utf-8")
    resp = MagicMock()
    resp.read.return_value = body
    cm = MagicMock()
    cm.__enter__.return_value = resp
    cm.__exit__.return_value = None
    return cm


class ParseExpectationsTest(unittest.TestCase):
    def test_parses_two_entries(self) -> None:
        exps = parse_schema_expectations(_doc_with_expectations())
        self.assertEqual(len(exps), 2)
        self.assertEqual(exps[0]["url"], "https://api.example.com/v1/data")
        self.assertEqual(exps[0]["method"], "GET")
        self.assertEqual(sorted(exps[0]["expected_keys"]), ["id", "name", "value"])
        self.assertEqual(exps[1]["url"], "https://api2.example.com/v2/items")
        self.assertEqual(sorted(exps[1]["expected_keys"]), ["price", "sku"])

    def test_no_frontmatter_returns_empty(self) -> None:
        doc = SkillDoc.from_text("no frontmatter at all")
        self.assertEqual(parse_schema_expectations(doc), [])

    def test_no_schema_expectations_returns_empty(self) -> None:
        doc = SkillDoc.from_text("---\nname: x\ndescription: y\nmetadata:\n  author: A\n---\nbody\n")
        self.assertEqual(parse_schema_expectations(doc), [])


class CheckSchemaDriftTest(unittest.TestCase):
    EXP = [{"url": "https://api.example.com/v1", "method": "GET", "expected_keys": ["id", "name"]}]

    @patch("schema_drift.urlopen")
    def test_exact_match_reports_match(self, mock_urlopen: MagicMock) -> None:
        mock_urlopen.return_value = _mock_json_response({"id": 1, "name": "x"})
        issues = check_schema_drift(self.EXP)
        self.assertTrue(any("Schema matches" in i["message"] for i in issues))
        self.assertFalse(any(i["level"] == "error" for i in issues))

    @patch("schema_drift.urlopen")
    def test_missing_key_is_error(self, mock_urlopen: MagicMock) -> None:
        mock_urlopen.return_value = _mock_json_response({"id": 1})  # missing 'name'
        issues = check_schema_drift(self.EXP)
        self.assertTrue(any(i["level"] == "error" and "missing keys" in i["message"] for i in issues))

    @patch("schema_drift.urlopen")
    def test_new_key_is_info(self, mock_urlopen: MagicMock) -> None:
        mock_urlopen.return_value = _mock_json_response({"id": 1, "name": "x", "added": True})
        issues = check_schema_drift(self.EXP)
        self.assertTrue(any(i["level"] == "info" and "new keys" in i["message"] for i in issues))

    @patch("schema_drift.urlopen")
    def test_non_json_body_is_error(self, mock_urlopen: MagicMock) -> None:
        resp = MagicMock()
        resp.read.return_value = b"<html>not json</html>"
        cm = MagicMock()
        cm.__enter__.return_value = resp
        cm.__exit__.return_value = None
        mock_urlopen.return_value = cm
        issues = check_schema_drift(self.EXP)
        self.assertTrue(any(i["level"] == "error" and "not valid JSON" in i["message"] for i in issues))

    @patch("schema_drift.urlopen")
    def test_urlerror_is_error(self, mock_urlopen: MagicMock) -> None:
        mock_urlopen.side_effect = URLError("Unreachable")
        issues = check_schema_drift(self.EXP)
        self.assertTrue(any(i["level"] == "error" and "Cannot reach" in i["message"] for i in issues))

    def test_non_http_url_is_warning(self) -> None:
        issues = check_schema_drift([{"url": "ftp://x", "method": "GET", "expected_keys": ["a"]}])
        self.assertTrue(any(i["level"] == "warning" and "non-HTTP" in i["message"] for i in issues))

    def test_no_expected_keys_is_skipped(self) -> None:
        issues = check_schema_drift([{"url": "https://x", "method": "GET", "expected_keys": []}])
        self.assertTrue(any(i["level"] == "info" and "No expected_keys" in i["message"] for i in issues))


if __name__ == "__main__":
    unittest.main()
