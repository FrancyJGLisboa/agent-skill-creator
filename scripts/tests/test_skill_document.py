"""Characterization tests for scripts.skill_document.SkillDoc.

These pin the SKILL.md parsing behavior that validate.py / staleness_check.py /
skill_registry.py / export_utils.py all depend on, so the consolidation onto a
single SkillDoc module cannot silently change it. Edge cases the rewrite must
preserve: YAML block scalars, the metadata indentation-walk exit condition, and
list-of-objects parsing.
"""

import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

from skill_document import SkillDoc  # noqa: E402

FULL = """---
name: demo-skill
description: >-
  A multi-line folded description
  that spans two lines.
license: MIT
metadata:
  author: Jane Doe
  version: 1.2.0
  created: 2026-05-29
  dependencies:
    - url: https://api.example.com/v1
      name: Example API
      type: api
    - url: https://api2.example.com
      name: Second
      type: api
top_after_meta: sibling
---
# /demo-skill — Body

Body text with [a link](references/guide.md) and [external](https://x.com).
"""


class FrontmatterBodyTest(unittest.TestCase):
    def test_splits_frontmatter_and_body(self) -> None:
        doc = SkillDoc.from_text(FULL)
        self.assertIn("name: demo-skill", doc.frontmatter)
        self.assertTrue(doc.body.startswith("# /demo-skill"))

    def test_no_frontmatter_returns_none(self) -> None:
        doc = SkillDoc.from_text("no frontmatter here")
        self.assertIsNone(doc.frontmatter)
        self.assertIsNone(doc.name)
        self.assertEqual(doc.metadata, {})
        self.assertEqual(doc.list_of_objects("metadata", "dependencies"), [])
        self.assertIsNone(doc.field("name"))
        self.assertFalse(doc.has_field("name"))

    def test_unclosed_frontmatter_returns_none(self) -> None:
        doc = SkillDoc.from_text("---\nname: x\nno closing delimiter\n")
        self.assertIsNone(doc.frontmatter)


class ScalarFieldTest(unittest.TestCase):
    def setUp(self) -> None:
        self.doc = SkillDoc.from_text(FULL)

    def test_inline_fields(self) -> None:
        self.assertEqual(self.doc.name, "demo-skill")
        self.assertEqual(self.doc.license, "MIT")
        self.assertEqual(self.doc.field("license"), "MIT")

    def test_folded_block_scalar_is_joined(self) -> None:
        self.assertEqual(
            self.doc.description,
            "A multi-line folded description that spans two lines.",
        )

    def test_has_field(self) -> None:
        self.assertTrue(self.doc.has_field("metadata"))
        self.assertFalse(self.doc.has_field("nonexistent"))

    def test_block_scalar_indicator_variants(self) -> None:
        for indicator in (">-", "|-", ">", "|", ">+", "|+"):
            text = f"---\ndescription: {indicator}\n  one\n  two\nname: x\n---\nbody\n"
            self.assertEqual(SkillDoc.from_text(text).description, "one two", indicator)

    def test_empty_block_scalar(self) -> None:
        text = "---\ndescription: >-\nname: x\n---\nbody\n"
        self.assertEqual(SkillDoc.from_text(text).description, "")


class SubfieldTest(unittest.TestCase):
    def setUp(self) -> None:
        self.doc = SkillDoc.from_text(FULL)

    def test_subfield_values(self) -> None:
        self.assertEqual(self.doc.subfield("metadata", "author"), "Jane Doe")
        self.assertEqual(self.doc.subfield("metadata", "version"), "1.2.0")
        self.assertEqual(self.doc.subfield("metadata", "created"), "2026-05-29")

    def test_has_subfield(self) -> None:
        self.assertTrue(self.doc.has_subfield("metadata", "author"))
        self.assertFalse(self.doc.has_subfield("metadata", "missing"))

    def test_sibling_of_parent_is_not_a_subfield(self) -> None:
        # top_after_meta is a sibling of metadata, not a child — the walk must
        # exit the metadata block on the unindented line.
        self.assertIsNone(self.doc.subfield("metadata", "top_after_meta"))
        self.assertFalse(self.doc.has_subfield("metadata", "top_after_meta"))

    def test_metadata_dict_matches_subfield(self) -> None:
        meta = self.doc.metadata
        self.assertEqual(meta.get("author"), self.doc.subfield("metadata", "author"))
        self.assertEqual(meta.get("version"), "1.2.0")
        self.assertEqual(meta.get("created"), "2026-05-29")
        # nested list key has no inline scalar value -> excluded
        self.assertNotIn("dependencies", meta)


class ListOfObjectsTest(unittest.TestCase):
    def test_parses_list_of_dicts(self) -> None:
        doc = SkillDoc.from_text(FULL)
        deps = doc.list_of_objects("metadata", "dependencies")
        self.assertEqual(
            deps,
            [
                {"url": "https://api.example.com/v1", "name": "Example API", "type": "api"},
                {"url": "https://api2.example.com", "name": "Second", "type": "api"},
            ],
        )

    def test_missing_list_returns_empty(self) -> None:
        doc = SkillDoc.from_text(FULL)
        self.assertEqual(doc.list_of_objects("metadata", "schema_expectations"), [])


class FromPathTest(unittest.TestCase):
    def test_from_path_reads_skill_md(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp) / "SKILL.md"
            p.write_text(FULL, encoding="utf-8")
            doc = SkillDoc.from_path(p)
            self.assertEqual(doc.name, "demo-skill")


if __name__ == "__main__":
    unittest.main()
