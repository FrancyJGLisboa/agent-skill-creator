"""Tests for the normalized skill IR and content-addressed gate runner."""

from __future__ import annotations

import json
import sys
import tempfile
import time
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

from skill_graph import build_graph, check_graph, run_gates  # noqa: E402


SKILL_MD = """---
name: demo-skill
description: Demo skill used to test the normalized skill graph and its gates.
license: MIT
metadata:
  author: tester
  version: 1.0.0
---
# /demo-skill

## Gotchas

None known.
"""

STEP = "def main():\n    return 0\n\nif __name__ == '__main__':\n    main()\n"


def write_skill(base: Path, *, expected: str | None = "golden/case-1/expected.json") -> Path:
    skill = base / "demo-skill"
    (skill / "scripts").mkdir(parents=True)
    (skill / "evals" / "golden" / "case-1").mkdir(parents=True)
    (skill / "SKILL.md").write_text(SKILL_MD, encoding="utf-8")
    (skill / "scripts" / "run_pipeline.py").write_text(STEP, encoding="utf-8")
    (skill / "evals" / "golden" / "case-1" / "input.json").write_text("{}", encoding="utf-8")
    (skill / "evals" / "golden" / "case-1" / "expected.json").write_text("{}", encoding="utf-8")
    expected_json = json.dumps(expected)
    (skill / "evals" / "demo-skill.eval.md").write_text(
        "# Eval\n\n```json\n"
        + "{\"skill\":\"demo-skill\",\"run\":\"python3 scripts/run_pipeline.py "
        + "--input {input} --output {output}\",\"criteria\":[],\"golden\":["
        + "{\"id\":\"case-1\",\"input\":\"golden/case-1/input.json\","
        + "\"expected\":"
        + expected_json
        + ",\"split\":\"test\"}]}"
        + "\n```\n",
        encoding="utf-8",
    )
    return skill


