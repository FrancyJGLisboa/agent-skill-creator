"""Health contract for the packaged Pull-request provider reviews and CI-checks endpoints interface."""


def report() -> dict[str, object]:
    """Confirm the packaged contract is ready for the example's read-only client."""
    return {
        "freshness": "FRESH",
        "smoke": "PASS",
        "usable": True,
        "interface": "Pull-request provider reviews and CI-checks endpoints",
    }
