"""Tests for scripts.mcp_audit_validate — the --mcp-audit report gate.

Each test encodes one of the audit's binary checks:
  C1 inventory provenance (matches raw tools/list or static evidence)
  C2 every buildable step maps to a real tool (or is an explicit local step)
  C3 every not-buildable verdict names the missing primitive + closest tool
  C4 orchestration is classified; script-orchestrated needs a non-MCP data path
  C5 the human-holdout block exists (its content is never validator-graded)
"""

import copy
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

from mcp_audit_validate import validate_report  # noqa: E402


def _valid_report() -> dict:
    return {
        "server": {"name": "vendor-data", "source": "https://mcp.vendor.example"},
        "inventory": {
            "raw_tools_list": {
                "tools": [
                    {"name": "query_prices", "inputSchema": {"type": "object"}},
                    {"name": "list_symbols", "inputSchema": {"type": "object"}},
                ]
            },
            "tools": [
                {"name": "query_prices", "description": "EOD prices by symbol"},
                {"name": "list_symbols", "description": "Symbol universe"},
            ],
        },
        "buildable": [
            {
                "skill_name": "daily-price-brief",
                "rank": 1,
                "orchestration": "agent",
                "steps": [
                    {"step": "fetch prices", "tool": "query_prices"},
                    {"step": "format brief", "local": True},
                ],
            },
            {
                "skill_name": "symbol-coverage-report",
                "rank": 2,
                "orchestration": "script",
                "data_access": "export",
                "steps": [
                    {"step": "pull universe", "tool": "list_symbols"},
                    {"step": "diff vs holdings", "local": True},
                ],
            },
        ],
        "not_buildable": [
            {
                "idea": "intraday tick alerting",
                "missing_primitive": "no tool exposes intraday data; query_prices is EOD only",
                "closest_tool": "query_prices",
            },
        ],
        "holdout": {
            "procedure": "human spot-checks 3 random buildable mappings against vendor docs"
        },
    }


def _errors(report: dict) -> list[str]:
    return [i["message"] for i in validate_report(report) if i["level"] == "error"]


class ValidReportTest(unittest.TestCase):
    def test_valid_report_has_no_errors(self) -> None:
        self.assertEqual(_errors(_valid_report()), [])

    def test_static_evidence_provenance_also_passes(self) -> None:
        report = _valid_report()
        del report["inventory"]["raw_tools_list"]
        report["inventory"]["static_evidence"] = [
            {"tool": "query_prices", "file": "src/server.ts", "line": 42},
            {"tool": "list_symbols", "file": "src/server.ts", "line": 80},
        ]
        self.assertEqual(_errors(report), [])


class C1InventoryProvenanceTest(unittest.TestCase):
    def test_no_provenance_at_all_is_error(self) -> None:
        report = _valid_report()
        del report["inventory"]["raw_tools_list"]
        self.assertTrue(any("provenance" in m for m in _errors(report)))

    def test_inventory_tool_absent_from_raw_list_is_error(self) -> None:
        report = _valid_report()
        report["inventory"]["tools"].append({"name": "invented_tool", "description": "x"})
        self.assertTrue(any("invented_tool" in m for m in _errors(report)))

    def test_raw_tool_missing_from_inventory_is_error(self) -> None:
        report = _valid_report()
        report["inventory"]["tools"] = report["inventory"]["tools"][:1]
        self.assertTrue(any("list_symbols" in m for m in _errors(report)))

    def test_empty_inventory_is_error(self) -> None:
        report = _valid_report()
        report["inventory"]["tools"] = []
        report["inventory"]["raw_tools_list"] = {"tools": []}
        report["buildable"] = []
        report["not_buildable"] = []
        self.assertTrue(any("empty" in m.lower() for m in _errors(report)))


class C2BuildableMappingTest(unittest.TestCase):
    def test_step_naming_unknown_tool_is_error(self) -> None:
        report = _valid_report()
        report["buildable"][0]["steps"][0]["tool"] = "hallucinated_tool"
        self.assertTrue(any("hallucinated_tool" in m for m in _errors(report)))

    def test_step_with_neither_tool_nor_local_is_error(self) -> None:
        report = _valid_report()
        report["buildable"][0]["steps"][1] = {"step": "mystery step"}
        self.assertTrue(any("mystery step" in m for m in _errors(report)))

    def test_candidate_with_no_mcp_step_is_error(self) -> None:
        report = _valid_report()
        report["buildable"][0]["steps"] = [{"step": "pure local", "local": True}]
        self.assertTrue(any("no MCP tool" in m for m in _errors(report)))

    def test_duplicate_ranks_is_error(self) -> None:
        report = _valid_report()
        report["buildable"][1]["rank"] = 1
        self.assertTrue(any("rank" in m.lower() for m in _errors(report)))


class C3NotBuildableTest(unittest.TestCase):
    def test_missing_primitive_absent_is_error(self) -> None:
        report = _valid_report()
        report["not_buildable"][0]["missing_primitive"] = ""
        self.assertTrue(any("missing_primitive" in m for m in _errors(report)))

    def test_vague_missing_primitive_is_error(self) -> None:
        report = _valid_report()
        report["not_buildable"][0]["missing_primitive"] = "insufficient data"
        self.assertTrue(any("missing_primitive" in m for m in _errors(report)))

    def test_closest_tool_not_in_inventory_is_error(self) -> None:
        report = _valid_report()
        report["not_buildable"][0]["closest_tool"] = "made_up"
        self.assertTrue(any("made_up" in m for m in _errors(report)))

    def test_closest_tool_null_is_allowed(self) -> None:
        report = _valid_report()
        report["not_buildable"][0]["closest_tool"] = None
        self.assertEqual(_errors(report), [])


class C4OrchestrationTest(unittest.TestCase):
    def test_missing_orchestration_is_error(self) -> None:
        report = _valid_report()
        del report["buildable"][0]["orchestration"]
        self.assertTrue(any("orchestration" in m for m in _errors(report)))

    def test_invalid_orchestration_value_is_error(self) -> None:
        report = _valid_report()
        report["buildable"][0]["orchestration"] = "magic"
        self.assertTrue(any("orchestration" in m for m in _errors(report)))

    def test_script_without_data_access_is_error(self) -> None:
        # Scripts cannot call MCP tools at runtime; a script-orchestrated
        # candidate must say where its data comes from instead.
        report = _valid_report()
        del report["buildable"][1]["data_access"]
        self.assertTrue(any("data_access" in m for m in _errors(report)))

    def test_script_with_invalid_data_access_is_error(self) -> None:
        report = _valid_report()
        report["buildable"][1]["data_access"] = "mcp"
        self.assertTrue(any("data_access" in m for m in _errors(report)))


class C5HoldoutTest(unittest.TestCase):
    def test_missing_holdout_block_is_error(self) -> None:
        report = _valid_report()
        del report["holdout"]
        self.assertTrue(any("holdout" in m for m in _errors(report)))

    def test_empty_holdout_procedure_is_error(self) -> None:
        report = _valid_report()
        report["holdout"]["procedure"] = ""
        self.assertTrue(any("holdout" in m for m in _errors(report)))


class MutationSafetyTest(unittest.TestCase):
    def test_validate_does_not_mutate_report(self) -> None:
        report = _valid_report()
        snapshot = copy.deepcopy(report)
        validate_report(report)
        self.assertEqual(report, snapshot)


if __name__ == "__main__":
    unittest.main()
