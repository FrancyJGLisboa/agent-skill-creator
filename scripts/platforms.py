#!/usr/bin/env python3
"""
Canonical registry of agent-skills install targets.

One source of truth for platform name -> install paths and detection markers.
Consumed by `scripts/skill_registry.py`. The shell installers
(`scripts/install-template.sh`, `scripts/bootstrap.sh`) hand-maintain their own
tables for now -- they ship into generated skills and cannot import Python at
install time. A drift test in `scripts/tests/test_platforms.py` flags when the
shell tables fall out of sync with this file; a future consolidation can
generate the shell tables from this source.

Source of truth for the paths is `scripts/install-template.sh` Step
"INSTALL_DIR resolution" (the project/user case arms), since that is the script
that real users run.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Platform:
    """An install target for a generated skill.

    user_path / project_path are install destinations (where the skill directory
    lands). detect_dir is the marker whose presence indicates the platform is
    installed on the user's machine (used for auto-detection); may equal the
    parent of user_path, or differ (e.g. Windsurf installs to
    ~/.codeium/windsurf/skills but is detected by ~/.codeium/windsurf).
    """

    name: str
    user_path: str
    project_path: str
    detect_dir: str = ""


PLATFORMS: tuple[Platform, ...] = (
    Platform("claude-code", "~/.claude/skills", ".claude/skills", "~/.claude"),
    Platform("copilot", "~/.copilot/skills", ".github/skills", "~/.copilot"),
    Platform("cursor", "~/.cursor/rules", ".cursor/rules", "~/.cursor"),
    Platform("windsurf", "~/.codeium/windsurf/skills", ".windsurf/rules", "~/.codeium/windsurf"),
    Platform("cline", "~/.cline/skills", ".clinerules/skills", "~/.cline"),
    Platform("codex", "~/.agents/skills", ".agents/skills", "~/.agents"),
    Platform("gemini", "~/.gemini/skills", ".gemini/skills", "~/.gemini"),
    Platform("kiro", "~/.kiro/skills", ".kiro/skills", "~/.kiro"),
    Platform("trae", "~/.trae/rules", ".trae/rules", "~/.trae"),
    Platform("goose", "~/.config/goose/skills", ".goose/skills", "~/.config/goose"),
    Platform("opencode", "~/.config/opencode/skills", ".opencode/skills", "~/.config/opencode"),
    Platform("roo-code", "~/.roo/skills", ".roo/skills", "~/.roo"),
    Platform("kilo-code", "~/.kilocode/skills", ".kilocode/skills", "~/.kilocode"),
    Platform("factory", "~/.factory/skills", ".factory/skills", "~/.factory"),
    Platform("junie", "~/.junie/skills", ".junie/skills", "~/.junie"),
    Platform("antigravity", "~/.gemini/antigravity/skills", ".agent/skills", "~/.gemini/antigravity"),
    Platform("universal", "~/.agents/skills", ".agents/skills", "~/.agents"),
)


_BY_NAME: dict[str, Platform] = {p.name: p for p in PLATFORMS}


def list_supported_platforms() -> list[str]:
    """Names of every supported install target, in canonical order."""
    return [p.name for p in PLATFORMS]


def get_platform(name: str) -> Platform | None:
    """Look up a platform by canonical name, or None if unknown."""
    return _BY_NAME.get(name)


def user_paths() -> dict[str, str]:
    """name -> user-level install path."""
    return {p.name: p.user_path for p in PLATFORMS}


def project_paths() -> dict[str, str]:
    """name -> project-level install path."""
    return {p.name: p.project_path for p in PLATFORMS}
