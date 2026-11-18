"""Tests for tools/check.py. Run: python -m unittest discover -s tools -v"""

from __future__ import annotations

import contextlib
import io
import os
import tempfile
import textwrap
import unittest
from pathlib import Path
from unittest import mock

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
            path.write_bytes(textwrap.dedent(body).lstrip("\n").encode("utf-8"))  # keep LF on Windows

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

    def deny_file(self, text: str) -> Path:
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        path = Path(tmp.name) / "deny.txt"
        path.write_bytes(text.encode("utf-8"))
        return path

    def test_deny_list_reports_line_not_term(self) -> None:
        deny = check.load_deny_list(self.deny_file("# comment\n\nSecretCorp\nre:acme-\\d+\n"))
        body = "# Guide\n\nI worked at secretcorp on acme-42.\n"
        problems = self.tree({"guides/a.md": body}).problems(deny)
        self.assertHas(problems, "matches deny-list line 3")
        self.assertHas(problems, "matches deny-list line 4")
        self.assertFalse(any("secretcorp" in p.lower() for p in problems))

    def test_deny_list_syntax(self) -> None:
        deny = check.load_deny_list(self.deny_file("\ufeffacme # client\nre: beta-\\d\nGamma Corp\n"))
        body = "# Guide\n\nAcme_prod uses BETA-1 at gamma corp, not acmeville.\n"
        problems = [p for p in self.tree({"guides/a.md": body}).problems(deny) if "deny-list" in p]
        self.assertEqual(len(problems), 3, problems)
        for text in ("re:(\n", "re:\n"):
            with self.assertRaisesRegex(ValueError, "deny-list line 1"):
                check.load_deny_list(self.deny_file(text))

    def main_exit_code(self, *argv: str) -> int:
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            return check.main(list(argv))

    def test_main_exit_codes(self) -> None:
        root = self.tree().root
        self.assertEqual(self.main_exit_code("--root", str(root)), 0)
        self.assertEqual(self.main_exit_code("--root", str(root), "--deny-list", str(root / "nope.txt")), 2)
        self.assertEqual(self.main_exit_code("--root", str(root), "--deny-list", str(self.deny_file("re:(\n"))), 2)
        (root / "guides/a.md").write_text("# Guide\n\n[x](gone.md)\n", encoding="utf-8")
        self.assertEqual(self.main_exit_code("--root", str(root)), 1)
        self.assertEqual(self.main_exit_code("--root", str(root / "missing")), 2)

    def test_every_secret_pattern_is_reported(self) -> None:
        samples = {
            "private key": "-----BEGIN RSA PRIVATE" " KEY-----",
            "GitHub token": "ghp_" + "a" * 36,
            "AWS access key id": "AKIA" + "A" * 16,
            "Slack token": "xoxb-" + "1" * 12,
            "API secret key": "sk-proj-" + "a" * 24,
            "Google API key": "AIza" + "a" * 35,
            "JSON web token": "eyJ" + "a" * 12 + ".eyJ" + "a" * 12 + ".sig",
        }
        for label, secret in samples.items():
            with self.subTest(label):
                problems = self.tree({"guides/a.md": f"# Guide\n\n{secret}\n"}).problems()
                self.assertHas(problems, f"guides/a.md:3: {label}")

    def test_home_paths_and_emails(self) -> None:
        leaks = ["cd /Users/" "alice", "HOME=/home/" "alice", r"C:\Users" r"\alice\Desktop", r"c:\users" r"\alice", "mail bob@" "corp.com"]
        fine = ["https://example.com/home/alice/profile", "src/home/widgets/index.ts", "/home/runner/work/x",
                "git@github.com:owner/repo.git", "noreply@anthropic.com", "bob@mail.example.com",
                "GET /users/42/orders"]
        for text, expected in [(t, True) for t in leaks] + [(t, False) for t in fine]:
            with self.subTest(text):
                problems = self.tree({"guides/a.md": f"# Guide\n\n{text}\n"}).problems()
                self.assertEqual(any(p.startswith("guides/a.md:3:") for p in problems), expected, problems)

    def test_whitespace_and_forbidden_files(self) -> None:
        problems = self.tree({"guides/a.md": "# Guide  \n", "notes.pdf": "x"}).problems()
        self.assertHas(problems, "guides/a.md:1: trailing whitespace")
        self.assertHas(problems, "notes.pdf: .pdf files must not be committed")

    def test_file_policy(self) -> None:
        files = {"x/.env.local": "A=1\n", "x/.env.sample": "A=\n", "x/deck.PPTX": "x", "x/.DS_Store": "x",
                 "x/big.txt": "a" * check.MAX_FILE_BYTES + "\n"}
        problems = self.tree(files).problems()
        self.assertHas(problems, "x/.env.local: local environment")
        self.assertHas(problems, "x/.DS_Store: local environment")
        self.assertHas(problems, "x/deck.PPTX: .PPTX files must not be committed")
        self.assertHas(problems, "x/big.txt: file is larger than 1 MB")
        self.assertFalse(any(".env.sample" in p for p in problems), problems)

    def test_line_endings_bom_and_line_numbers(self) -> None:
        tree = self.tree()
        guide = tree.root / "guides/a.md"
        for raw, fragment in [(b"# Guide\r\n", "guides/a.md: CRLF line endings"),
                              (b"# Guide", "guides/a.md: missing newline at end of file"),
                              (b"# Guide\n\n\n", "guides/a.md: extra blank line at end of file")]:
            guide.write_bytes(raw)
            self.assertHas(tree.problems(), fragment)
        guide.write_bytes(b"\xef\xbb\xbf# Guide\n\n[x](#guide)\n")
        problems = tree.problems()
        self.assertHas(problems, "byte-order mark")
        self.assertFalse(any("missing anchor" in p for p in problems), problems)
        guide.write_bytes("# Guide\n\nline\u2028two\n[gone](gone.md)\n".encode("utf-8"))
        self.assertHas(tree.problems(), "guides/a.md:4: broken link: gone.md")

    def test_link_and_code_span_case_must_match_disk(self) -> None:
        guide = "# Guide\n\n[x](B.md) `guides/B.md`\n"
        problems = self.tree({"guides/a.md": guide, "guides/b.md": "# B\n"}).problems()
        self.assertHas(problems, "guides/a.md:3: broken link: B.md")
        self.assertHas(problems, "`guides/B.md` does not exist")

    def test_fences_in_lists_quotes_tildes_and_unclosed(self) -> None:
        body = ("# Guide\n\n1. step\n\n    ```\n    [a](gone1.md)\n    ```\n\n"
                "> ```\n> [b](gone2.md)\n> ```\n\n~~~\n[c](gone3.md)\n~~~\n\n[d](gone4.md)\n")
        problems = self.tree({"guides/a.md": body}).problems()
        self.assertEqual([p for p in problems if "broken link" in p], ["guides/a.md:17: broken link: gone4.md"])
        problems = self.tree({"guides/a.md": "# Guide\n\n```\n[x](gone.md)\n"}).problems()
        self.assertHas(problems, "guides/a.md:3: code fence is never closed")

    def test_footnotes_and_prose_colons_are_not_reference_definitions(self) -> None:
        body = "# Guide\n\nText[^1].\n\n[^1]: See the docs\n[Interviewer]: Tell me about yourself.\n[ref]: gone.md\n"
        problems = self.tree({"guides/a.md": body}).problems()
        self.assertEqual([p for p in problems if "broken link" in p], ["guides/a.md:7: broken link: gone.md"])

    def test_skill_standalone_variants(self) -> None:
        head = "---\nname: demo-coach\ndescription: Coach a demo skill. Use for tests.\n---\n"
        body = (head + "[up](../) [all](../../guides/) `./guides/a.md` `../../guides/a.md` `/guides/a.md`\n"
                "[own](templates/own.md) and `templates/own.md`\n")
        problems = self.tree({"skills/demo-coach/SKILL.md": body, "skills/demo-coach/templates/own.md": "# Own\n"}).problems()
        self.assertEqual(sum("skills must stand alone" in p for p in problems), 5, problems)
        self.assertFalse(any("templates/own.md" in p for p in problems), problems)

    def test_skill_size_limits_and_optional_fields(self) -> None:
        def problems_for(extra: str = "", description: str = "Use for tests.", body: str = "") -> list[str]:
            text = f"---\nname: demo-coach\ndescription: {description}\n{extra}---\n{body}"
            return self.tree({"skills/demo-coach/SKILL.md": text}).problems()

        self.assertEqual(problems_for(description="d" * 1024), [])
        self.assertHas(problems_for(description="d" * 1025), "description is 1025 characters")
        self.assertEqual(problems_for(body="x\n" * 496), [])
        self.assertHas(problems_for(body="x\n" * 497), "longer than 500 lines")
        self.assertEqual(problems_for("compatibility: " + "c" * 500 + "\n"), [])
        self.assertHas(problems_for("compatibility: " + "c" * 501 + "\n"), "compatibility must be")
        self.assertHas(problems_for("description2: x\n"), "outside the Agent Skills spec: description2")
        if check.yaml is not None:
            self.assertHas(problems_for("metadata:\n  version: 1.0\n"), "metadata must map string keys")
            self.assertHas(problems_for("allowed-tools:\n  - Read\n"), "allowed-tools must be one")
            self.assertEqual(problems_for('metadata:\n  version: "1.0"\nallowed-tools: Read Bash\n'), [])

    def test_frontmatter_fallback_parser_without_pyyaml(self) -> None:
        head = "---\nname: demo-coach\n\n# note\ndescription: >\n  Coach a demo skill.\n  Use for tests.\n"
        with mock.patch.object(check, "yaml", None):
            ok = self.tree({"skills/demo-coach/SKILL.md": head + "allowed-tools:\n- Read\n---\nBody\n"}).problems()
            bad = self.tree({"skills/demo-coach/SKILL.md": head + "oops\n---\nBody\n"}).problems()
        self.assertEqual(ok, [])
        self.assertHas(bad, "unparseable frontmatter line: 'oops'")

    def test_odd_input_is_reported_not_raised(self) -> None:
        guide = "# Guide\n\n[a](" + "x" * 300 + ".md) [b](bad%00.md) `guides/" + "y" * 300 + ".md`\n"
        tree = self.tree({"guides/a.md": guide, "guides/bad.csv": "a,b\x00c\n1,2\n"})
        problems = tree.problems()
        self.assertEqual(sum("broken link" in p for p in problems), 2, problems)
        self.assertHas(problems, "does not exist in this repository")

    @unittest.skipIf(os.name != "posix", "needs symlinks")
    def test_symlink_loop_is_reported_not_raised(self) -> None:
        tree = self.tree({"guides/a.md": "# Guide\n\n[loop](loop.md)\n"})
        os.symlink("loop.md", tree.root / "guides/loop.md")
        problems = tree.problems()
        self.assertHas(problems, "guides/loop.md: symlinks are not allowed")
        self.assertHas(problems, "broken link: loop.md")


if __name__ == "__main__":
    unittest.main()
