#!/usr/bin/env python3
"""Artifact opportunity detector for agent-skill-creator v5.

Public API: detect_artifact(description, domain=None)

Returns one of: "line-chart", "bar-chart", "kpi-cards", "data-table", None.

Heuristic is keyword/pattern based. No external dependencies.
"""

from __future__ import annotations


Template = str | None


def detect_artifact(description: str, domain: str | None = None) -> Template:
    """Return the artifact template name for the given skill description, or
    None if no artifact is appropriate.

    Args:
        description: The user's workflow description (natural language).
        domain: Optional domain hint from Phase 1 Discovery (unused in v5.0).

    Returns:
        One of {"line-chart", "bar-chart", "kpi-cards", "data-table"} or None.
    """
    if not description or not description.strip():
        return None
    return None  # Stub: subsequent tasks implement signals.
