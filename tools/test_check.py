"""Tests for tools/check.py. Run: python -m unittest discover -s tools -v"""

from __future__ import annotations

import tempfile
import textwrap
import unittest
from pathlib import Path

import check

SKILL = """
    ---
    name: demo-coach
    description: Coach a demo skill. Use for tests.
    ---
    # Demo coach
    Body.
"""

BASE = {
    "README.md": "# Demo\n\n[guide](guides/a.md) [skill](skills/demo-coach/SKILL.md) [csv](templates/t.csv)\n",
    "guides/a.md": "# Guide\n\n## Same\n\n## Same\n\nSee [again](#same-1).\n",
    "skills/demo-coach/SKILL.md": SKILL,
    "templates/t.csv": "a,b\n1,2\n",
}


class Tree:
    def __init__(self, files: dict[str, str]) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)
        for name, body in files.items():
            path = self.root / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(textwrap.dedent(body).lstrip("\n"), encoding="utf-8")

    def problems(self, deny=None) -> list[str]:
        return [str(p) for p in check.run(self.root, deny)[0]]

    def close(self) -> None:
        self._tmp.cleanup()


class CheckTests(unittest.TestCase):
    def tree(self, overrides: dict[str, str] | None = None) -> Tree:
        tree = Tree({**BASE, **(overrides or {})})
        self.addCleanup(tree.close)
        return tree

    def assertHas(self, problems: list[str], fragment: str) -> None:
        self.assertTrue(any(fragment in p for p in problems), f"{fragment!r} not in {problems}")

    def test_clean_tree_passes(self) -> None:
        self.assertEqual(self.tree().problems(), [])

    def test_repository_itself_passes(self) -> None:
        problems, count = check.run(Path(__file__).resolve().parent.parent)
        self.assertEqual([str(p) for p in problems], [])
        self.assertGreater(count, 10)

    def test_links_and_anchors(self) -> None:
        body = "# Guide\n\n[x](missing.md) [y](a.md#nope) [z](../../outside.md)\n\n```\n[ignored](gone.md)\n```\n"
        problems = self.tree({"guides/a.md": body}).problems()
        self.assertHas(problems, "broken link: missing.md")
        self.assertHas(problems, "missing anchor #nope")
        self.assertHas(problems, "link leaves the repository")
        self.assertFalse(any("gone.md" in p for p in problems))

    def test_slug_matches_github_rules(self) -> None:
        self.assertEqual(check.slugify("Why `this` works - and [when](x.md)?"), "why-this-works---and-when")
        self.assertEqual(check.slugify("A & B"), "a--b")

    def test_unreachable_content_is_reported(self) -> None:
        problems = self.tree({"guides/orphan.md": "# Orphan\n"}).problems()
        self.assertHas(problems, "guides/orphan.md: not reachable from README.md")

    def test_stale_repo_path_in_code_span(self) -> None:
        readme = "# Demo\n\n`guides/gone.md` [g](guides/a.md) [s](skills/demo-coach/SKILL.md) [c](templates/t.csv)\n"
        problems = self.tree({"README.md": readme}).problems()
        self.assertHas(problems, "`guides/gone.md` does not exist")

    def test_skill_rules(self) -> None:
        bad = """
            ---
            name: Wrong_Name
            description: Has <angle> brackets and a # hash
            extra: nope
            ---
            [out](../../guides/a.md) and `templates/t.csv`
        """
        problems = self.tree({"skills/demo-coach/SKILL.md": bad}).problems()
        self.assertHas(problems, "must be 1-64 lowercase")
        self.assertHas(problems, "must match its folder name")
        self.assertHas(problems, "angle brackets")
        self.assertHas(problems, "outside the Agent Skills spec: extra")
        self.assertHas(problems, "' #'")
        self.assertHas(problems, "skill links outside its own folder")
        self.assertHas(problems, "skill refers to repository path `templates/t.csv`")

    def test_skill_missing_frontmatter(self) -> None:
        problems = self.tree({"skills/demo-coach/SKILL.md": "# No frontmatter\n"}).problems()
        self.assertHas(problems, "missing YAML frontmatter")

    def test_csv_shape(self) -> None:
        problems = self.tree({"templates/t.csv": "a,b\n1,2,3\n"}).problems()
        self.assertHas(problems, "templates/t.csv:2: 3 columns, header has 2")

    def test_privacy_patterns(self) -> None:
        leaks = (
            "mail person" "@" "gmail.com ok a" "@" "example.com\n"
            "path /Users/" "alice/notes and /home/you/ok\n"
            "see ~/.copilot/session-" "state/x\n"
        )
        problems = self.tree({"guides/a.md": "# Guide\n\n" + leaks}).problems()
        self.assertHas(problems, "a.md:3: email address")
        self.assertEqual(sum("email address" in p for p in problems), 1)
        self.assertHas(problems, "a.md:4: absolute home-directory path")
        self.assertEqual(sum("home-directory" in p for p in problems), 1)
        self.assertHas(problems, "a.md:5: agent session path")

    def test_deny_list_reports_line_not_term(self) -> None:
        deny_file = Path(tempfile.mkdtemp()) / "deny.txt"
        deny_file.write_text("# comment\n\nSecretCorp\nre:acme-\\d+\n", encoding="utf-8")
        self.addCleanup(deny_file.unlink)
        body = "# Guide\n\nI worked at secretcorp on acme-42.\n"
        problems = self.tree({"guides/a.md": body}).problems(check.load_deny_list(deny_file))
        self.assertHas(problems, "matches deny-list line 3")
        self.assertHas(problems, "matches deny-list line 4")
        self.assertFalse(any("secretcorp" in p.lower() for p in problems))

    def test_whitespace_and_forbidden_files(self) -> None:
        problems = self.tree({"guides/a.md": "# Guide  \n", "notes.pdf": "x"}).problems()
        self.assertHas(problems, "guides/a.md:1: trailing whitespace")
        self.assertHas(problems, "notes.pdf: .pdf files must not be committed")


if __name__ == "__main__":
    unittest.main()
