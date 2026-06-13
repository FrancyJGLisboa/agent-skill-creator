"""Tests for scripts.skill_registry.

Covers the gaps called out in issue #10:
  * publish: validation gating + (name, author, version) duplicate detection
  * install: platform/path resolution + author disambiguation
  * search
  * stale: ISO date parsing (datetime.fromisoformat, not naive slicing)
  * author/namespace isolation so two authors can share a skill name

The registry is created under a TemporaryDirectory and project-level installs
chdir into the temp dir, so nothing touches the real home or repo tree.
"""

import argparse
import json
import os
import sys
import tempfile
import unittest
from datetime import date, timedelta
from pathlib import Path

ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

import skill_registry as reg  # noqa: E402


def make_skill(base: Path, name: str, author: str = "alice", version: str = "1.0.0") -> Path:
    """Create a minimal skill directory that passes validate.validate_skill.

    validate_skill requires the directory basename to equal the ``name`` field,
    so the leaf is exactly ``name`` and a per-author parent keeps two authors'
    sources for the same skill name from colliding on disk.
    """
    skill = base / f"src-{author}" / name
    (skill / "scripts").mkdir(parents=True)
    (skill / "SKILL.md").write_text(
        f"""---
name: {name}
description: >-
  Demo skill {name} used by skill_registry tests for coverage.
license: MIT
metadata:
  author: {author}
  version: {version}
---
# /{name}

Demo body.
""",
        encoding="utf-8",
    )
    (skill / "scripts" / "main.py").write_text("print('ok')\n", encoding="utf-8")
    return skill


def init_registry(base: Path) -> Path:
    registry = base / "registry"
    args = argparse.Namespace(registry=str(registry), name="Test Registry")
    reg.cmd_init(args)
    return registry


def publish(registry: Path, skill: Path, tags=None, force=False, as_json=False):
    args = argparse.Namespace(
        registry=str(registry), skill_path=str(skill),
        tags=tags, force=force, json=as_json,
    )
    reg.cmd_publish(args)


def read_registry(registry: Path) -> dict:
    return json.loads((registry / "registry.json").read_text(encoding="utf-8"))


# --- Pure helpers ---------------------------------------------------------

class TestParseIsoDate(unittest.TestCase):
    def test_plain_date(self):
        self.assertEqual(reg.parse_iso_date("2026-06-13"), date(2026, 6, 13))

    def test_full_iso_timestamp(self):
        self.assertEqual(
            reg.parse_iso_date("2026-06-13T12:30:00+00:00"), date(2026, 6, 13)
        )

    def test_empty_and_garbage_return_none(self):
        self.assertIsNone(reg.parse_iso_date(""))
        self.assertIsNone(reg.parse_iso_date("not-a-date"))
        self.assertIsNone(reg.parse_iso_date("2026-13-99"))


class TestStoragePath(unittest.TestCase):
    def test_author_namespaced(self):
        self.assertEqual(reg.skill_storage_path("foo", "Alice Doe"), "skills/alice-doe/foo")

    def test_authorless_is_flat_legacy_layout(self):
        self.assertEqual(reg.skill_storage_path("foo", ""), "skills/foo")


# --- Publish --------------------------------------------------------------

