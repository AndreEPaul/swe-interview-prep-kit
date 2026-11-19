"""Tests for tools/check.py. Run: python -m unittest discover -s tools -v"""

from __future__ import annotations

import contextlib
import io
import os
import shutil
import subprocess
import tempfile
import textwrap
import time
import unittest
from pathlib import Path
from unittest import mock

import check


def setUpModule() -> None:
    # check.main() reads PEER_KIT_DENY_LIST, so a developer's own deny-list must not leak into the tests.
    patcher = mock.patch.dict(os.environ)
    patcher.start()
    unittest.addModuleCleanup(patcher.stop)
    os.environ.pop("PEER_KIT_DENY_LIST", None)


HOSTILE_GIT_CONFIG = """\
[diff]
\tnoprefix = true
\trenames = copies
\tcontext = 9
\tinterHunkContext = 20
\tsuppressBlankEmpty = true
\texternal = /no/such/diff-tool
[color]
\tui = always
[log]
\tshowRoot = false
\tshowSignature = true
[format]
\tpretty = fuller
"""

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

    def privacy_messages(self, text: str) -> list[str]:
        problems: list[check.Problem] = []
        check.check_privacy("x.md", text + "\n", [], problems)
        return [p.message for p in problems]

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

    def test_contact_details_and_private_links(self) -> None:
        flagged = {
            "phone number": ["call 212-456-" "7890", "(212) 456-" "7890", "+1 212 456 " "7890", "+44 20 7946 " "0958"],
            "personal profile or scheduling link": ["https://www.linkedin.com/in/" "alice-b", "calendly.com/" "alice/30min"],
            "meeting link": ["https://us02web.zoom.us" "/j/1234567890", "https://meet.google.com/" "abc-defg-hij",
                             "https://chime.aws" "/1234567890", "https://acme.webex.com" "/meet/alice",
                             "https://teams.contoso" ".net/l/meetup-join/19%3ameeting", "https://teams.live" ".com/meet/9876543210"],
            "link into a private document": ["https://docs.google.com" "/document/d/1AbC", "https://acme.sharepoint" ".com/sites/x",
                                             "https://acme.slack.com" "/archives/C123", "https://acme.atlassian" ".net/browse/ABC-1",
                                             "https://acme.visualstudio" ".com/project"],
            "link into a hiring or assessment system": ["https://boards.greenhouse" ".io/acme/jobs/1", "https://app.coderpad" ".io/ABC123XY",
                                                        "https://acme.wd5.myworkdayjobs" ".com/en-US/x", "https://acme.hirevue" ".com/x"],
        }
        fine = ["call 212-555-0100 or (555) 123-4567 or +1 415 555 0100", "2024-01-15, v2.345.678.9012, 185,000-220,000",
                "https://www.linkedin.com/in/your-name", "https://calendly.com/", "https://zoom.us/pricing", "https://meet.google.com/landing",
                "https://api.slack.com/methods/chat.postMessage", "https://code.visualstudio.com/docs", "https://developer.atlassian.com/x",
                "https://coderpad.io/sandbox", "https://www.hirevue.com/", "https://www.hackerrank.com/challenges/two-sum"]
        for label, samples in flagged.items():
            for text in samples:
                with self.subTest(text):
                    self.assertTrue(any(m.startswith(label) for m in self.privacy_messages(text)), text)
        for text in fine:
            with self.subTest(text):
                self.assertEqual(self.privacy_messages(text), [])

    def test_long_lines_do_not_stall_the_privacy_patterns(self) -> None:
        # A leading [a-z0-9-]+ in a host pattern takes ~18 s on a 50,000-character line; these patterns take milliseconds.
        for line in ("a-" * 25_000, "a." * 25_000, "1 " * 25_000, "(" * 50_000, "calendly.com/" * 4_000):
            started = time.monotonic()
            self.privacy_messages(line)
            self.assertLess(time.monotonic() - started, 5, line[:12])

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

    def test_media_and_exports_are_forbidden(self) -> None:
        banned = ["shot.PNG", "photo.jpeg", "mock.m4a", "call.webm", "mock.vtt", "recruiter.eml", "invite.ics", "traffic.har"]
        problems = self.tree({f"x/{name}": "x" for name in banned} | {"x/diagram.svg": "<svg/>\n"}).problems()
        for name in banned:
            with self.subTest(name):
                self.assertHas(problems, f"x/{name}: {Path(name).suffix} files must not be committed")
        self.assertFalse(any("diagram.svg" in p for p in problems), problems)

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

    def test_diff_header_paths_and_git_quoting(self) -> None:
        headers = {
            "diff --git a/guides/a.md b/guides/a.md": "guides/a.md",
            "diff --git a/my notes.md b/my notes.md": "my notes.md",
            "diff --git a/a b/c.md b/a b/c.md": "a b/c.md",
            'diff --git "a/say \\"hi\\".md" "b/say \\"hi\\".md"': 'say "hi".md',
            'diff --git "a/tab\\there.md" "b/tab\\there.md"': "tab\there.md",
            'diff --git "a/caf\\303\\251.md" "b/caf\\303\\251.md"': "caf\u00e9.md",
            'diff --git "a/back\\\\slash.md" "b/back\\\\slash.md"': "back\\slash.md",
            "diff --git a/x b/y": None,
            "diff --git ": None,
        }
        for header, expected in headers.items():
            with self.subTest(header):
                self.assertEqual(check.diff_git_path(header), expected)
        self.assertEqual(check.unquote_git_path("plain"), "plain")

    def test_parse_diff_sections(self) -> None:
        diff = "\n".join([
            "diff --git a/one.md b/one.md", "index 111..222 100644", "--- a/one.md", "+++ b/one.md",
            "@@ -2 +2 @@ some heading", "-old", "+++ not a header",
            "@@ -9,0 +10,2 @@", "+ten", "+--- not a header either",
            "@@ -20,2 +22,3 @@", " context", "", "+twenty-four", "\\ No newline at end of file",
            "diff --git a/gone.md b/gone.md", "deleted file mode 100644", "index 222..000", "--- a/gone.md", "+++ /dev/null",
            "@@ -1 +0,0 @@", "-deleted file mode 100644",
            "diff --git a/empty.md b/empty.md", "new file mode 100644", "index 000..e69de29",
            "diff --git a/pic.bin b/pic.bin", "new file mode 100644", "index 000..333", "Binary files /dev/null and b/pic.bin differ",
            "",
        ])
        self.assertEqual([(f.path, f.deleted, f.added) for f in check.parse_diff(diff)], [
            ("one.md", False, [(2, "++ not a header"), (10, "ten"), (11, "--- not a header either"), (24, "twenty-four")]),
            ("gone.md", True, []),
            ("empty.md", False, []),
            ("pic.bin", False, []),
        ])
        with self.assertRaises(ValueError):
            list(check.parse_diff("diff --git a/x b/x\n@@ garbage @@\n"))


