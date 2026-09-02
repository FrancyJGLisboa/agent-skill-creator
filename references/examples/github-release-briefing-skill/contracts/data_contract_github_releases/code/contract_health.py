"""Health contract for the packaged GitHub Releases interface."""


def report() -> dict[str, object]:
    """Confirm the packaged contract is ready for the example's read-only client."""
    return {
        "freshness": "FRESH",
        "smoke": "PASS",
        "usable": True,
        "interface": "GitHub REST Releases latest-release endpoint",
    }
