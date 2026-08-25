# Normalized Skill Graph

The five factory phases remain the user-facing progress model. They are not the
validation model. A generated skill is validated as a normalized graph of typed
artifacts, dependency edges, constraints, and gates.

## Build the IR

Run from the factory repository:

```bash
python3 scripts/skill_graph.py build <skill-dir> --output <skill-dir>/skill.graph.json
```

The graph is normalized: artifact IDs are stable, paths are relative, edges are
sorted, and every file hash is SHA-256. `skill.graph.json` is excluded while the
graph is rebuilt, so emitting the graph does not change its own digest.

The IR makes conventions explicit. For example, `run_evals.py` treats
`evals/golden/<case-id>/expected.json` as a promoted baseline even when the eval
spec says `"expected": null`. The graph emits a `compared_against` edge for that
implicit relationship.

## Blocking constraints

Two constraints are errors rather than warnings:

1. `every_expected_is_reachable` — every expected-output file must be connected
   to an eval case by a `compared_against` edge. Reference an intentional baseline
   or remove an unreachable file.
2. `deterministic_multistep_has_orchestrator` — a deterministic workflow with
   multiple runnable steps must expose `scripts/run_pipeline.py`. For a genuinely
   interactive workflow or independent CLIs, set `workflow.kind` in the emitted
   graph to `interactive` or `independent` and rebuild it after package changes.

Each failure names the constraint, artifact, path, and smallest repair. This is
the graph's minimal unsatisfied constraint set.

## Run the gates

Run all static gates through one command:

```bash
python3 scripts/skill_graph.py run <skill-dir> --jobs 4
```

The command builds and checks the graph, then executes these independent gates:

| Gate | Inputs |
|---|---|
| `spec` | SKILL.md and the package path index |
| `security` | the complete package |
| `pipeline` | scripts, shared Python, and dependency manifests |
| `eval_schema` | eval specs and golden cases |

Gate results are keyed by their normalized inputs plus the gate implementation.
Unchanged results are loaded from `<skill-dir>/.skill-cache/gates.json`; the cache
directory is runtime state and must not be committed. A validator-code change
invalidates the corresponding cache entry automatically.

Use `--json` for CI or other tools. Use `--cache <path>` to place the cache outside
the generated skill.

## What remains dynamic

The graph proves package structure, reachability, static security patterns, script
compilation, dependency declaration, and eval-schema validity. It does not replace
the representative run: semantic correctness, live APIs, subjective output quality,
and interactive agent decisions still require rollout evidence.
