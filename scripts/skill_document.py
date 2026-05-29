#!/usr/bin/env python3
"""
Skill-document parsing for agent-skill-creator.

`SkillDoc` is the single source of SKILL.md parsing. It owns frontmatter
extraction and the deliberately-simple YAML reads (scalar fields, parent.child
sub-fields, and lists-of-objects) that validate.py, staleness_check.py,
skill_registry.py, and export_utils.py all need. Parse once via `from_text` /
`from_path`, then query through the interface. Validation *rules* (length
limits, name regex, link checks) stay in validate.py — this module only parses.

The YAML reads are intentionally not a full YAML parser: they match the narrow
shapes the spec uses and avoid a PyYAML dependency.
"""

from __future__ import annotations

from pathlib import Path

_BLOCK_SCALAR_INDICATORS = (">-", "|-", ">", "|", ">+", "|+")


def _split_frontmatter(content: str) -> tuple[str | None, str | None]:
    """Return (frontmatter, body) or (None, None) if frontmatter is absent or
    not closed."""
    if not content.startswith("---"):
        return None, None
    closing_index = content.find("---", 3)
    if closing_index == -1:
        return None, None
    frontmatter = content[3:closing_index].strip()
    body = content[closing_index + 3:].strip()
    return frontmatter, body


class SkillDoc:
    """Parsed view of a SKILL.md document."""

    def __init__(self, frontmatter: str | None, body: str | None) -> None:
        self._frontmatter = frontmatter
        self._body = body

    @classmethod
    def from_text(cls, content: str) -> SkillDoc:
        """Parse SKILL.md content. `frontmatter`/`body` are None when absent."""
        frontmatter, body = _split_frontmatter(content)
        return cls(frontmatter, body)

    @classmethod
    def from_path(cls, path: str | Path) -> SkillDoc:
        """Parse a SKILL.md file from disk."""
        content = Path(path).read_text(encoding="utf-8")
        return cls.from_text(content)

    # --- Raw sections ---

    @property
    def frontmatter(self) -> str | None:
        return self._frontmatter

    @property
    def body(self) -> str | None:
        return self._body

    # --- Typed accessors for the universal fields ---

    @property
    def name(self) -> str | None:
        return self.field("name")

    @property
    def description(self) -> str | None:
        return self.field("description")

    @property
    def license(self) -> str | None:
        return self.field("license")

    @property
    def metadata(self) -> dict[str, str]:
        """Direct scalar children of the `metadata:` block (non-empty values).

        Nested structures (e.g. `dependencies:`) are excluded; read those with
        `list_of_objects`. Only the first child-indent level is collected — use
        `subfield()` if you need an any-depth lookup.
        """
        return self._collect_scalar_children("metadata")

    # --- Generic queries ---

    def field(self, field: str) -> str | None:
        """Top-level scalar field value, joining a YAML block scalar if used."""
        if self._frontmatter is None:
            return None
        lines = self._frontmatter.split("\n")
        for i, line in enumerate(lines):
            stripped = line.strip()
            if stripped.startswith(f"{field}:"):
                value = stripped[len(field) + 1:].strip()
                if value in _BLOCK_SCALAR_INDICATORS:
                    parts: list[str] = []
                    for j in range(i + 1, len(lines)):
                        continuation = lines[j]
                        if continuation and (continuation[0] == " " or continuation[0] == "\t"):
                            parts.append(continuation.strip())
                        else:
                            break
                    return " ".join(parts) if parts else ""
                return value
        return None

    def has_field(self, field: str) -> bool:
        """True if `field` appears as a top-level key."""
        if self._frontmatter is None:
            return False
        for line in self._frontmatter.split("\n"):
            if line.strip().startswith(f"{field}:"):
                return True
        return False

    def subfield(self, parent: str, child: str) -> str | None:
        """Scalar value of `child` under the indented `parent:` block."""
        if self._frontmatter is None:
            return None
        in_parent = False
        for line in self._frontmatter.split("\n"):
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

    def has_subfield(self, parent: str, child: str) -> bool:
        """True if `child` exists under the indented `parent:` block."""
        if self._frontmatter is None:
            return False
        in_parent = False
        for line in self._frontmatter.split("\n"):
            stripped = line.strip()
            if stripped.startswith(f"{parent}:"):
                in_parent = True
                continue
            if in_parent:
                if line and (line[0] == " " or line[0] == "\t"):
                    if stripped.startswith(f"{child}:"):
                        return True
                else:
                    in_parent = False
        return False

    def list_of_objects(self, parent: str, child: str) -> list[dict]:
        """Parse a YAML list-of-objects under `parent.child`.

        Handles::

            metadata:
              dependencies:
                - url: https://example.com
                  name: Example
                  type: api
        """
        if self._frontmatter is None:
            return []
        lines = self._frontmatter.split("\n")
        items: list[dict] = []
        in_parent = False
        in_child = False
        current_item: dict | None = None
        child_indent = -1

        for line in lines:
            stripped = line.strip()
            if not in_parent:
                if stripped.startswith(f"{parent}:"):
                    in_parent = True
                continue
            if line and line[0] != " " and line[0] != "\t" and stripped:
                break
            if not in_child:
                if stripped.startswith(f"{child}:"):
                    in_child = True
                continue
            if not stripped:
                continue
            raw_indent = len(line) - len(line.lstrip())
            if child_indent == -1 and stripped.startswith("- "):
                child_indent = raw_indent
            if raw_indent <= child_indent and not stripped.startswith("- "):
                if ":" in stripped:
                    break
            if stripped.startswith("- "):
                if current_item is not None:
                    items.append(current_item)
                current_item = {}
                rest = stripped[2:].strip()
                if ":" in rest:
                    key, _, val = rest.partition(":")
                    current_item[key.strip()] = val.strip()
            elif current_item is not None and ":" in stripped:
                key, _, val = stripped.partition(":")
                current_item[key.strip()] = val.strip()

        if current_item is not None:
            items.append(current_item)
        return items

    def _collect_scalar_children(self, parent: str) -> dict[str, str]:
        """All direct scalar children of `parent:` with non-empty inline values."""
        if self._frontmatter is None:
            return {}
        result: dict[str, str] = {}
        in_parent = False
        child_indent: int | None = None
        for line in self._frontmatter.split("\n"):
            stripped = line.strip()
            if not in_parent:
                if stripped.startswith(f"{parent}:"):
                    in_parent = True
                continue
            if not stripped:
                continue
            indent = len(line) - len(line.lstrip())
            if indent == 0:
                break
            if child_indent is None:
                child_indent = indent
            if indent == child_indent and ":" in stripped and not stripped.startswith("- "):
                key, _, val = stripped.partition(":")
                val = val.strip()
                if val:
                    result[key.strip()] = val
        return result
