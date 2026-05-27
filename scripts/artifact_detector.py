#!/usr/bin/env python3
"""Artifact opportunity detector for agent-skill-creator v6.

Public API: detect_artifact(description, domain=None)

Returns one of: "line-chart", "bar-chart", "kpi-cards", "data-table", None.

Heuristic is keyword/pattern based. No external dependencies.
"""

from __future__ import annotations

import re


Template = str | None


TEMPORAL_KEYWORDS = (
    "trend", "over time", "over the last", "over the past", "monthly",
    "weekly", "daily", "hourly", "year over year", "year-over-year",
    "month over month", "month-over-month", "history", "historical",
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


# Tabular keywords use word-boundary matching to avoid false positives on
# short common substrings (e.g. "log" inside "apology", "table" inside
# "vegetable", "grid" inside "frigid").
TABULAR_KEYWORDS = (
    "listing", "log", "table", "grid", "status", "ticket", "tickets",
    "invoice", "invoices", "inventory", "shipment", "shipments", "fleet",
    "snapshot", "audit results", "line items", "findings",
)

_TABULAR_PATTERN = re.compile(
    r"\b(" + "|".join(re.escape(k) for k in TABULAR_KEYWORDS) + r")\b",
    re.IGNORECASE,
)


def _has_tabular_signal(text: str) -> bool:
    return bool(_TABULAR_PATTERN.search(text))


def detect_artifact(description: str, domain: str | None = None) -> Template:
    """Return the artifact template name for the given skill description, or
    None if no artifact is appropriate.

    Precedence (load-bearing, not accidental): temporal > KPI > tabular >
    comparative > none. Rationale: time series carry the most information
    per pixel, so they win when a temporal cadence is mentioned even if
    other signals also fire. KPI cards convey headline numbers that
    summarize rather than itemize. Tabular beats comparative because
    structured rows of records read more naturally as a table than as
    bars. Comparative is the most generic positive signal and acts as a
    fallback.

    To add a new template in v6.1+: define KEYWORDS, a _has_X_signal
    helper, and insert an `if` branch here at the priority that matches
    the new template's information density relative to the others.
    """
    if not description or not description.strip():
        return None
    # Time series outranks all other signals.
    if _has_temporal_signal(description):
        return "line-chart"
    # Headline numbers outrank categorical or tabular framings.
    if _has_kpi_signal(description):
        return "kpi-cards"
    # Structured rows of records prefer a table over bars.
    if _has_tabular_signal(description):
        return "data-table"
    # Generic comparison fallback.
    if _has_comparative_signal(description):
        return "bar-chart"
    return None