@unittest.skipUnless(shutil.which("git"), "needs git")
class HistoryTests(unittest.TestCase):
    """Runs the history scan against throwaway repositories, so it is tested on real `git log` output."""

    LEAK = "mail bob@" "corp.com"
    CORP = "dev@secretcorp" ".test"

    def setUp(self) -> None:
        self.tmp = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, str(self.tmp), ignore_errors=True)
        self.home, self.root = self.tmp / "home", self.tmp / "repo"
        self.home.mkdir()
        self.root.mkdir()
        # Neither the machine's git settings nor the developer's own may leak into (or out of) these repositories.
        env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
        env.update({
            "HOME": str(self.home), "XDG_CONFIG_HOME": str(self.home), "USERPROFILE": str(self.home),
            "GIT_CONFIG_NOSYSTEM": "1", "GIT_CONFIG_GLOBAL": str(self.home / ".gitconfig"),
            "GIT_CEILING_DIRECTORIES": str(self.tmp),
            "GIT_AUTHOR_NAME": "A U Thor", "GIT_AUTHOR_EMAIL": "author@example.com",
            "GIT_COMMITTER_NAME": "A U Thor", "GIT_COMMITTER_EMAIL": "author@example.com",
        })
        patcher = mock.patch.dict(os.environ, env, clear=True)
        patcher.start()
        self.addCleanup(patcher.stop)
        self.git("init", "-q")
        self.git("symbolic-ref", "HEAD", "refs/heads/main")

    def git(self, *args: str, stdin: str | None = None, **env: str) -> str:
        done = subprocess.run(
            ["git", "-C", str(self.root), *args], stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
            input=None if stdin is None else stdin.encode("utf-8"), env={**os.environ, **env},
        )
        output = done.stdout.decode("utf-8", "replace")
        self.assertEqual(done.returncode, 0, f"git {' '.join(args)}: {output}")
        return output

    def commit(self, message: str, files: dict[str, str | None] | None = None, **env: str) -> str:
        """Write the files (None deletes one), commit everything, and return the new commit's hash."""
        for name, body in (files or {}).items():
            path = self.root / name
            if body is None:
                path.unlink()
            else:
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(body.encode("utf-8"))
        self.git("add", "-A")
        self.git("commit", "-q", "--allow-empty", "-F", "-", stdin=message, **env)
        return self.git("rev-parse", "HEAD").strip()

    def scan(self, rev_range: str = "HEAD", deny=None) -> list[str]:
        return [str(p) for p in check.scan_history(self.root, rev_range, deny)[0]]

    def deny(self, text: str):
        path = self.tmp / "deny.txt"
        path.write_bytes(text.encode("utf-8"))
        return check.load_deny_list(path)

    def assertHas(self, problems: list[str], fragment: str) -> None:
        self.assertTrue(any(fragment in p for p in problems), f"{fragment!r} not in {problems}")

    def run_main(self, *argv: str, root: Path | None = None) -> tuple[int, str]:
        out = io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(out):
            code = check.main(["--root", str(root or self.root), *argv])
        return code, out.getvalue()

    def tricky_history(self) -> tuple[str, str]:
        """A root commit with a leak, then edits that look like diff headers and sit in separate hunks."""
        lines = ["# Guide", "two", "three", "four", "-- old", "six", self.LEAK, "", "nine", "ten", "eleven", "twelve"]
        root = self.commit("Add guide", {"guides/a.md": "\n".join(lines) + "\n"})
        lines[1], lines[4], lines[9] = "++ b/fake.png", "five", "mail amy@" "corp.com"
        return root, self.commit("Edit guide", {"guides/a.md": "\n".join(lines) + "\n"})

    def check_tricky_history(self, root: str, edit: str) -> None:
        problems = self.scan()
        self.assertHas(problems, f"{root[:8]} guides/a.md:7: email address")
        self.assertHas(problems, f"{edit[:8]} guides/a.md:10: email address")
        self.assertEqual(len(problems), 2, problems)  # in particular, no .png problem for the "+++ b/fake.png" line

    def test_a_leak_that_was_added_and_removed_is_still_found(self) -> None:
        self.commit("Add guide", {"guides/a.md": "# Guide\n"})
        leaked = self.commit("Add contact", {"guides/a.md": f"# Guide\n\n{self.LEAK}\n"})
        self.commit("Remove contact", {"guides/a.md": "# Guide\n"})
        tree: list[check.Problem] = []
        check.check_privacy("guides/a.md", (self.root / "guides/a.md").read_text(encoding="utf-8"), [], tree)
        self.assertEqual(tree, [])  # the working tree is clean, which is why history needs its own scan
        problems = self.scan()
        self.assertHas(problems, f"{leaked[:8]} guides/a.md:3: email address")
        self.assertEqual(len(problems), 1, problems)

    def test_messages_are_checked_and_cannot_pose_as_diffs(self) -> None:
        fake_diff = "diff --git a/evil.png b/evil.png\nnew file mode 100644\n@@ -0,0 +1 @@\n+hello"
        self.commit("Add notes\n\nCo-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>\n\n" + fake_diff)
        leaked = self.commit(f"Add contact\n\n{self.LEAK}")
        problems = self.scan()
        self.assertHas(problems, f"{leaked[:8]} (commit message):3: email address")
        self.assertEqual(len(problems), 1, problems)

    def test_deny_list_covers_emails_messages_lines_and_paths_but_not_names(self) -> None:
        deny = self.deny("# terms\nSecretCorp\nre:acme-\\d+\n")
        by_author = self.commit("Add guide", {"guides/a.md": "# Guide\n"}, GIT_AUTHOR_EMAIL=self.CORP)
        by_committer = self.commit("Edit guide", {"guides/a.md": "# Guide\n\ntext\n"}, GIT_COMMITTER_EMAIL=self.CORP)
        in_message = self.commit("Notes for acme-42")
        in_line = self.commit("Edit again", {"guides/a.md": "# Guide\n\ntext\n\nworked at SecretCorp\n"})
        in_path = self.commit("Add notes", {"guides/secretcorp.md": "# Notes\n"})
        self.commit("Named after the term", GIT_AUTHOR_NAME="SecretCorp Fan")
        problems = self.scan(deny=deny)
        self.assertHas(problems, f"{by_author[:8]} (author email): matches deny-list line 2")
        self.assertHas(problems, f"{by_committer[:8]} (committer email): matches deny-list line 2")
        self.assertHas(problems, f"{in_message[:8]} (commit message):1: matches deny-list line 3")
        self.assertHas(problems, f"{in_line[:8]} guides/a.md:5: matches deny-list line 2")
        self.assertHas(problems, f"{in_path[:8]} guides/secretcorp.md: path matches deny-list line 2")
        self.assertEqual(len(problems), 5, problems)
        self.assertFalse(any("secretcorp" in p.lower() for p in problems if "guides/secretcorp.md" not in p), problems)

    def test_range_limits_what_is_scanned(self) -> None:
        old = self.commit("Add contact", {"guides/a.md": f"# Guide\n\n{self.LEAK}\n"})
        self.commit("Clean up", {"guides/a.md": "# Guide\n"})
        self.assertEqual(len(self.scan("HEAD")), 1)
        self.assertEqual(self.scan(f"{old}..HEAD"), [])
        counts = [check.scan_history(self.root, r)[1] for r in ("HEAD", f"{old}..HEAD", "HEAD..HEAD")]
        self.assertEqual(counts, [2, 1, 0])

    def test_merge_commits_are_checked_by_message_and_not_scanned_twice(self) -> None:
        self.commit("Base", {"guides/a.md": "# Guide\n"})
        self.git("checkout", "-q", "-b", "feature")
        leaked = self.commit("Feature", {"guides/b.md": f"# B\n\n{self.LEAK}\n"})
        self.git("checkout", "-q", "main")
        self.commit("Main work", {"guides/c.md": "# C\n"})
        self.git("merge", "-q", "--no-ff", "-m", f"Merge feature\n\n{self.LEAK}", "feature")
        merge = self.git("rev-parse", "HEAD").strip()
        problems = self.scan()
        self.assertHas(problems, f"{leaked[:8]} guides/b.md:3: email address")
        self.assertHas(problems, f"{merge[:8]} (commit message):3: email address")
        self.assertEqual(len(problems), 2, problems)

    def test_forbidden_files_are_reported_where_added_and_binaries_by_name_only(self) -> None:
        self.commit("Base", {"README.md": "# Demo\n", "notes/old.md": "same text\n"})
        added = self.commit("Add files", {"notes/resume.pdf": "text\n", "notes/scan.pdf": "\0" + self.LEAK + "\n"})
        renamed = self.commit("Rename", {"notes/old.md": None, "notes/old.pdf": "same text\n"})
        self.commit("Remove files", {"notes/resume.pdf": None, "notes/scan.pdf": None, "notes/old.pdf": None})
        problems = self.scan()
        self.assertHas(problems, f"{added[:8]} notes/resume.pdf: .pdf files must not be committed")
        self.assertHas(problems, f"{added[:8]} notes/scan.pdf: .pdf files must not be committed")
        self.assertHas(problems, f"{renamed[:8]} notes/old.pdf: .pdf files must not be committed")
        self.assertEqual(len(problems), 3, problems)  # nothing for the deletions, and no email from inside the binary

    def test_diff_lookalikes_and_later_hunks_keep_their_line_numbers(self) -> None:
        self.check_tricky_history(*self.tricky_history())

    def test_git_config_and_environment_cannot_change_what_is_scanned(self) -> None:
        (self.home / ".gitconfig").write_text(HOSTILE_GIT_CONFIG, encoding="utf-8")
        hostile = {"GIT_EXTERNAL_DIFF": str(self.tmp / "no-such-diff-tool"), "GIT_DIFF_OPTS": "--unified=9"}
        with mock.patch.dict(os.environ, hostile):
            root, edit = self.tricky_history()
            # The premise: a plain `git log -p` shows one diff, not two, because the config hides the root commit's.
            self.assertEqual(self.git("log", "-p").count("diff --git"), 1)
            self.check_tricky_history(root, edit)

    def test_a_replace_ref_cannot_hide_a_commit(self) -> None:
        clean = self.commit("Add guide", {"guides/a.md": "# Guide\n"})
        leaked = self.commit("Add contact", {"guides/a.md": f"# Guide\n\n{self.LEAK}\n"})
        self.commit("Remove contact", {"guides/a.md": "# Guide\n"})
        self.git("replace", leaked, clean)
        self.assertNotIn(self.LEAK, self.git("log", "-p"))  # the premise: a plain `git log -p` no longer shows it
        self.assertHas(self.scan(), f"{leaked[:8]} guides/a.md:3: email address")

    def test_paths_with_spaces_quotes_and_non_ascii_are_decoded(self) -> None:
        names = ["notes/my notes.pdf", "notes/caf\u00e9.pdf", "notes/a b/c.pdf"]
        if os.name == "posix":
            names += ['notes/say "hi".pdf', "notes/tab\there.pdf", "notes/back\\slash.pdf"]
        sha = self.commit("Add files", {name: "x\n" for name in names})
        problems = self.scan()
        for name in names:
            self.assertHas(problems, f"{sha[:8]} {name}: .pdf files must not be committed")
        self.assertEqual(len(problems), len(names), problems)

    def test_git_failures_are_errors_not_findings(self) -> None:
        self.commit("Add guide", {"guides/a.md": "# Guide\n"})
        for bad in ("no-such-ref", "no-such..HEAD", "", "--all", "-x"):
            with self.subTest(bad), self.assertRaises(check.HistoryError):
                check.scan_history(self.root, bad)
        with mock.patch.object(check.subprocess, "run", side_effect=FileNotFoundError(2, "No such file")):
            with self.assertRaisesRegex(check.HistoryError, "cannot run git"):
                check.scan_history(self.root, "HEAD")

    def test_main_history_output_and_exit_codes(self) -> None:
        self.commit("One", {"guides/a.md": "# Guide\n"})
        self.assertEqual(self.run_main("--history", "HEAD"), (0, "OK: 1 commit checked (no deny-list supplied)\n"))
        self.commit("Two", {"guides/a.md": f"# Guide\n\n{self.LEAK}\n"})
        code, output = self.run_main("--history", "HEAD")
        self.assertEqual(code, 1)
        self.assertIn("guides/a.md:3: email address", output)
        self.assertTrue(output.endswith("FAIL: 1 problem(s) in 2 commits (no deny-list supplied)\n"), output)
        self.assertEqual(self.run_main("--history", "HEAD~1")[0], 0)
        self.assertEqual(self.run_main("--history", "no-such-ref")[0], 2)
        self.assertEqual(self.run_main("--history", "")[0], 2)
        with self.assertRaises(SystemExit):  # argparse reads "-x" as an option, so the usage error exits with 2
            self.run_main("--history", "-x")
        self.assertEqual(self.run_main("--history", "HEAD", root=self.home)[0], 2)  # not a repository

    def hooked_remote(self):
        """Connect this repository to a bare remote, with the real pre-push hook. Returns push() and remote_branches()."""
        source = Path(check.__file__).resolve().parent.parent
        (self.root / "tools").mkdir()
        shutil.copy(source / "tools" / "check.py", self.root / "tools" / "check.py")  # the hook runs the checker next to it
        (self.root / ".git" / "info").mkdir(exist_ok=True)
        (self.root / ".git" / "info" / "exclude").write_bytes(b"tools/\n")
        remote = self.tmp / "remote.git"
        self.git("init", "-q", "--bare", str(remote))
        self.git("remote", "add", "origin", str(remote))
        self.git("config", "core.hooksPath", str(source / ".githooks"))

        def push(*args: str, path: str | None = None) -> tuple[int, str]:
            env = {**os.environ, "PATH": path} if path else os.environ.copy()
            done = subprocess.run(["git", "-C", str(self.root), "push", *args], stdout=subprocess.PIPE,
                                  stderr=subprocess.STDOUT, env=env)
            return done.returncode, done.stdout.decode("utf-8", "replace")

        def remote_branches() -> list[str]:
            return self.git("--git-dir", str(remote), "for-each-ref", "--format=%(refname:short)", "refs/heads").split()

        return push, remote_branches

    @unittest.skipIf(os.name == "nt", "the hook is a POSIX shell script")
    def test_pre_push_hook_checks_only_what_is_pushed(self) -> None:
        push, remote_branches = self.hooked_remote()
        self.commit("Add guide", {"guides/a.md": "# Guide\n"})
        code, output = push("origin", "main")
        self.assertEqual(code, 0, output)
        self.assertIn("1 commit checked", output)

        self.commit("Extend guide", {"guides/a.md": "# Guide\n\nmore\n"})
        code, output = push("origin", "main")  # an update: only the commits the remote lacks are checked
        self.assertEqual(code, 0, output)
        self.assertIn("1 commit checked", output)

        code, output = push("origin", "main:refs/tags/v1")  # the commit is already on the remote, so nothing is checked
        self.assertEqual(code, 0, output)
        self.assertNotIn("checked", output)

        self.git("checkout", "-q", "-b", "fine")
        self.commit("Edit guide", {"guides/a.md": "# Guide\n\ntext\n"})
        code, output = push("origin", "fine")  # a new branch: only its own commit is checked, not main's again
        self.assertEqual(code, 0, output)
        self.assertIn("1 commit checked", output)

        code, output = push("origin", "--delete", "fine")  # nothing is pushed, so there is nothing to check
        self.assertEqual(code, 0, output)
        self.assertEqual(remote_branches(), ["main"])

    @unittest.skipIf(os.name == "nt", "the hook is a POSIX shell script")
    def test_pre_push_hook_refuses_leaks_and_fails_closed(self) -> None:
        push, remote_branches = self.hooked_remote()
        self.commit("Add guide", {"guides/a.md": "# Guide\n"})
        self.assertEqual(push("origin", "main")[0], 0)

        self.git("checkout", "-q", "-b", "leaky")
        self.commit("Add contact", {"guides/a.md": f"# Guide\n\n{self.LEAK}\n"})
        self.commit("Remove contact", {"guides/a.md": "# Guide\n"})
        code, output = push("origin", "leaky")  # the files are clean again, but the first commit would be published
        self.assertNotEqual(code, 0, output)
        self.assertIn("guides/a.md:3: email address", output)
        self.assertEqual(remote_branches(), ["main"])

        self.git("checkout", "-q", "-b", "fine", "main")
        self.commit("Add notes", {"guides/b.md": "# B\n"})
        for refs in (("fine", "leaky"), ("leaky", "fine")):  # one bad ref stops the whole push, in either order
            code, output = push("origin", *refs)
            self.assertNotEqual(code, 0, output)
            self.assertEqual(remote_branches(), ["main"])

        bin_dir = self.tmp / "bin"
        bin_dir.mkdir()
        for tool in ("git", "tail"):
            (bin_dir / tool).symlink_to(str(shutil.which(tool)))
        code, output = push("origin", "fine", path=str(bin_dir))  # without Python the commits cannot be checked
        self.assertNotEqual(code, 0, output)
        self.assertIn("Python 3 not found", output)
        self.assertEqual(remote_branches(), ["main"])
        code, output = push("origin", "fine")  # the same push succeeds once Python is available
        self.assertEqual(code, 0, output)
        self.assertEqual(remote_branches(), ["fine", "main"])


if __name__ == "__main__":
    unittest.main()
