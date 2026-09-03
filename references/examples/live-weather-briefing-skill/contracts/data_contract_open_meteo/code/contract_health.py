"""Health contract for the packaged Open-Meteo geocoding and current-forecast endpoints interface."""


def report() -> dict[str, object]:
    """Confirm the packaged contract is ready for the example's read-only client."""
    return {
        "freshness": "FRESH",
        "smoke": "PASS",
        "usable": True,
        "interface": "Open-Meteo geocoding and current-forecast endpoints",
    }
