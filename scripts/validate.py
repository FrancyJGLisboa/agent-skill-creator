#!/usr/bin/env python3
"""
Spec Compliance Validator for the Agent Skills Open Standard.

Validates a skill directory against the Agent Skills Open Standard by checking
SKILL.md existence, frontmatter structure, naming conventions, and best practices.

Usage:
    python3 scripts/validate.py path/to/skill/
    python3 scripts/validate.py path/to/skill/ --json

Exit codes:
    0 - Valid (no errors, may have warnings)
    1 - Invalid (one or more errors found)
"""

import json
import re
import sys
from pathlib import Path

from skill_document import SkillDoc
from marketplace_discovery import DiscoveryError, require_operating_contract
from structured_interview import InterviewError, load as load_interview, readiness_report


# --- Constants ---

MAX_NAME_LENGTH = 64
MAX_DESCRIPTION_LENGTH = 1024
MAX_BODY_LINES_WARNING = 500

# Heading that must carry the skill's environment-specific facts. Warning-level:
# the section is required doctrine, but a missing heading should not block delivery
# of an otherwise-working skill.
GOTCHAS_HEADING_PATTERN = re.compile(r"^[ \t]{0,3}#{1,6}[ \t]+gotchas\b", re.IGNORECASE | re.MULTILINE)

# --- Run-vs-read labeling ---
#
# A skill bundles two kinds of file the agent must treat differently: scripts it
# should EXECUTE, and references it should READ. Left to inference, an agent will
# sometimes read a script as documentation (losing the determinism the script
# existed to provide) or try to execute a reference. The directory split alone
# does not say which is which -- the SKILL.md has to.
#
# This is a heuristic on a natural-language body, so it is warning-level and
# deliberately generous: a mention counts as labeled if an action verb appears on
# its line or the line before. Shell fences are self-evidently executable and
# table rows carry their verb in the column header, so both are skipped.
SCRIPT_MENTION_PATTERN = re.compile(r"(?<![\w/])scripts/[\w./-]+\.(?:py|sh|ps1|bat)")
REFERENCE_MENTION_PATTERN = re.compile(r"(?<![\w/])references/[\w./-]+\.md")
RUN_VERB_PATTERN = re.compile(
    r"\b(run|runs|running|execute|executes|executing|invoke|invokes|call|calls|"
    r"python3?|bash|sh|copy|copies|emit|emits|write|writes|generate|generates)\b",
    re.IGNORECASE,
)
READ_VERB_PATTERN = re.compile(
    r"\b(read|reads|see|consult|consults|refer|refers|reference|guide|guidance|"
    r"documented|documents|described|describes|detail|details|listed|explains)\b",
    re.IGNORECASE,
)
SHELL_FENCE_PATTERN = re.compile(r"^\s*```\s*(\w+)?")
SHELL_FENCE_LANGUAGES = {"bash", "sh", "shell", "console", "zsh", "powershell", "ps1"}
MAX_REPORTED_UNLABELED = 4

# Pattern for valid skill names: lowercase letters, numbers, hyphens
NAME_PATTERN = re.compile(r"^[a-z0-9]([a-z0-9-]*[a-z0-9])?$")
CONSECUTIVE_HYPHENS_PATTERN = re.compile(r"--")

# Pattern for YYYY-MM-DD date format
DATE_FORMAT_PATTERN = re.compile(r"^\d{4}-\d{2}-\d{2}$")

# Pattern for local file references in markdown: [text](path) excluding http/https/mailto/#
LOCAL_LINK_PATTERN = re.compile(
    r"\[([^\]]*)\]\(([^)]+)\)"
)


def _extract_local_links(body: str) -> list[str]:
    """
    Extract local file paths referenced in markdown links within the body.

    Filters out URLs (http, https, mailto) and anchor links (#).

    Args:
        body: The markdown body text.

    Returns:
        List of relative file paths referenced in the body.
    """
    paths: list[str] = []
    for match in LOCAL_LINK_PATTERN.finditer(body):
        target = match.group(2).strip()
        # Skip external URLs and anchors
        if target.startswith(("http://", "https://", "mailto:", "#")):
            continue
        # Strip any anchor fragment from the path
        if "#" in target:
            target = target.split("#")[0]
        if target:
            paths.append(target)
    return paths


