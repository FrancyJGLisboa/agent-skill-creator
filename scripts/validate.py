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
from typing import Optional


# --- Constants ---

MAX_NAME_LENGTH = 64
MAX_DESCRIPTION_LENGTH = 1024
MAX_BODY_LINES_WARNING = 500

# Pattern for valid skill names: lowercase letters, numbers, hyphens
NAME_PATTERN = re.compile(r"^[a-z0-9]([a-z0-9-]*[a-z0-9])?$")
CONSECUTIVE_HYPHENS_PATTERN = re.compile(r"--")

# Pattern for YYYY-MM-DD date format
DATE_FORMAT_PATTERN = re.compile(r"^\d{4}-\d{2}-\d{2}$")

# Pattern for local file references in markdown: [text](path) excluding http/https/mailto/#
LOCAL_LINK_PATTERN = re.compile(
    r"\[([^\]]*)\]\(([^)]+)\)"
)


def _parse_frontmatter(content: str) -> tuple[Optional[str], Optional[str]]:
    """
    Extract frontmatter and body from SKILL.md content.

    Args:
        content: Full text content of SKILL.md.

    Returns:
        Tuple of (frontmatter_text, body_text). Either may be None if
        frontmatter is missing or malformed.
    """
    if not content.startswith("---"):
        return None, None

    # Find the closing --- (skip the opening one at position 0)
    closing_index = content.find("---", 3)
    if closing_index == -1:
        return None, None

    frontmatter = content[3:closing_index].strip()
    body = content[closing_index + 3:].strip()
    return frontmatter, body


def _parse_yaml_field(frontmatter: str, field: str) -> Optional[str]:
    """
    Extract a top-level scalar field value from YAML frontmatter using simple parsing.

    Handles both inline values (``name: value``) and YAML block scalars
    (``description: >-`` followed by indented continuation lines).

    Args:
        frontmatter: The frontmatter text (without ``---`` delimiters).
        field: The field name to look for.

    Returns:
        The field value as a string, or None if the field is not present.
    """
    lines = frontmatter.split("\n")
    for i, line in enumerate(lines):
        stripped = line.strip()
        if stripped.startswith(f"{field}:"):
            value = stripped[len(field) + 1:].strip()

            # Check for YAML block scalar indicators (>- , |-, >, |)
            if value in (">-", "|-", ">", "|", ">+", "|+"):
                # Collect indented continuation lines
                parts: list[str] = []
                for j in range(i + 1, len(lines)):
                    continuation = lines[j]
                    # Continuation lines must be indented
                    if continuation and (continuation[0] == " " or continuation[0] == "\t"):
                        parts.append(continuation.strip())
                    else:
                        break
                return " ".join(parts) if parts else ""

            return value
    return None


def _field_exists_in_frontmatter(frontmatter: str, field: str) -> bool:
    """
    Check whether a field name appears as a top-level key in frontmatter.

    Args:
        frontmatter: The frontmatter text.
        field: The field name to look for.

    Returns:
        True if the field is present.
    """
    for line in frontmatter.split("\n"):
        stripped = line.strip()
        if stripped.startswith(f"{field}:"):
            return True
    return False


def _subfield_exists(frontmatter: str, parent: str, child: str) -> bool:
    """
    Check whether a sub-field exists under a parent field in YAML frontmatter.

    Args:
        frontmatter: The frontmatter text.
        parent: The parent field name (e.g., ``metadata``).
        child: The child field name (e.g., ``author``).

    Returns:
        True if the sub-field is found under the parent.
    """
    lines = frontmatter.split("\n")
    in_parent = False
    for line in lines:
        stripped = line.strip()
        # Detect the parent field
        if stripped.startswith(f"{parent}:"):
            in_parent = True
            continue
        if in_parent:
            # Still inside the parent block if line is indented
            if line and (line[0] == " " or line[0] == "\t"):
                if stripped.startswith(f"{child}:"):
                    return True
            else:
                # Left the parent block
                in_parent = False
    return False


def _parse_subfield_value(frontmatter: str, parent: str, child: str) -> Optional[str]:
    """
    Extract a sub-field value from under a parent field in YAML frontmatter.

    Args:
        frontmatter: The frontmatter text.
        parent: The parent field name (e.g., ``metadata``).
        child: The child field name (e.g., ``author``).

    Returns:
        The sub-field value as a string, or None if not found.
    """
    lines = frontmatter.split("\n")
    in_parent = False
    for line in lines:
        stripped = line.strip()
        if stripped.startswith(f"{parent}:"):
            in_parent = True
            continue
        if in_parent:
            if line and (line[0] == " " or line[0] == "\t"):
                if stripped.startswith(f"{child}:"):
                    return stripped[len(child) + 1:].strip()
            else:
                in_parent = False
    return None


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

    frontmatter, body = _parse_frontmatter(content)

    if frontmatter is None:
        errors.append("SKILL.md frontmatter is not properly closed (missing closing '---')")
        return {"valid": False, "errors": errors, "warnings": warnings}

    # --- Check: name field ---
    name_value = _parse_yaml_field(frontmatter, "name")
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
    description_value = _parse_yaml_field(frontmatter, "description")
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

    # license field
    if not _field_exists_in_frontmatter(frontmatter, "license"):
        warnings.append("'license' field is missing from frontmatter")

    # metadata field
    if not _field_exists_in_frontmatter(frontmatter, "metadata"):
        warnings.append("'metadata' field is missing from frontmatter")
    else:
        if not _subfield_exists(frontmatter, "metadata", "author"):
            warnings.append("'metadata.author' sub-field is missing")
        if not _subfield_exists(frontmatter, "metadata", "version"):
            warnings.append("'metadata.version' sub-field is missing")

        # Temporal metadata validation (optional, warnings only)
        created_val = _parse_subfield_value(frontmatter, "metadata", "created")
        reviewed_val = _parse_subfield_value(frontmatter, "metadata", "last_reviewed")
        interval_val = _parse_subfield_value(frontmatter, "metadata", "review_interval_days")

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

    # activation field (harness factory v1.1)
    if not _field_exists_in_frontmatter(frontmatter, "activation"):
        warnings.append(
            "'activation' field is missing from frontmatter. "
            "Add 'activation: /{skill-name}' for namespace enforcement."
        )

    # provenance field (harness factory v1.1)
    if not _field_exists_in_frontmatter(frontmatter, "provenance"):
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
