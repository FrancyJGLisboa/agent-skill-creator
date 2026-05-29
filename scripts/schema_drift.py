#!/usr/bin/env python3
"""
Schema drift check for declared API endpoints.

Each `metadata.schema_expectations` entry declares a URL, method, and the keys
the response is expected to carry. This module parses the declarations out of
SKILL.md frontmatter and, given them, GETs each URL and compares the
top-level JSON keys to the expected set.
"""

from __future__ import annotations

import json
from urllib.error import URLError
from urllib.request import Request, urlopen

from skill_document import SkillDoc

HTTP_TIMEOUT_SECONDS = 10
_USER_AGENT = "agent-skill-staleness-check/1.0"


def parse_schema_expectations(doc: SkillDoc) -> list[dict]:
    """Extract schema_expectations from the skill document.

    Each expectation has: url, method (default GET), expected_keys (list of
    strings). The simple list parser in SkillDoc doesn't carry sub-lists, so
    we re-walk the frontmatter to recover expected_keys.
    """
    if doc.frontmatter is None:
        return []
    return _parse_expectations_from_frontmatter(doc.frontmatter)


def _parse_expectations_from_frontmatter(frontmatter: str) -> list[dict]:
    """Walk YAML-ish frontmatter to recover schema_expectations entries with
    their expected_keys sub-lists."""
    lines = frontmatter.split("\n")
    expectations: list[dict] = []
    current: dict | None = None
    in_metadata = False
    in_schema = False
    in_expected_keys = False

    for line in lines:
        stripped = line.strip()

        if not in_metadata:
            if stripped.startswith("metadata:"):
                in_metadata = True
            continue

        # Left metadata block on an unindented non-blank line.
        if line and line[0] != " " and line[0] != "\t" and stripped:
            break

        if not in_schema:
            if stripped.startswith("schema_expectations:"):
                in_schema = True
            continue

        if stripped.startswith("- url:") or stripped.startswith("- method:"):
            if current is not None:
                expectations.append(current)
            in_expected_keys = False
            current = {"url": "", "method": "GET", "expected_keys": []}
            if stripped.startswith("- url:"):
                current["url"] = stripped.split(":", 1)[1].strip()
            elif stripped.startswith("- method:"):
                current["method"] = stripped.split(":", 1)[1].strip().upper()
        elif current is not None:
            if stripped.startswith("url:"):
                current["url"] = stripped.split(":", 1)[1].strip()
            elif stripped.startswith("method:"):
                current["method"] = stripped.split(":", 1)[1].strip().upper()
            elif stripped.startswith("expected_keys:"):
                in_expected_keys = True
            elif in_expected_keys and stripped.startswith("- "):
                current["expected_keys"].append(stripped[2:].strip())
            elif not stripped.startswith("-") and ":" in stripped:
                key = stripped.split(":")[0].strip()
                if key not in ("url", "method", "expected_keys"):
                    in_expected_keys = False

    if current is not None:
        expectations.append(current)

    return expectations


def check_schema_drift(expectations: list[dict]) -> list[dict]:
    """
    GET each declared endpoint and compare top-level JSON keys against
    expected_keys. Reports missing keys (error), new keys (info), or full
    match (info).
    """
    issues: list[dict] = []

    for exp in expectations:
        url = exp.get("url", "").strip()
        method = exp.get("method", "GET").upper()
        expected_keys = exp.get("expected_keys", [])

        if not url:
            continue
        if not url.startswith(("http://", "https://")):
            issues.append({
                "level": "warning",
                "message": f"Schema check skipped for non-HTTP URL: {url}",
                "detail": "Only HTTP/HTTPS URLs are supported.",
            })
            continue
        if not expected_keys:
            issues.append({
                "level": "info",
                "message": f"No expected_keys declared for {url}",
                "detail": "Skipping drift check.",
            })
            continue

        try:
            req = Request(url, method=method)
            req.add_header("User-Agent", _USER_AGENT)
            req.add_header("Accept", "application/json")
            with urlopen(req, timeout=HTTP_TIMEOUT_SECONDS) as resp:
                body = resp.read().decode("utf-8", errors="replace")
                data = json.loads(body)

                if not isinstance(data, dict):
                    issues.append({
                        "level": "warning",
                        "message": f"Response from {url} is not a JSON object",
                        "detail": f"Got {type(data).__name__}, expected dict. "
                                  "Cannot compare keys.",
                    })
                    continue

                actual_keys = set(data.keys())
                expected_set = set(expected_keys)
                missing = expected_set - actual_keys
                new_keys = actual_keys - expected_set

                if missing:
                    issues.append({
                        "level": "error",
                        "message": f"Schema drift: missing keys from {url}",
                        "detail": f"Expected keys not found: {sorted(missing)}. "
                                  "The API response structure may have changed.",
                    })
                if new_keys:
                    issues.append({
                        "level": "info",
                        "message": f"Schema drift: new keys in {url}",
                        "detail": f"Unexpected keys found: {sorted(new_keys)}. "
                                  "The API may have added new fields.",
                    })
                if not missing and not new_keys:
                    issues.append({
                        "level": "info",
                        "message": f"Schema matches for {url}",
                        "detail": f"All {len(expected_keys)} expected keys present, "
                                  "no unexpected keys.",
                    })

        except json.JSONDecodeError:
            issues.append({
                "level": "error",
                "message": f"Response from {url} is not valid JSON",
                "detail": "Cannot perform schema drift check.",
            })
        except URLError as exc:
            issues.append({
                "level": "error",
                "message": f"Cannot reach {url} for schema check",
                "detail": f"Error: {exc.reason}",
            })
        except Exception as exc:
            issues.append({
                "level": "error",
                "message": f"Schema check failed for {url}",
                "detail": f"Error: {exc}",
            })

    return issues
