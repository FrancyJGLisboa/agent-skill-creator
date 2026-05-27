#!/usr/bin/env python3
"""Artifact opportunity detector for agent-skill-creator v5.

Public API: detect_artifact(description, domain=None)

Returns one of: "line-chart", "bar-chart", "kpi-cards", "data-table", None.

Heuristic is keyword/pattern based. No external dependencies.
"""

from __future__ import annotations


Template = str | None


TEMPORAL_KEYWORDS = (
    "trend", "over time", "over the last", "monthly", "weekly", "daily",
    "hourly", "year over year", "month over month", "history", "historical",
    "past week", "past month", "past quarter", "past year",
)


def _has_temporal_signal(text: str) -> bool:
    lowered = text.lower()
    return any(keyword in lowered for keyword in TEMPORAL_KEYWORDS)


COMPARATIVE_KEYWORDS = (
    " by ", "compare", "comparison", "across ", "per ", "breakdown",
    "ranked", "ranking",
)


def _has_comparative_signal(text: str) -> bool:
    lowered = " " + text.lower() + " "
    return any(keyword in lowered for keyword in COMPARATIVE_KEYWORDS)


KPI_KEYWORDS = (
    "kpi", "key metric", "key metrics", "scorecard", "headline number",
    "north star", "top-level", "executive summary numbers", "highlights",
    "sla scorecard",
)


def _has_kpi_signal(text: str) -> bool:
    lowered = text.lower()
    return any(keyword in lowered for keyword in KPI_KEYWORDS)


def detect_artifact(description: str, domain: str | None = None) -> Template:
    """Return the artifact template name for the given skill description, or
    None if no artifact is appropriate.
    """
    if not description or not description.strip():
        return None
    if _has_temporal_signal(description):
        return "line-chart"
    if _has_kpi_signal(description):
        return "kpi-cards"
    if _has_comparative_signal(description):
        return "bar-chart"
    return None
