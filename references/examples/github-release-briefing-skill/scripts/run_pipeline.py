#!/usr/bin/env python3
"""Fetch and render the latest published release for one public GitHub repository."""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

REPOSITORY = re.compile(r"^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$")


def latest_release(repository: str) -> tuple[dict, str]:
    if not REPOSITORY.fullmatch(repository):
        raise ValueError("repository must use OWNER/REPOSITORY")
    source = f"https://api.github.com/repos/{repository}/releases/latest"
    request = Request(source, headers={"Accept": "application/vnd.github+json", "User-Agent": "agent-skill-creator-release-briefing"})
    try:
        with urlopen(request, timeout=20) as response:
            return json.load(response), source
    except HTTPError as exc:
        if exc.code == 404:
            raise ValueError("repository is unavailable or has no published release") from exc
        raise RuntimeError(f"GitHub API returned HTTP {exc.code}") from exc
    except URLError as exc:
        raise RuntimeError(f"GitHub API request failed: {exc.reason}") from exc


def render(repository: str, release: dict, source: str) -> str:
    required = ("tag_name", "published_at", "html_url")
    missing = [field for field in required if not release.get(field)]
    if missing:
        raise ValueError("GitHub response missing: " + ", ".join(missing))
    title = release.get("name") or release["tag_name"]
    return f"""# Latest release: {repository}

- Tag: {release['tag_name']}
- Title: {title}
- Published: {release['published_at']}
- Release: {release['html_url']}

This is read-only release evidence. A human still approves any dependency change.

## Live source
- GitHub API: {source}
"""


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repository", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args(argv)
    try:
        release, source = latest_release(args.repository)
        Path(args.output).write_text(render(args.repository, release, source), encoding="utf-8")
    except (ValueError, RuntimeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