def _find_unlabeled_mentions(body: str) -> tuple[list[str], list[str]]:
    """
    Find file mentions that never say whether to run the file or read it.

    Walks the body line by line, skipping shell code fences (self-evidently
    executable) and markdown table rows (the verb lives in the column header). A
    mention is considered labeled when an action verb appears on its own line or
    the line immediately before it, which is where "Run `scripts/x.py`" and
    "See `references/y.md`" both put it.

    Args:
        body: The SKILL.md body, frontmatter already stripped.

    Returns:
        (unlabeled_scripts, unlabeled_references), each formatted "line N: path".
    """
    lines = body.split("\n")
    unlabeled_scripts: list[str] = []
    unlabeled_references: list[str] = []
    in_shell_fence = False
    in_fence = False
    previous_prose = ""

    for index, line in enumerate(lines):
        fence = SHELL_FENCE_PATTERN.match(line)
        if fence:
            if in_fence:
                in_fence = False
                in_shell_fence = False
            else:
                in_fence = True
                in_shell_fence = (fence.group(1) or "").lower() in SHELL_FENCE_LANGUAGES
            continue

        if in_shell_fence or line.lstrip().startswith("|"):
            continue

        # The paths themselves must not supply the verb: "api-guide.md" contains
        # "guide", "scripts/run_pipeline.py" contains "run". Strip every mention
        # before looking for an action word.
        stripped = REFERENCE_MENTION_PATTERN.sub(" ", SCRIPT_MENTION_PATTERN.sub(" ", line))
        # Look back to the nearest non-blank line, so a blank line between the
        # instruction and the path does not hide the verb.
        context = previous_prose + " " + stripped
        if stripped.strip():
            previous_prose = stripped

        if not RUN_VERB_PATTERN.search(context):
            for match in SCRIPT_MENTION_PATTERN.finditer(line):
                unlabeled_scripts.append(f"line {index + 1}: {match.group()}")

        if not READ_VERB_PATTERN.search(context):
            for match in REFERENCE_MENTION_PATTERN.finditer(line):
                unlabeled_references.append(f"line {index + 1}: {match.group()}")

    return unlabeled_scripts, unlabeled_references


def _format_unlabeled(kind: str, directive: str, found: list[str]) -> str:
    """Build the warning text for one class of unlabeled mention."""
    shown = ", ".join(found[:MAX_REPORTED_UNLABELED])
    if len(found) > MAX_REPORTED_UNLABELED:
        shown += f", and {len(found) - MAX_REPORTED_UNLABELED} more"
    return (
        f"{len(found)} {kind} mention(s) do not say what to do with the file "
        f"({shown}). Say \"{directive}\" explicitly so the agent does not have to "
        f"guess whether to execute it or read it."
    )