class GraphEncodingTest(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.base = Path(self._tmp.name)

    def tearDown(self) -> None:
        self._tmp.cleanup()

    def test_graph_contains_typed_artifacts_edges_constraints_and_gates(self) -> None:
        graph = build_graph(write_skill(self.base))

        artifacts = {item["id"]: item for item in graph["artifacts"]}
        self.assertEqual(artifacts["skill_document"]["type"], "instruction")
        self.assertEqual(artifacts["case_1_expected"]["type"], "expected_output")
        self.assertIn(
            {"from": "case_1_input", "to": "pipeline", "relation": "consumed_by"},
            graph["edges"],
        )
        self.assertIn(
            {"from": "pipeline", "to": "case_1_expected", "relation": "compared_against"},
            graph["edges"],
        )
        self.assertEqual(
            {item["id"] for item in graph["constraints"]},
            {"every_expected_is_reachable", "deterministic_multistep_has_orchestrator"},
        )
        self.assertEqual({gate["id"] for gate in graph["gates"]}, {"spec", "security", "pipeline", "eval_schema"})

    def test_orphan_expected_output_is_a_blocking_error(self) -> None:
        skill = write_skill(self.base, expected=None)
        orphan = skill / "evals" / "golden" / "orphan" / "expected.json"
        orphan.parent.mkdir(parents=True)
        orphan.write_text("{}", encoding="utf-8")
        graph = build_graph(skill)
        result = check_graph(graph)

        self.assertFalse(result["valid"])
        self.assertTrue(any(item["constraint"] == "every_expected_is_reachable" for item in result["errors"]))

    def test_conventional_baseline_is_explicitly_reachable_when_expected_is_null(self) -> None:
        graph = build_graph(write_skill(self.base, expected=None))

        self.assertTrue(check_graph(graph)["valid"])
        self.assertIn(
            {"from": "pipeline", "to": "case_1_expected", "relation": "compared_against"},
            graph["edges"],
        )

    def test_every_declared_multi_artifact_baseline_is_reachable(self) -> None:
        skill = write_skill(self.base)
        (skill / "evals/golden/case-1/expected.md").write_text("# Report\n", encoding="utf-8")
        spec = skill / "evals/demo-skill.eval.md"
        spec.write_text(
            spec.read_text(encoding="utf-8").replace(
                '"expected":"golden/case-1/expected.json"',
                '"expected_artifacts":{".json":"golden/case-1/expected.json",'
                '".md":"golden/case-1/expected.md"}',
            ),
            encoding="utf-8",
        )
        graph = build_graph(skill)
        by_id = {artifact["id"]: artifact["path"] for artifact in graph["artifacts"]}
        compared = {
            by_id[edge["to"]] for edge in graph["edges"] if edge["relation"] == "compared_against"
        }
        self.assertTrue({
            "evals/golden/case-1/expected.json",
            "evals/golden/case-1/expected.md",
        } <= compared)
        self.assertTrue(check_graph(graph)["valid"])

    def test_deterministic_multistep_workflow_requires_orchestrator(self) -> None:
        skill = write_skill(self.base)
        (skill / "scripts" / "run_pipeline.py").unlink()
        (skill / "scripts" / "fetch.py").write_text(STEP, encoding="utf-8")
        (skill / "scripts" / "analyze.py").write_text(STEP, encoding="utf-8")
        graph = build_graph(skill)
        result = check_graph(graph)

        self.assertFalse(result["valid"])
        self.assertTrue(
            any(item["constraint"] == "deterministic_multistep_has_orchestrator" for item in result["errors"])
        )


class GateRunnerTest(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.base = Path(self._tmp.name)
        self.skill = write_skill(self.base)

    def tearDown(self) -> None:
        self._tmp.cleanup()

    def test_unchanged_gate_results_are_loaded_from_cache(self) -> None:
        calls: list[str] = []

        def execute(gate: dict, _skill: Path) -> dict:
            calls.append(gate["id"])
            return {"exit_code": 0, "stdout": "ok", "stderr": "", "duration_ms": 1.0}

        cache = self.base / "cache.json"
        first = run_gates(self.skill, cache_path=cache, execute=execute)
        second = run_gates(self.skill, cache_path=cache, execute=execute)

        self.assertEqual(len(calls), 4)
        self.assertEqual(first["cached"], 0)
        self.assertEqual(second["cached"], 4)

    def test_only_gates_that_read_changed_input_are_recomputed(self) -> None:
        calls: list[str] = []

        def execute(gate: dict, _skill: Path) -> dict:
            calls.append(gate["id"])
            return {"exit_code": 0, "stdout": "ok", "stderr": "", "duration_ms": 1.0}

        cache = self.base / "cache.json"
        run_gates(self.skill, cache_path=cache, execute=execute)
        calls.clear()
        eval_spec = self.skill / "evals" / "demo-skill.eval.md"
        eval_spec.write_text(eval_spec.read_text(encoding="utf-8") + "\n", encoding="utf-8")
        result = run_gates(self.skill, cache_path=cache, execute=execute)

        self.assertCountEqual(calls, ["security", "eval_schema"])
        self.assertEqual(result["cached"], 2)

    def test_graph_manifest_change_invalidates_security_without_self_reference(self) -> None:
        calls: list[str] = []

        def execute(gate: dict, _skill: Path) -> dict:
            calls.append(gate["id"])
            return {"exit_code": 0, "stdout": "ok", "stderr": "", "duration_ms": 1.0}

        cache = self.base / "cache.json"
        run_gates(self.skill, cache_path=cache, execute=execute)
        calls.clear()
        (self.skill / "skill.graph.json").write_text(
            '{"workflow":{"kind":"deterministic"}}\n',
            encoding="utf-8",
        )
        result = run_gates(self.skill, cache_path=cache, execute=execute)

        self.assertEqual(calls, ["security"])
        self.assertEqual(result["cached"], 3)

    def test_eval_runner_change_invalidates_every_gate_that_reads_it(self) -> None:
        calls: list[str] = []

        def execute(gate: dict, _skill: Path) -> dict:
            calls.append(gate["id"])
            return {"exit_code": 0, "stdout": "ok", "stderr": "", "duration_ms": 1.0}

        runner = self.skill / "scripts" / "run_evals.py"
        runner.write_text("print('valid')\n", encoding="utf-8")
        cache = self.base / "cache.json"
        run_gates(self.skill, cache_path=cache, execute=execute)
        calls.clear()
        runner.write_text("print('changed')\n", encoding="utf-8")
        result = run_gates(self.skill, cache_path=cache, execute=execute)

        self.assertCountEqual(calls, ["security", "pipeline", "eval_schema"])
        self.assertEqual(result["cached"], 1)

    def test_independent_gates_execute_in_parallel(self) -> None:
        def execute(_gate: dict, _skill: Path) -> dict:
            time.sleep(0.08)
            return {"exit_code": 0, "stdout": "ok", "stderr": "", "duration_ms": 80.0}

        started = time.perf_counter()
        result = run_gates(
            self.skill,
            cache_path=self.base / "parallel-cache.json",
            execute=execute,
            jobs=4,
        )
        elapsed = time.perf_counter() - started

        self.assertTrue(result["valid"])
        self.assertLess(elapsed, 0.26)


if __name__ == "__main__":
    unittest.main()
