#!/usr/bin/env python3
"""
Dependency health check for a skill.

Issues an HTTP HEAD to each declared dependency URL and reports whether the
endpoint is reachable, returning a normal status, or has moved / errored.
Non-HTTP URLs and URLs without a scheme are reported as skipped.
"""

from __future__ import annotations

from urllib.error import URLError
from urllib.request import Request, urlopen

HTTP_TIMEOUT_SECONDS = 10
_USER_AGENT = "agent-skill-staleness-check/1.0"


def check_dependency_health(dependencies: list[dict]) -> list[dict]:
    """
    Probe each dependency's URL. Returns a list of issue dicts (level, message,
    detail). Status thresholds:
        2xx-3xx -> info "healthy"
        4xx     -> warning "client error / may have moved"
        5xx     -> error  "server error"
        URLError, other -> error "unreachable / check failed"
    """
    issues: list[dict] = []

    for dep in dependencies:
        url = dep.get("url", "").strip()
        name = dep.get("name", url)

        if not url:
            issues.append({
                "level": "warning",
                "message": f"Dependency '{name}' has no URL",
                "detail": "Cannot check health without a URL.",
            })
            continue

        if not url.startswith(("http://", "https://")):
            issues.append({
                "level": "warning",
                "message": f"Dependency '{name}' has non-HTTP URL",
                "detail": f"Skipping health check for: {url}",
            })
            continue

        try:
            req = Request(url, method="HEAD")
            req.add_header("User-Agent", _USER_AGENT)
            with urlopen(req, timeout=HTTP_TIMEOUT_SECONDS) as resp:
                status = resp.status
                if 200 <= status < 400:
                    issues.append({
                        "level": "info",
                        "message": f"Dependency '{name}' is healthy",
                        "detail": f"HTTP {status} from {url}",
                    })
                elif 400 <= status < 500:
                    issues.append({
                        "level": "warning",
                        "message": f"Dependency '{name}' returned client error",
                        "detail": f"HTTP {status} from {url}. "
                                  "The endpoint may have moved or require authentication.",
                    })
                else:
                    issues.append({
                        "level": "error",
                        "message": f"Dependency '{name}' returned server error",
                        "detail": f"HTTP {status} from {url}",
                    })
        except URLError as exc:
            issues.append({
                "level": "error",
                "message": f"Dependency '{name}' is unreachable",
                "detail": f"Failed to connect to {url}: {exc.reason}",
            })
        except Exception as exc:
            issues.append({
                "level": "error",
                "message": f"Dependency '{name}' check failed",
                "detail": f"Error checking {url}: {exc}",
            })

    return issues