def validate_skill(skill_path: str) -> dict:
    """
    Validate a skill directory against the Agent Skills Open Standard.

    Performs both required checks (errors) and recommended checks (warnings).

    Args:
        skill_path: Path to the skill directory to validate.

    Returns:
        Dictionary with keys:
            - ``valid`` (bool): True if no errors were found.
            - ``errors`` (list[str]): List of error messages (must fix).
            - ``warnings`` (list[str]): List of warning messages (should fix).
    """
    errors: list[str] = []
    warnings: list[str] = []

    skill_dir = Path(skill_path).resolve()

    # --- Check: directory exists ---
    if not skill_dir.exists():
        errors.append(f"Path does not exist: {skill_dir}")
        return {"valid": False, "errors": errors, "warnings": warnings}

    if not skill_dir.is_dir():
        errors.append(f"Path is not a directory: {skill_dir}")
        return {"valid": False, "errors": errors, "warnings": warnings}

    # --- Check: SKILL.md exists ---
    skill_md = skill_dir / "SKILL.md"
    if not skill_md.exists():
        errors.append("SKILL.md not found in skill directory")
        return {"valid": False, "errors": errors, "warnings": warnings}

    # --- Read SKILL.md ---
    try:
        content = skill_md.read_text(encoding="utf-8")
    except Exception as exc:
        errors.append(f"Could not read SKILL.md: {exc}")
        return {"valid": False, "errors": errors, "warnings": warnings}

    # --- Check: frontmatter exists ---
    if not content.startswith("---"):
        errors.append("SKILL.md must start with '---' frontmatter delimiter")
        return {"valid": False, "errors": errors, "warnings": warnings}

    doc = SkillDoc.from_text(content)
    body = doc.body

    if doc.frontmatter is None:
        errors.append("SKILL.md frontmatter is not properly closed (missing closing '---')")
        return {"valid": False, "errors": errors, "warnings": warnings}

    discovery_path = skill_dir / "discovery.json"
    if not discovery_path.exists():
        errors.append(
            "discovery.json is required and must define question, trigger, decision, "
            "evidence, and success_measure"
        )
    else:
        try:
            discovery = json.loads(discovery_path.read_text(encoding="utf-8"))
            if not isinstance(discovery, dict):
                raise DiscoveryError("discovery.json must contain a JSON object")
            require_operating_contract({
                "name": doc.name or skill_dir.name,
                "version": str(doc.subfield("metadata", "version") or ""),
                "discovery": discovery,
            })
            if "semantic_contract" not in discovery:
                warnings.append(
                    "legacy discovery.json has no semantic_contract; treated as "
                    "{\"applies\": false}. Add the field before the next release."
                )
        except (json.JSONDecodeError, OSError, DiscoveryError) as exc:
            errors.append(f"invalid discovery.json decision contract: {exc}")

    # Generated skills preserve the evidence-backed intake that authorized
    # generation. Third-party skills remain valid without this factory artifact,
    # but once interview.json is present it must be structurally valid and ready.
    interview_path = skill_dir / "interview.json"
    if interview_path.exists():
        try:
            interview = load_interview(interview_path)
            interview_report = readiness_report(interview)
            if not interview_report["ready"]:
                fields = ", ".join(interview_report["blocking_fields"])
                errors.append(f"interview.json is not ready for generation; unresolved: {fields}")
        except InterviewError as exc:
            errors.append(f"invalid interview.json: {exc}")

    # --- Check: name field ---
    name_value = doc.name
    if name_value is None:
        errors.append("'name' field is missing from frontmatter")
    else:
        name_value = name_value.strip()
        if len(name_value) == 0:
            errors.append("'name' field is empty")
        elif len(name_value) > MAX_NAME_LENGTH:
            errors.append(
                f"'name' field exceeds {MAX_NAME_LENGTH} characters "
                f"(found {len(name_value)})"
            )
        else:
            # Validate name format
            if not NAME_PATTERN.match(name_value):
                errors.append(
                    f"'name' field must contain only lowercase letters, numbers, "
                    f"and hyphens (found: '{name_value}')"
                )
            if name_value.startswith("-"):
                errors.append(f"'name' must not start with a hyphen (found: '{name_value}')")
            if name_value.endswith("-"):
                errors.append(f"'name' must not end with a hyphen (found: '{name_value}')")
            if CONSECUTIVE_HYPHENS_PATTERN.search(name_value):
                errors.append(
                    f"'name' must not contain consecutive hyphens (found: '{name_value}')"
                )

            # --- Check: directory name matches name field ---
            dir_name = skill_dir.name
            if dir_name != name_value:
                errors.append(
                    f"Directory name '{dir_name}' does not match 'name' field "
                    f"'{name_value}' in frontmatter"
                )

    # --- Check: description field ---
    description_value = doc.description
    if description_value is None:
        errors.append("'description' field is missing from frontmatter")
    else:
        description_value = description_value.strip()
        if len(description_value) == 0:
            errors.append("'description' field is empty")
        elif len(description_value) > MAX_DESCRIPTION_LENGTH:
            errors.append(
                f"'description' field exceeds {MAX_DESCRIPTION_LENGTH} characters "
                f"(found {len(description_value)})"
            )

    # --- Check: -cskill suffix is deprecated ---
    if name_value is not None and name_value.endswith("-cskill"):
        errors.append(
            f"'name' uses the deprecated '-cskill' suffix. "
            f"Use '-skill' instead (found: '{name_value}')"
        )

    # --- Warnings ---

    # Naming convention: -skill suffix (or -suite for suites)
    if name_value is not None and len(name_value) > 0:
        if not name_value.endswith("-skill") and not name_value.endswith("-suite"):
            warnings.append(
                f"'name' should end with '-skill' for discoverability "
                f"(found: '{name_value}')"
            )

    # Body line count
    if body is not None:
        body_lines = body.split("\n")
        body_line_count = len(body_lines)
        if body_line_count > MAX_BODY_LINES_WARNING:
            warnings.append(
                f"SKILL.md body exceeds {MAX_BODY_LINES_WARNING} lines "
                f"({body_line_count} lines). Consider moving content to references/."
            )

        # Gotchas section
        if not GOTCHAS_HEADING_PATTERN.search(body):
            warnings.append(
                "SKILL.md body has no '## Gotchas' section. This is where the "
                "environment-specific facts that defy reasonable assumptions live — "
                "the part a model cannot supply on its own. Write 'None known' if "
                "the skill genuinely has none."
            )

        # Run-vs-read labeling
        unlabeled_scripts, unlabeled_references = _find_unlabeled_mentions(body)
        if unlabeled_scripts:
            warnings.append(
                _format_unlabeled("script", "Run `python3 scripts/x.py`", unlabeled_scripts)
            )
        if unlabeled_references:
            warnings.append(
                _format_unlabeled("reference", "Read `references/x.md` for ...", unlabeled_references)
            )

    # license field
    if not doc.has_field("license"):
        warnings.append("'license' field is missing from frontmatter")

    # metadata field
    if not doc.has_field("metadata"):
        warnings.append("'metadata' field is missing from frontmatter")
    else:
        if not doc.has_subfield("metadata", "author"):
            warnings.append("'metadata.author' sub-field is missing")
        if not doc.has_subfield("metadata", "version"):
            warnings.append("'metadata.version' sub-field is missing")

        # Temporal metadata validation (optional, warnings only)
        created_val = doc.subfield("metadata", "created")
        reviewed_val = doc.subfield("metadata", "last_reviewed")
        interval_val = doc.subfield("metadata", "review_interval_days")

        if created_val and not DATE_FORMAT_PATTERN.match(created_val.strip()):
            warnings.append(
                f"'metadata.created' should be YYYY-MM-DD format (found: '{created_val}')"
            )
        if reviewed_val and not DATE_FORMAT_PATTERN.match(reviewed_val.strip()):
            warnings.append(
                f"'metadata.last_reviewed' should be YYYY-MM-DD format (found: '{reviewed_val}')"
            )
        if interval_val:
            try:
                int(interval_val.strip())
            except ValueError:
                warnings.append(
                    f"'metadata.review_interval_days' should be an integer (found: '{interval_val}')"
                )

        has_temporal = bool(created_val or reviewed_val or interval_val)
        if not has_temporal:
            warnings.append(
                "Consider adding temporal metadata (metadata.created, metadata.last_reviewed, "
                "metadata.review_interval_days) for staleness tracking"
            )

    # AGENTS.md companion file
    agents_md = skill_dir / "AGENTS.md"
    if not agents_md.exists():
        warnings.append(
            "AGENTS.md not found. Adding an AGENTS.md companion file maximizes "
            "cross-tool discoverability (read by 15+ tools including Codex CLI, "
            "Cursor, Roo Code, Kilo Code, Kiro, Goose, and others)."
        )

    # activation field (harness factory v1.1)
    if not doc.has_field("activation"):
        warnings.append(
            "'activation' field is missing from frontmatter. "
            "Add 'activation: /{skill-name}' for namespace enforcement."
        )

    # provenance field (harness factory v1.1)
    if not doc.has_field("provenance"):
        warnings.append(
            "'provenance' field is missing from frontmatter. "
            "Add provenance metadata (maintainer, version, created, source_references)."
        )

    # Referenced local files
    if body is not None:
        local_links = _extract_local_links(body)
        for link_path in local_links:
            resolved = skill_dir / link_path
            if not resolved.exists():
                warnings.append(
                    f"Referenced file does not exist: '{link_path}'"
                )

    return {
        "valid": len(errors) == 0,
        "errors": errors,
        "warnings": warnings,
    }


