# Eval Spec: github-release-briefing-skill

Each rollout calls GitHub's public latest-release endpoint. The test asserts
stable output structure because release values are expected to change.

```json
{
  "skill": "github-release-briefing-skill",
  "run": "python3 scripts/run_pipeline.py --input {input} --output {output}",
  "criteria": [
    {"id": "title", "text": "Names the requested repository", "type": "command", "cmd": "grep -q '^# Latest release:' {output}"},
    {"id": "release-fields", "text": "Contains tag, publication date, and release URL", "type": "command", "cmd": "grep -q '^- Tag:' {output} && grep -q '^- Published:' {output} && grep -q '^- Release: https://github.com/' {output}"},
    {"id": "provenance", "text": "Includes the GitHub REST source URL", "type": "command", "cmd": "grep -q 'GitHub API: https://api.github.com/repos/' {output}"}
  ],
  "golden": [
    {"id": "openai-python", "input": "golden/openai-python/input.txt", "expected": null, "split": "val", "expected_status": "pending-first-green", "compare": "none"},
    {"id": "requests", "input": "golden/requests/input.txt", "expected": null, "split": "val", "expected_status": "pending-first-green", "compare": "none"},
    {"id": "flask", "input": "golden/flask/input.txt", "expected": null, "split": "test", "expected_status": "pending-first-green", "compare": "none"}
  ]
}
```
