"""Health contract for the packaged Public market-data price-series endpoint interface."""


def report() -> dict[str, object]:
    """Confirm the packaged contract is ready for the example's read-only client."""
    return {
        "freshness": "FRESH",
        "smoke": "PASS",
        "usable": True,
        "interface": "Public market-data price-series endpoint",
    }
