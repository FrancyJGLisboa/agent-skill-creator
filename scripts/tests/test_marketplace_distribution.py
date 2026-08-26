"""Governed, provider-neutral distribution planning and certification tests."""

from __future__ import annotations

import sys
from datetime import datetime, timezone
from pathlib import Path

import pytest

ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

import marketplace_distribution as distribution  # noqa: E402
from platforms import list_supported_platforms  # noqa: E402


NOW = datetime(2026, 8, 25, 12, tzinfo=timezone.utc)


def evidence(platform: str = "codex", version: str = "1.2.3") -> dict[str, object]:
    return {
        "platform": platform,
        "skill_version": version,
        "adapter": distribution.adapter_for(platform)["name"],
        "adapter_version": distribution.ADAPTER_VERSION,
        "checks": [
            {"name": "artifact-shape", "passed": True},
            {"name": "representative-load", "passed": True},
        ],
    }


@pytest.mark.parametrize("scope", ["user", "project"])
def test_adapter_resolves_canonical_destination(scope: str, tmp_path: Path) -> None:
    home, project = tmp_path / "home", tmp_path / "project"
    destination = distribution.resolve_destination("codex", scope, "report-skill", home=home, project_root=project)
    expected_root = home / ".agents/skills" if scope == "user" else project / ".agents/skills"
    assert destination == (expected_root / "report-skill").resolve()


@pytest.mark.parametrize("name", ["../escape", "bad/name", ".", "Skill Name"])
def test_adapter_rejects_unsafe_skill_names(name: str, tmp_path: Path) -> None:
    with pytest.raises(distribution.DistributionError):
        distribution.resolve_destination("codex", "user", name, home=tmp_path, project_root=tmp_path)


def test_adapter_rejects_unknown_platform_and_scope(tmp_path: Path) -> None:
    with pytest.raises(distribution.DistributionError, match="platform"):
        distribution.resolve_destination("unknown", "user", "skill", home=tmp_path, project_root=tmp_path)
    with pytest.raises(distribution.DistributionError, match="scope"):
        distribution.resolve_destination("codex", "system", "skill", home=tmp_path, project_root=tmp_path)


def test_adapter_registry_uses_every_canonical_platform() -> None:
    assert [distribution.adapter_for(name)["platform"] for name in list_supported_platforms()] == list_supported_platforms()


def test_copilot_alias_is_canonicalized_in_plan_and_adapter(tmp_path: Path) -> None:
    assert distribution.adapter_for("copilot")["platform"] == "github-copilot"
    plan = distribution.build_install_plan(
        skill_name="report-skill", skill_version="1.2.3",
        platforms=["copilot", "github-copilot"], scope="project",
        source="./skills/report-skill", release_ref=None, remote=False,
        home=tmp_path / "home", project_root=tmp_path / "project",
    )
    assert [target["platform"] for target in plan["targets"]] == ["github-copilot"]
    assert plan["targets"][0]["destination"].endswith("/.github/skills/report-skill")


def test_copilot_alias_is_canonicalized_in_certification() -> None:
    proof = evidence("github-copilot")
    record = distribution.certify_compatibility(
        platform="copilot", skill_version="1.2.3",
        declared_platforms=["github-copilot"], evidence=proof, timestamp=NOW,
    )
    assert record["platform"] == "github-copilot"


def test_adapter_install_plan_requires_exact_remote_release(tmp_path: Path) -> None:
    with pytest.raises(distribution.DistributionError, match="immutable"):
        distribution.build_install_plan(
            skill_name="report-skill", skill_version="1.2.3", platforms=["codex"],
            scope="user", source="https://example.test/skills.git", release_ref="main",
            remote=True, home=tmp_path / "home", project_root=tmp_path / "project",
        )


def test_adapter_install_plan_rejects_tag_version_mismatch(tmp_path: Path) -> None:
    with pytest.raises(distribution.DistributionError, match="version"):
        distribution.build_install_plan(
            skill_name="report-skill", skill_version="1.2.3", platforms=["codex"],
            scope="user", source="https://example.test/skills.git", release_ref="v1.2.2",
            remote=True, home=tmp_path / "home", project_root=tmp_path / "project",
        )


def test_adapter_install_plan_is_deterministic_and_describes_native_and_adapted_tiers(tmp_path: Path) -> None:
    kwargs = dict(
        skill_name="report-skill", skill_version="1.2.3",
        platforms=["cursor", "codex", "windsurf"], scope="project",
        source="https://example.test/skills.git", release_ref="v1.2.3", remote=True,
        home=tmp_path / "home", project_root=tmp_path / "project",
    )
    plan = distribution.build_install_plan(**kwargs)
    assert plan == distribution.build_install_plan(**kwargs)
    assert [item["platform"] for item in plan["targets"]] == ["cursor", "windsurf", "codex"]
    assert plan["release_ref"] == "v1.2.3" and plan["mutates"] is False
    assert next(item for item in plan["targets"] if item["platform"] == "codex")["tier"] == "native"
    assert next(item for item in plan["targets"] if item["platform"] == "cursor")["artifacts"] == ["SKILL.md", "report-skill.mdc"]


def test_local_adapter_plan_does_not_require_release_but_keeps_version(tmp_path: Path) -> None:
    plan = distribution.build_install_plan(
        skill_name="report-skill", skill_version="1.2.3", platforms=["codex"],
        scope="user", source="./skills/report-skill", release_ref=None, remote=False,
        home=tmp_path / "home", project_root=tmp_path / "project",
    )
    assert plan["release_ref"] is None and plan["skill_version"] == "1.2.3"


def test_certification_records_explicit_passing_evidence() -> None:
    record = distribution.certify_compatibility(
        platform="codex", skill_version="1.2.3", declared_platforms=["codex", "cursor"],
        evidence=evidence(), timestamp=NOW,
    )
    assert record == {
        "platform": "codex", "skill_version": "1.2.3", "passed": True,
        "certified_at": "2026-08-25T12:00:00Z", "adapter": "native-skill",
        "adapter_version": distribution.ADAPTER_VERSION,
        "checks": ["artifact-shape", "representative-load"],
    }


@pytest.mark.parametrize(
    ("change", "message"),
    [
        ({"platform": "unknown"}, "platform"),
        ({"skill_version": "1.2.2"}, "version"),
        ({"checks": []}, "check"),
        ({"checks": [{"name": "load", "passed": False}]}, "failed"),
        ({"adapter_version": "0"}, "adapter"),
    ],
)
def test_certification_rejects_unknown_mismatch_failed_or_missing_evidence(change: dict[str, object], message: str) -> None:
    proof = evidence()
    proof.update(change)
    with pytest.raises(distribution.DistributionError, match=message):
        distribution.certify_compatibility(
            platform="codex", skill_version="1.2.3", declared_platforms=["codex"],
            evidence=proof, timestamp=NOW,
        )


def test_certification_rejects_unsupported_claim() -> None:
    with pytest.raises(distribution.DistributionError, match="declared"):
        distribution.certify_compatibility(
            platform="codex", skill_version="1.2.3", declared_platforms=["cursor"],
            evidence=evidence(), timestamp=NOW,
        )