class TestPublish(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.base = Path(self._tmp.name)
        self.registry = init_registry(self.base)

    def tearDown(self):
        self._tmp.cleanup()

    def test_publish_creates_entry_and_files(self):
        skill = make_skill(self.base, "alpha", author="alice")
        publish(self.registry, skill)
        data = read_registry(self.registry)
        self.assertEqual(len(data["skills"]), 1)
        entry = data["skills"][0]
        self.assertEqual(entry["name"], "alpha")
        self.assertEqual(entry["author"], "alice")
        self.assertEqual(entry["path"], "skills/alice/alpha")
        self.assertTrue((self.registry / "skills" / "alice" / "alpha" / "SKILL.md").exists())

    def test_duplicate_same_author_version_blocked(self):
        skill = make_skill(self.base, "alpha", author="alice")
        publish(self.registry, skill)
        with self.assertRaises(SystemExit):
            publish(self.registry, skill)

    def test_duplicate_overwritten_with_force(self):
        skill = make_skill(self.base, "alpha", author="alice")
        publish(self.registry, skill)
        publish(self.registry, skill, force=True)
        data = read_registry(self.registry)
        self.assertEqual(len(data["skills"]), 1)

    def test_invalid_skill_fails_validation(self):
        bad = self.base / "bad-skill"
        bad.mkdir()
        # No SKILL.md -> validate_skill reports errors -> publish exits 1.
        args = argparse.Namespace(
            registry=str(self.registry), skill_path=str(bad),
            tags=None, force=False, json=False,
        )
        with self.assertRaises(SystemExit):
            reg.cmd_publish(args)


# --- Author / namespace isolation -----------------------------------------

class TestNamespaceIsolation(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.base = Path(self._tmp.name)
        self.registry = init_registry(self.base)
        publish(self.registry, make_skill(self.base, "shared", author="alice"))
        publish(self.registry, make_skill(self.base, "shared", author="bob"))

    def tearDown(self):
        self._tmp.cleanup()

    def test_both_authors_coexist_without_clobber(self):
        data = read_registry(self.registry)
        self.assertEqual(len(data["skills"]), 2)
        paths = {s["path"] for s in data["skills"]}
        self.assertEqual(paths, {"skills/alice/shared", "skills/bob/shared"})
        self.assertTrue((self.registry / "skills" / "alice" / "shared" / "SKILL.md").exists())
        self.assertTrue((self.registry / "skills" / "bob" / "shared" / "SKILL.md").exists())

    def test_resolve_ambiguous_name_requires_author(self):
        data = read_registry(self.registry)
        entry, error = reg.resolve_skill_entry(data, "shared")
        self.assertIsNone(entry)
        self.assertIn("multiple authors", error)

    def test_resolve_with_author_disambiguates(self):
        data = read_registry(self.registry)
        entry, error = reg.resolve_skill_entry(data, "shared", "bob")
        self.assertIsNone(error)
        self.assertEqual(entry["author"], "bob")

    def test_remove_only_targets_named_author(self):
        args = argparse.Namespace(
            registry=str(self.registry), skill_name="shared",
            author="alice", force=True,
        )
        reg.cmd_remove(args)
        data = read_registry(self.registry)
        self.assertEqual([s["author"] for s in data["skills"]], ["bob"])
        # alice's files gone, bob's intact
        self.assertFalse((self.registry / "skills" / "alice" / "shared").exists())
        self.assertTrue((self.registry / "skills" / "bob" / "shared").exists())


# --- Search ---------------------------------------------------------------

class TestSearch(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.base = Path(self._tmp.name)
        self.registry = init_registry(self.base)
        publish(self.registry, make_skill(self.base, "weather-report", author="alice"))
        publish(self.registry, make_skill(self.base, "crop-yield", author="bob"))

    def tearDown(self):
        self._tmp.cleanup()

    def test_search_matches_name(self):
        args = argparse.Namespace(registry=str(self.registry), query="weather", json=True)
        # cmd_search prints JSON; capture stdout.
        import io
        from contextlib import redirect_stdout
        buf = io.StringIO()
        with redirect_stdout(buf):
            reg.cmd_search(args)
        matches = json.loads(buf.getvalue())
        self.assertEqual([m["name"] for m in matches], ["weather-report"])

    def test_search_no_match(self):
        args = argparse.Namespace(registry=str(self.registry), query="nonexistent", json=True)
        import io
        from contextlib import redirect_stdout
        buf = io.StringIO()
        with redirect_stdout(buf):
            reg.cmd_search(args)
        self.assertEqual(json.loads(buf.getvalue()), [])


# --- Install (platform + path resolution) ---------------------------------

class TestResolveInstallPath(unittest.TestCase):
    def test_user_path_for_known_platform(self):
        path = reg.resolve_install_path("demo", "claude-code", project=False)
        # as_posix() normalizes separators so the assertion holds on Windows too.
        self.assertTrue(path.as_posix().endswith("/.claude/skills/demo"))

    def test_project_path_for_known_platform(self):
        path = reg.resolve_install_path("demo", "claude-code", project=True)
        self.assertTrue(path.as_posix().endswith("/.claude/skills/demo"))

    def test_unknown_platform_exits(self):
        with self.assertRaises(SystemExit):
            reg.resolve_install_path("demo", "nope", project=False)


class TestInstall(unittest.TestCase):
    def setUp(self):
        self._cwd = os.getcwd()
        self._tmp = tempfile.TemporaryDirectory()
        self.base = Path(self._tmp.name)
        self.registry = init_registry(self.base)
        publish(self.registry, make_skill(self.base, "tool", author="alice"))
        # Project-level installs resolve against cwd; chdir into an isolated dir.
        self.workdir = self.base / "work"
        self.workdir.mkdir()
        os.chdir(self.workdir)

    def tearDown(self):
        os.chdir(self._cwd)
        self._tmp.cleanup()

    def test_project_install_lands_at_resolved_path(self):
        args = argparse.Namespace(
            registry=str(self.registry), skill_name="tool", author=None,
            platform="claude-code", project=True, force=False, json=False,
        )
        reg.cmd_install(args)
        installed = self.workdir / ".claude" / "skills" / "tool" / "SKILL.md"
        self.assertTrue(installed.exists())

    def test_install_missing_skill_exits(self):
        args = argparse.Namespace(
            registry=str(self.registry), skill_name="ghost", author=None,
            platform="claude-code", project=True, force=False, json=False,
        )
        with self.assertRaises(SystemExit):
            reg.cmd_install(args)


# --- Stale ----------------------------------------------------------------

class TestStale(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.base = Path(self._tmp.name)
        self.registry = init_registry(self.base)

    def tearDown(self):
        self._tmp.cleanup()

    def _run_stale(self):
        import io
        from contextlib import redirect_stdout
        args = argparse.Namespace(registry=str(self.registry), json=True)
        buf = io.StringIO()
        with redirect_stdout(buf):
            reg.cmd_stale(args)
        return json.loads(buf.getvalue())

    def test_fresh_skill_from_published_timestamp(self):
        publish(self.registry, make_skill(self.base, "fresh", author="alice"))
        results = self._run_stale()
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["status"], "fresh")
        self.assertEqual(results[0]["date_source"], "published")

    def test_last_reviewed_overdue(self):
        publish(self.registry, make_skill(self.base, "old", author="alice"))
        # Inject an old last_reviewed date directly into the manifest.
        data = read_registry(self.registry)
        long_ago = (date.today() - timedelta(days=999)).isoformat()
        data["skills"][0]["staleness"] = {
            "last_reviewed": long_ago, "review_interval_days": 90,
        }
        (self.registry / "registry.json").write_text(
            json.dumps(data, indent=2) + "\n", encoding="utf-8"
        )
        results = self._run_stale()
        self.assertEqual(results[0]["status"], "overdue")
        self.assertEqual(results[0]["date_source"], "last_reviewed")

    def test_unparseable_date_is_unknown(self):
        publish(self.registry, make_skill(self.base, "weird", author="alice"))
        data = read_registry(self.registry)
        data["skills"][0]["published"] = "not-a-date"
        data["skills"][0]["staleness"] = {}
        (self.registry / "registry.json").write_text(
            json.dumps(data, indent=2) + "\n", encoding="utf-8"
        )
        results = self._run_stale()
        self.assertEqual(results[0]["status"], "unknown")
        self.assertEqual(results[0]["date_source"], "none")


if __name__ == "__main__":
    unittest.main()
