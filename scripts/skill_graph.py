#!/usr/bin/env python3
"""Build and verify the normalized graph representation of an agent skill.

The file tree remains the portable package format.  This module projects that
tree into a typed intermediate representation where dependencies, constraints,
and validation gates are explicit.  Gates can then run concurrently and reuse
content-addressed results when none of their inputs changed.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Callable


SCHEMA_VERSION = 1
GRAPH_FILE = "skill.graph.json"
IGNORED_PARTS = {".git", ".skill-cache", "__pycache__", ".pytest_cache"}
TOOLING_SCRIPTS = {
    "check_pipeline.py",
    "dependency_health.py",
    "evolve.py",
    "review_staleness.py",
    "run_evals.py",
    "schema_drift.py",
    "skill_document.py",
    "staleness_check.py",
    "success_ledger.py",
}

GateExecutor = Callable[[dict, Path], dict]


def _slug(value: str) -> str:
    normalized = re.sub(r"[^a-z0-9]+", "_", value.lower()).strip("_")
    return normalized or "artifact"


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    if path.is_symlink():
        digest.update(b"SYMLINK\0")
        digest.update(os.readlink(path).encode("utf-8"))
        return digest.hexdigest()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(128 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _artifact_type(relative: Path) -> str:
    posix = relative.as_posix()
    if posix == "SKILL.md":
        return "instruction"
    if posix == "AGENTS.md":
        return "companion_instruction"
    if relative.name.endswith(".eval.md") and relative.parts[:1] == ("evals",):
        return "eval_spec"
    if len(relative.parts) >= 4 and relative.parts[:2] == ("evals", "golden"):
        if relative.name.startswith("input."):
            return "golden_input"
        if relative.name.startswith("expected."):
            return "expected_output"
    if relative.parts[:1] in (("scripts",), ("shared",)):
        return "script"
    if relative.name == "requirements.txt":
        return "dependency_manifest"
    if relative.parts[:1] == ("references",):
        return "reference"
    if relative.parts[:1] == ("assets",):
        return "asset"
    return "package_file"


def _artifact_id(relative: Path) -> str:
    if relative.as_posix() == "SKILL.md":
        return "skill_document"
    if relative.as_posix() == "AGENTS.md":
        return "agents_document"
    if relative.name == "run_pipeline.py" and relative.parts[:1] == ("scripts",):
        return "pipeline"
    if len(relative.parts) >= 4 and relative.parts[:2] == ("evals", "golden"):
        case = _slug(relative.parts[2])
        if relative.name.startswith("input."):
            return f"{case}_input"
        if relative.name.startswith("expected."):
            return f"{case}_expected"
    return _slug(relative.as_posix())


def _files(skill_dir: Path) -> list[Path]:
    return sorted(
        path
        for path in skill_dir.rglob("*")
        if path.is_file()
        and path.name != GRAPH_FILE
        and not (set(path.relative_to(skill_dir).parts) & IGNORED_PARTS)
    )


def _load_eval_specs(skill_dir: Path) -> list[dict]:
    specs: list[dict] = []
    for path in sorted((skill_dir / "evals").glob("*.eval.md")):
        text = path.read_text(encoding="utf-8")
        blocks = re.findall(r"```json\s*(.*?)```", text, re.DOTALL | re.IGNORECASE)
        if not blocks:
            continue
        try:
            spec = json.loads(blocks[-1])
        except json.JSONDecodeError:
            continue
        if isinstance(spec, dict):
            specs.append(spec)
    return specs


def _declared_workflow(skill_dir: Path) -> str | None:
    graph_path = skill_dir / GRAPH_FILE
    if not graph_path.exists():
        return None
    try:
        stored = json.loads(graph_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    workflow = stored.get("workflow", {})
    kind = workflow.get("kind") if isinstance(workflow, dict) else None
    return kind if kind in {"deterministic", "interactive", "independent"} else None


def _is_runnable_script(path: Path) -> bool:
    if path.name in TOOLING_SCRIPTS:
        return False
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return False
    return "if __name__" in text and "__main__" in text


def build_graph(skill_dir: str | Path) -> dict:
    """Project a concrete skill directory into a normalized, typed IR."""
    root = Path(skill_dir).resolve()
    if not root.is_dir():
        raise FileNotFoundError(f"not a skill directory: {root}")

    paths = _files(root)
    artifacts: list[dict] = []
    used_ids: set[str] = set()
    for path in paths:
        relative = path.relative_to(root)
        artifact_id = _artifact_id(relative)
        if artifact_id in used_ids:
            suffix = hashlib.sha256(relative.as_posix().encode("utf-8")).hexdigest()[:8]
            artifact_id = f"{artifact_id}_{suffix}"
        used_ids.add(artifact_id)
        artifacts.append(
            {
                "id": artifact_id,
                "path": path.relative_to(root).as_posix(),
                "type": _artifact_type(path.relative_to(root)),
                "sha256": _sha256(path),
            }
        )
    by_path = {item["path"]: item for item in artifacts}
    by_id = {item["id"]: item for item in artifacts}
    edges: list[dict[str, str]] = []

    specs = _load_eval_specs(root)
    run_commands = [spec.get("run", "") for spec in specs if isinstance(spec.get("run", ""), str)]
    pipeline_id = "pipeline" if "pipeline" in by_id else None
    for spec in specs:
        for case in spec.get("golden", []):
            if not isinstance(case, dict):
                continue
            case_id = _slug(str(case.get("id", "case")))
            input_path = case.get("input")
            if isinstance(input_path, str):
                artifact = by_path.get(f"evals/{input_path}")
                if artifact and pipeline_id:
                    edges.append(
                        {"from": artifact["id"], "to": pipeline_id, "relation": "consumed_by"}
                    )
            expected_paths: list[str] = []
            declared_artifacts = case.get("expected_artifacts")
            if isinstance(declared_artifacts, dict):
                expected_paths.extend(
                    value for value in declared_artifacts.values() if isinstance(value, str)
                )
            expected_path = case.get("expected")
            if isinstance(expected_path, str):
                expected_paths.append(expected_path)
            if not expected_paths:
                conventional = f"golden/{case.get('id', 'case')}/expected.json"
                if f"evals/{conventional}" in by_path:
                    expected_paths.append(conventional)
            for expected_path in expected_paths:
                artifact = by_path.get(f"evals/{expected_path}")
                if artifact and pipeline_id:
                    edges.append(
                        {"from": pipeline_id, "to": artifact["id"], "relation": "compared_against"}
                    )
                elif artifact:
                    edges.append(
                        {
                            "from": f"{case_id}_result",
                            "to": artifact["id"],
                            "relation": "compared_against",
                        }
                    )

    scripts = [path for path in paths if path.parent == root / "scripts" and path.suffix == ".py"]
    runnable = [path for path in scripts if _is_runnable_script(path)]
    declared = _declared_workflow(root)
    if declared:
        workflow_kind = declared
    elif any("run_pipeline.py" in command for command in run_commands) or len(runnable) >= 2:
        workflow_kind = "deterministic"
    else:
        workflow_kind = "independent"

    constraints = [
        {"id": "every_expected_is_reachable", "severity": "error"},
        {"id": "deterministic_multistep_has_orchestrator", "severity": "error"},
    ]
    gates = [
        {"id": "spec", "inputs": ["skill_document", "package_index"]},
        {"id": "security", "inputs": ["package"]},
        {"id": "pipeline", "inputs": ["scripts", "dependency_manifests"]},
        {"id": "eval_schema", "inputs": ["eval_specs", "golden_cases", "eval_runner"]},
    ]
    return {
        "schema_version": SCHEMA_VERSION,
        "skill": root.name,
        "workflow": {"kind": workflow_kind},
        "artifacts": artifacts,
        "edges": sorted(edges, key=lambda edge: (edge["from"], edge["to"], edge["relation"])),
        "constraints": constraints,
        "gates": gates,
    }


def check_graph(graph: dict) -> dict:
    """Evaluate graph-local constraints and return minimal repair evidence."""
    artifacts = {item["id"]: item for item in graph.get("artifacts", [])}
    errors: list[dict[str, str]] = []
    compared = {
        edge.get("to")
        for edge in graph.get("edges", [])
        if edge.get("relation") == "compared_against"
    }
    for artifact in graph.get("artifacts", []):
        if artifact.get("type") == "expected_output" and artifact.get("id") not in compared:
            errors.append(
                {
                    "constraint": "every_expected_is_reachable",
                    "artifact": artifact.get("id", "unknown"),
                    "path": artifact.get("path", "unknown"),
                    "message": "expected output is not referenced by any eval case",
                    "repair": "reference this path from a golden case or remove the unreachable file",
                }
            )

    if graph.get("workflow", {}).get("kind") == "deterministic" and "pipeline" not in artifacts:
        errors.append(
            {
                "constraint": "deterministic_multistep_has_orchestrator",
                "artifact": "pipeline",
                "path": "scripts/run_pipeline.py",
                "message": "deterministic multi-step workflow has no orchestrator",
                "repair": "add scripts/run_pipeline.py or declare workflow.kind as interactive/independent",
            }
        )
    return {"valid": not errors, "errors": errors}


def _gate_artifacts(graph: dict, gate: dict) -> list[dict]:
    selected: dict[str, dict] = {}
    for selector in gate.get("inputs", []):
        for artifact in graph.get("artifacts", []):
            artifact_type = artifact.get("type")
            matches = (
                artifact.get("id") == selector
                or selector == "package"
                or (selector == "scripts" and artifact_type == "script")
                or (selector == "dependency_manifests" and artifact_type == "dependency_manifest")
                or (selector == "eval_specs" and artifact_type == "eval_spec")
                or (selector == "golden_cases" and artifact_type in {"golden_input", "expected_output"})
                or (selector == "eval_runner" and artifact.get("path") == "scripts/run_evals.py")
            )
            if matches:
                selected[artifact["id"]] = artifact
    return sorted(selected.values(), key=lambda item: item["id"])


def _implementation_hash(gate_id: str) -> str:
    root = Path(__file__).resolve().parent
    implementations = {
        "spec": root / "validate.py",
        "security": root / "security_scan.py",
        "pipeline": root / "check_pipeline.py",
        "eval_schema": root / "run_evals_template.py",
    }
    paths = [Path(__file__), implementations[gate_id]]
    digest = hashlib.sha256()
    for path in paths:
        digest.update(path.name.encode("utf-8"))
        digest.update(path.read_bytes())
    return digest.hexdigest()


def _gate_key(graph: dict, gate: dict, skill_dir: Path) -> str:
    package_index = sorted(item["path"] for item in graph.get("artifacts", []))
    payload = {
        "schema_version": graph.get("schema_version"),
        "gate": gate,
        "implementation": _implementation_hash(gate["id"]),
        "artifacts": [
            {"id": item["id"], "sha256": item["sha256"]}
            for item in _gate_artifacts(graph, gate)
        ],
    }
    if "package_index" in gate.get("inputs", []):
        payload["package_index"] = package_index
    graph_file = skill_dir / GRAPH_FILE
    if gate["id"] == "security" and graph_file.exists():
        payload["graph_manifest_sha256"] = _sha256(graph_file)
    return hashlib.sha256(json.dumps(payload, sort_keys=True).encode("utf-8")).hexdigest()


def _default_execute(gate: dict, skill_dir: Path) -> dict:
    root = Path(__file__).resolve().parent.parent
    commands = {
        "spec": [sys.executable, str(root / "scripts" / "validate.py"), str(skill_dir), "--json"],
        "security": [sys.executable, str(root / "scripts" / "security_scan.py"), str(skill_dir), "--json"],
        "pipeline": [sys.executable, str(root / "scripts" / "check_pipeline.py"), str(skill_dir), "--json"],
    }
    if gate["id"] == "eval_schema":
        runner = skill_dir / "scripts" / "run_evals.py"
        if not runner.exists():
            return {"exit_code": 0, "stdout": "SKIPPED: no eval runner", "stderr": "", "duration_ms": 0.0}
        command = [sys.executable, str(runner), "--validate"]
    else:
        command = commands[gate["id"]]
    started = time.perf_counter()
    completed = subprocess.run(command, cwd=skill_dir, capture_output=True, text=True, check=False)
    return {
        "exit_code": completed.returncode,
        "stdout": completed.stdout,
        "stderr": completed.stderr,
        "duration_ms": round((time.perf_counter() - started) * 1000, 3),
    }


def _read_cache(cache_path: Path) -> dict:
    try:
        value = json.loads(cache_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {"version": 1, "entries": {}}
    if isinstance(value, dict) and isinstance(value.get("entries"), dict):
        return value
    return {"version": 1, "entries": {}}


def run_gates(
    skill_dir: str | Path,
    *,
    cache_path: str | Path | None = None,
    jobs: int | None = None,
    execute: GateExecutor | None = None,
) -> dict:
    """Run independent gates concurrently and cache results by input content."""
    root = Path(skill_dir).resolve()
    graph = build_graph(root)
    graph_result = check_graph(graph)
    cache_file = Path(cache_path) if cache_path else root / ".skill-cache" / "gates.json"
    cache = _read_cache(cache_file)
    executor = execute or _default_execute
    results: dict[str, dict] = {}
    pending: list[tuple[dict, str]] = []

    for gate in graph["gates"]:
        key = _gate_key(graph, gate, root)
        cached = cache["entries"].get(key)
        if isinstance(cached, dict):
            results[gate["id"]] = {**cached, "cached": True}
        else:
            pending.append((gate, key))

    def invoke(item: tuple[dict, str]) -> tuple[dict, str, dict]:
        gate, key = item
        return gate, key, executor(gate, root)

    worker_count = max(1, min(jobs or (os.cpu_count() or 1), len(pending) or 1))
    with ThreadPoolExecutor(max_workers=worker_count) as pool:
        for gate, key, result in pool.map(invoke, pending):
            stored = {**result, "cached": False}
            results[gate["id"]] = stored
            cache["entries"][key] = {key: value for key, value in result.items()}

    cache_file.parent.mkdir(parents=True, exist_ok=True)
    cache_file.write_text(json.dumps(cache, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    ordered = [results[gate["id"]] | {"id": gate["id"]} for gate in graph["gates"]]
    valid = graph_result["valid"] and all(item.get("exit_code") == 0 for item in ordered)
    return {
        "valid": valid,
        "graph": graph_result,
        "gates": ordered,
        "cached": sum(bool(item.get("cached")) for item in ordered),
    }


def _print_check(result: dict) -> None:
    for error in result["errors"]:
        print(f"  [ERROR] {error['constraint']}: {error['path']}: {error['message']}")
        print(f"          repair: {error['repair']}")
    if result["valid"]:
        print("skill graph OK")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Build and verify a normalized agent-skill graph.")
    subparsers = parser.add_subparsers(dest="command", required=True)
    for command in ("build", "check", "run"):
        child = subparsers.add_parser(command)
        child.add_argument("skill_dir")
        child.add_argument("--json", action="store_true")
    subparsers.choices["build"].add_argument("--output")
    subparsers.choices["run"].add_argument("--cache")
    subparsers.choices["run"].add_argument("--jobs", type=int)
    args = parser.parse_args(argv)

    try:
        graph = build_graph(args.skill_dir)
    except FileNotFoundError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    if args.command == "build":
        rendered = json.dumps(graph, indent=2, sort_keys=True) + "\n"
        if args.output:
            Path(args.output).write_text(rendered, encoding="utf-8")
        else:
            print(rendered, end="")
        return 0
    if args.command == "check":
        result = check_graph(graph)
        if args.json:
            print(json.dumps(result, indent=2))
        else:
            _print_check(result)
        return 0 if result["valid"] else 1

    result = run_gates(args.skill_dir, cache_path=args.cache, jobs=args.jobs)
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        for gate in result["gates"]:
            state = "CACHED" if gate["cached"] else ("PASS" if gate["exit_code"] == 0 else "FAIL")
            print(f"  [{state}] {gate['id']} ({gate['duration_ms']:.1f} ms)")
        _print_check(result["graph"])
    return 0 if result["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