def _print_human_readable(result: dict, skill_path: str) -> None:
    """
    Print validation results in a human-readable format.

    Args:
        result: The validation result dictionary.
        skill_path: The path that was validated (for display).
    """
    print(f"Validating: {skill_path}")
    print(f"{'=' * 60}")

    if result["valid"]:
        print("Status: VALID")
    else:
        print("Status: INVALID")

    if result["errors"]:
        print(f"\nErrors ({len(result['errors'])}):")
        for error in result["errors"]:
            print(f"  [ERROR] {error}")

    if result["warnings"]:
        print(f"\nWarnings ({len(result['warnings'])}):")
        for warning in result["warnings"]:
            print(f"  [WARN]  {warning}")

    if not result["errors"] and not result["warnings"]:
        print("\nNo issues found.")

    print(f"{'=' * 60}")


def main() -> None:
    """CLI entry point for the spec compliance validator."""
    if len(sys.argv) < 2:
        print(
            "Usage: python3 scripts/validate.py <skill-path> [--json]\n"
            "\n"
            "Arguments:\n"
            "  skill-path    Path to the skill directory to validate\n"
            "\n"
            "Options:\n"
            "  --json        Output results as JSON to stdout\n"
            "\n"
            "Exit codes:\n"
            "  0  Valid (no errors)\n"
            "  1  Invalid (one or more errors)\n",
            file=sys.stderr,
        )
        sys.exit(1)

    skill_path = sys.argv[1]
    use_json = "--json" in sys.argv

    result = validate_skill(skill_path)

    if use_json:
        print(json.dumps(result, indent=2))
    else:
        _print_human_readable(result, skill_path)

    sys.exit(0 if result["valid"] else 1)


if __name__ == "__main__":
    main()
