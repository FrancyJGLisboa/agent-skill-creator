---
name: github-release-briefing-skill
description: >-
  Create a source-linked briefing for the latest published GitHub release of a
  public repository. Use for engineering teams tracking a dependency release;
  do not use it to publish releases or change repositories.
license: MIT
activation: /github-release-briefing-skill
metadata:
  author: agent-skill-creator
  version: 1.0.0
  created: 2026-08-27
  last_reviewed: 2026-08-27
  review_interval_days: 30
  owners: [platform-operations]
  approval_status: approved
  lifecycle: approved
  dependencies:
    - name: GitHub REST API
      url: https://api.github.com
      type: service
provenance:
  maintainer: platform-operations
  version: 1.0.0
  created: 2026-08-27
  source_references:
    - https://docs.github.com/en/rest/releases/releases#get-the-latest-release
---

# /github-release-briefing-skill

Create a current briefing for the latest published release of one public GitHub
repository. Run `scripts/run_pipeline.py` with an `OWNER/REPOSITORY` input.
The command uses GitHub's public REST endpoint, writes a Markdown briefing, and
does not authenticate, publish, modify a repository, or download release assets.

```bash
python3 scripts/run_pipeline.py --repository openai/openai-python --output release.md
```

## Required behavior

1. Reject malformed repository identifiers before any request.
2. Retrieve only the latest published release and identify its tag, title, date, and URL.
3. State clearly when a repository has no published release or is unavailable.
4. Include the GitHub API source URL so a human can inspect the result.

## Gotchas

- A GitHub "latest" release excludes drafts and prereleases according to the API's rules.
- This is dependency-awareness evidence, not a change-approval recommendation.
- Public API availability and release content can change after retrieval.

## References

- https://docs.github.com/en/rest/releases/releases#get-the-latest-release
