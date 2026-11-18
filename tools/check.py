#!/usr/bin/env python3
"""Consistency and privacy checks for peer-kit.

    python tools/check.py
    python tools/check.py --deny-list ~/peer-kit-deny.txt

Checks markdown links and anchors, that every guide/skill/template is reachable
from README.md, skill frontmatter and standalone-ness, CSV shape, whitespace,
forbidden file types, and privacy patterns (machine paths, emails, secrets, and an
optional private deny-list). Standard library only; PyYAML is used for stricter
frontmatter parsing when it is installed. Exit status is 1 if any problem is found.

Deny-list file: one term per line, matched case-insensitively as a whole word on a
single line; start a line with "re:" for a regular expression; "#" at the start of a
line or after whitespace starts a comment. Keep that file outside this repository.
Matches are reported by line number, never by term.
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import re
import subprocess
import sys
from collections import deque
from pathlib import Path
from typing import Dict, Iterator, List, NamedTuple, Optional, Set, Tuple
from urllib.parse import unquote

try:
    import yaml  # type: ignore
except ImportError:
    yaml = None

CONTENT_DIRS = ("guides", "skills", "templates", "examples", "exercises")
CHECKED_PATH_ROOTS = CONTENT_DIRS + ("tools",)
SKIP_DIRS = {".git", "node_modules", "__pycache__", ".venv"}
TEXT_SUFFIXES = {".md", ".csv", ".json", ".yml", ".yaml", ".txt", ".py", ".js", ".mjs", ".cjs", ".ts", ".sh"}
FORBIDDEN_SUFFIXES = {
    ".pdf", ".doc", ".docx", ".rtf", ".pages", ".zip", ".tar", ".gz",
    ".pem", ".key", ".p12", ".pfx", ".log",
    ".ppt", ".pptx", ".xls", ".xlsx", ".odt", ".tgz", ".7z", ".rar", ".bz2", ".xz",
    ".jks", ".keystore", ".sqlite", ".db", ".mp4", ".mov", ".heic",
}
MAX_FILE_BYTES = 1_000_000
MAX_SKILL_LINES = 500
SKILL_KEYS = {"name", "description", "license", "compatibility", "metadata", "allowed-tools"}
SKILL_NAME = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
FRONTMATTER = re.compile(r"\A---\r?\n(.*?)\r?\n---[ \t]*(?:\r?\n|\Z)", re.S)

FENCE = re.compile(r"^[ \t>]*(`{3,}(?=[^`]*$)|~{3,})")
HEADING = re.compile(r"^ {0,3}#{1,6}[ \t]+(.*?)[ \t]*#*[ \t]*$")
INLINE_CODE = re.compile(r"(?<!`)(`+)(?!`)(.+?)(?<!`)\1(?!`)")
LINK = re.compile(
    r"!?\[(?:[^\[\]\\]|\\.|\[[^\[\]]*\])*\]\(\s*(<[^>\n]*>|(?:[^()\s]|\([^()\s]*\))*)"
)
REF_DEF = re.compile(r"^ {0,3}\[(?!\^)[^\]]+\]:\s*(<[^>]*>|\S+)(?:\s+(?:\"[^\"]*\"|'[^']*'|\([^)]*\)))?\s*$")
HTML_ID = re.compile(r"\b(?:id|name)\s*=\s*[\"']([^\"']+)[\"']", re.I)
EXTERNAL = re.compile(r"^[A-Za-z][A-Za-z0-9+.-]*:")

EMAIL = re.compile(r"(?<![A-Za-z0-9._%+-])[A-Za-z0-9._%+-]+@([A-Za-z0-9-]+(?:\.[A-Za-z0-9-]+)*\.[A-Za-z]{2,})")
ALLOWED_EMAIL_DOMAINS = {"example.com", "example.org", "example.net", "users.noreply.github.com"}
ALLOWED_EMAIL_ADDRESSES = {"git@github.com", "noreply@github.com", "noreply@anthropic.com"}
GENERIC_HOME_NAMES = {"you", "your-name", "yourname", "name", "user", "username", "me", "someone", "example", "runner"}
HOME_PATH = re.compile(  # POSIX names are case-sensitive on purpose, so API routes such as /users/42 pass
    r"(?<![\w.~-])(?:/Users/|/home/)([A-Za-z0-9._-]+)(?![A-Za-z0-9._-])"
    r"|(?i:[A-Za-z]:\\{1,2}Users\\{1,2})([^\\\s\"'`]+)"
)
PRIVACY_PATTERNS = [
    ("agent session path", re.compile(r"[.]copilot/session-state|[.]claude/projects/|[.]codex/sessions")),
    ("private key", re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY( BLOCK)?-----")),
    ("GitHub token", re.compile(r"\b(?:gh[pousr]_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{20,})\b")),
    ("AWS access key id", re.compile(r"\b(?:AKIA|ASIA)[0-9A-Z]{16}\b")),
    ("Slack token", re.compile(r"\bxox[abprs]-[A-Za-z0-9-]{10,}")),
    ("API secret key", re.compile(r"\bsk-[A-Za-z0-9_-]{20,}")),
    ("Google API key", re.compile(r"\bAIza[0-9A-Za-z_-]{35}")),
    ("JSON web token", re.compile(r"\beyJ[A-Za-z0-9_-]{10,}\.eyJ[A-Za-z0-9_-]{10,}\.")),
]


class Problem(NamedTuple):
    path: str
    line: int
    message: str

    def __str__(self) -> str:
        where = f"{self.path}:{self.line}" if self.line else self.path
        return f"{where}: {self.message}"


def rel(root: Path, path: Path) -> str:
    return path.relative_to(root).as_posix()


def lines_of(text: str) -> List[str]:
    """Split on \\n, \\r\\n and \\r only; str.splitlines() also splits on U+2028, \\x0c, \\x85 and shifts line numbers."""
    lines = re.split(r"\r\n|\r|\n", text)
    return lines[:-1] if lines and lines[-1] == "" else lines


def exists_exact_case(root: Path, dest: Path) -> bool:
    """Existence check that is case-sensitive on every OS (macOS and Windows would accept 'B.MD', Linux CI would not)."""
    current = root
    try:
        for part in dest.relative_to(root).parts:
            if part not in os.listdir(current):
                return False
            current = current / part
    except (OSError, ValueError):
        return False
    return True


def list_files(root: Path) -> List[Path]:
    """Files that are or could be committed: tracked plus untracked-but-not-ignored."""
    if (root / ".git").exists():
        try:
            out = subprocess.run(
                ["git", "-C", str(root), "ls-files", "-z", "--cached", "--others", "--exclude-standard"],
                stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, check=True,
            ).stdout.decode("utf-8", "surrogateescape")
        except (OSError, subprocess.CalledProcessError):
            out = None
        if out is not None:
            paths = (root / name for name in out.split("\0") if name)
            return sorted(p for p in paths if p.is_symlink() or p.exists())
    found: List[Path] = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = sorted(d for d in dirnames if d not in SKIP_DIRS)
        found.extend(Path(dirpath) / name for name in sorted(filenames))
    return found


def outside_fences(text: str, unclosed: Optional[List[int]] = None) -> Iterator[Tuple[int, str]]:
    """Yield (line number, raw line) for markdown lines that are not inside fenced code."""
    fence: Optional[str] = None
    opened = 0
    for number, line in enumerate(lines_of(text), 1):
        match = FENCE.match(line)
        if fence:
            closing = line.lstrip(" \t>").rstrip()
            if match and closing[0] == fence[0] and len(match.group(1)) >= len(fence) and not closing.strip(fence[0]):
                fence = None
            continue
        if match:
            fence, opened = match.group(1), number
            continue
        yield number, line
    if fence and unclosed is not None:
        unclosed.append(opened)


def slugify(heading: str) -> str:
    """Approximate GitHub heading anchor (duplicate suffixes are added by the caller).

    Headings with emoji, underscores, or HTML entities can differ from GitHub's anchors.
    """
    text = re.sub(r"!?\[([^\]]*)\]\([^)]*\)", r"\1", heading)
    text = re.sub(r"<[^>]+>", "", text).strip().lower()
    return re.sub(r"[^\w\- ]", "", text).replace(" ", "-")


def heading_anchors(text: str) -> Set[str]:
    seen: Dict[str, int] = {}
    anchors: Set[str] = set()
    for _, line in outside_fences(text):
        heading = HEADING.match(line)
        if heading:
            slug = slugify(heading.group(1))
            count = seen.get(slug, 0)
            seen[slug] = count + 1
            anchors.add(slug if count == 0 else f"{slug}-{count}")
        anchors.update(HTML_ID.findall(line))
    return {a.lower() for a in anchors}


class MarkdownInfo:
    def __init__(self) -> None:
        self.edges: Dict[Path, Set[Path]] = {}
        self.links: List[Tuple[Path, int, Path]] = []
        self.code_paths: List[Tuple[Path, int, str]] = []


def scan_markdown(root: Path, texts: Dict[Path, str], problems: List[Problem]) -> MarkdownInfo:
    info = MarkdownInfo()
    md_files = [p for p in texts if p.suffix.lower() == ".md"]
    anchors = {p: heading_anchors(texts[p]) for p in md_files}
    for path in md_files:
        info.edges[path] = set()
        unclosed: List[int] = []
        for number, line in outside_fences(texts[path], unclosed):
            visible = INLINE_CODE.sub("", line)
            targets = [m.group(1) for m in LINK.finditer(visible)]
            ref = REF_DEF.match(visible)
            if ref:
                targets.append(ref.group(1))
            for target in targets:
                check_link(root, path, number, target, anchors, info, problems)
            for span in INLINE_CODE.finditer(line):
                info.code_paths.append((path, number, span.group(2).strip()))
        if unclosed:
            problems.append(Problem(rel(root, path), unclosed[0], "code fence is never closed; the rest of the file is not checked"))
    return info


def check_link(
    root: Path, path: Path, number: int, target: str,
    anchors: Dict[Path, Set[str]], info: MarkdownInfo, problems: List[Problem],
) -> None:
    target = target.strip()
    if target.startswith("<") and target.endswith(">"):
        target = target[1:-1]
    if not target or EXTERNAL.match(target):
        return
    base, _, fragment = target.partition("#")
    base = unquote(base.split("?", 1)[0])
    where = rel(root, path)
    try:
        dest = path if not base else (path.parent / base).resolve()
        inside = dest == root or root in dest.parents
        found = inside and exists_exact_case(root, dest)
    except (OSError, ValueError, RuntimeError):  # name too long, NUL byte, symlink loop
        problems.append(Problem(where, number, f"broken link: {target}"))
        return
    if not inside:
        problems.append(Problem(where, number, f"link leaves the repository: {target}"))
        return
    if not found:
        problems.append(Problem(where, number, f"broken link: {target}"))
        return
    if dest.is_dir():
        info.links.append((path, number, dest))
        for index in ("README.md", "SKILL.md"):
            if (dest / index).is_file():
                info.edges[path].add(dest / index)
    else:
        info.edges[path].add(dest)
        info.links.append((path, number, dest))
    if fragment and dest.is_file() and dest.suffix.lower() == ".md":
        wanted = unquote(fragment).lower()
        if wanted not in anchors.get(dest, set()):
            problems.append(Problem(where, number, f"missing anchor #{wanted} in {rel(root, dest)}"))


def check_code_paths(root: Path, info: MarkdownInfo, problems: List[Problem]) -> None:
    """A backticked path under a repo content folder must exist (catches stale references after renames)."""
    for path, number, span in info.code_paths:
        first = span.split("/", 1)[0]
        if "/" not in span or first not in CHECKED_PATH_ROOTS or re.search(r"[\s<>*{}$|]|\.\.\.", span):
            continue
        target = os.path.normpath(span.partition("#")[0])
        if not any(exists_exact_case(root, base / target) for base in (root, path.parent)):
            problems.append(Problem(rel(root, path), number, f"`{span}` does not exist in this repository"))


def check_reachability(root: Path, files: List[Path], info: MarkdownInfo, problems: List[Problem]) -> None:
    start = root / "README.md"
    if not start.is_file():
        problems.append(Problem("README.md", 0, "missing"))
        return
    reached = {start}
    queue = deque([start])
    while queue:
        for nxt in info.edges.get(queue.popleft(), ()):
            if nxt not in reached:
                reached.add(nxt)
                queue.append(nxt)
    for path in files:
        parts = path.relative_to(root).parts
        if parts[0] in CONTENT_DIRS and len(parts) > 1 and path.suffix.lower() in {".md", ".csv"} and path not in reached:
            problems.append(Problem(rel(root, path), 0, "not reachable from README.md through links"))


def read_frontmatter(text: str) -> Tuple[Optional[Dict[str, object]], List[str]]:
    match = FRONTMATTER.match(text)
    if not match:
        return None, ["missing YAML frontmatter delimited by ---"]
    block = match.group(1)
    errors: List[str] = []
    for line in block.splitlines():
        key, sep, value = line.partition(":")
        if line[:1].isspace() or not sep or not key.strip():
            continue
        value = value.strip()
        if not value or value[0] in "\"'>|[{&*!":
            continue
        if ": " in value:
            errors.append(f"'{key}' contains an unquoted ': ' (quote the value)")
        if " #" in value:
            errors.append(f"'{key}' contains ' #', which YAML treats as a comment (quote the value)")
    if yaml is not None:
        try:
            fields = yaml.safe_load(block)
        except (yaml.YAMLError, ValueError) as exc:  # ValueError: PyYAML builds datetime.date for 2024-13-45
            return None, errors + [f"invalid YAML: {str(exc).splitlines()[0]}"]
        if not isinstance(fields, dict):
            return None, errors + ["frontmatter is not a mapping"]
        return fields, errors
    fields = {}
    last = None
    for line in block.splitlines():
        if not line.strip() or line.lstrip().startswith("#") or line.startswith("- "):
            continue
        if line[:1].isspace() and last:
            fields[last] = f"{fields[last]} {line.strip()}".strip()
            continue
        key, sep, value = line.partition(":")
        if not sep:
            errors.append(f"unparseable frontmatter line: {line!r}")
            continue
        last = key.strip()
        value = value.strip()
        if len(value) > 1 and value[0] == value[-1] and value[0] in "\"'":
            value = value[1:-1]
        fields[last] = "" if value in {">", "|", ">-", "|-"} else value
    return fields, errors


def check_skills(root: Path, files: List[Path], texts: Dict[Path, str], info: MarkdownInfo,
                 problems: List[Problem]) -> None:
    names: Set[str] = set()
    for path in files:
        parts = path.relative_to(root).parts
        if parts[0] == "skills" and len(parts) >= 3:
            names.add(parts[1])
    for name in sorted(names):
        folder = root / "skills" / name
        skill_md = folder / "SKILL.md"
        where = rel(root, skill_md)
        if skill_md not in texts:
            problems.append(Problem(rel(root, folder), 0, "skill folder has no SKILL.md"))
            continue
        text = texts[skill_md]
        fields, errors = read_frontmatter(text)
        for error in errors:
            problems.append(Problem(where, 1, error))
        if fields is not None:
            check_skill_fields(where, name, fields, problems)
        if text.count("\n") > MAX_SKILL_LINES:
            problems.append(Problem(where, 0, f"longer than {MAX_SKILL_LINES} lines; move detail into references/"))
        for path, number, dest in info.links:
            if folder in path.parents and dest != folder and folder not in dest.parents:
                problems.append(Problem(rel(root, path), number,
                                        f"skill links outside its own folder ({rel(root, dest)}); skills must stand alone"))
        for path, number, span in info.code_paths:
            if folder not in path.parents or "/" not in span or span.lstrip("./").split("/", 1)[0] not in CHECKED_PATH_ROOTS:
                continue
            if not exists_exact_case(root, folder / os.path.normpath(span.partition("#")[0])):
                problems.append(Problem(rel(root, path), number,
                                        f"skill refers to repository path `{span}`; skills must stand alone"))


def check_skill_fields(where: str, folder_name: str, fields: Dict[str, object], problems: List[Problem]) -> None:
    unknown = sorted(set(map(str, fields)) - SKILL_KEYS)
    if unknown:
        problems.append(Problem(where, 1, f"frontmatter keys outside the Agent Skills spec: {', '.join(unknown)}"))
    name = fields.get("name")
    if not isinstance(name, str) or not name.strip():
        problems.append(Problem(where, 1, "missing 'name'"))
    else:
        if not SKILL_NAME.match(name) or len(name) > 64:
            problems.append(Problem(where, 1, f"name {name!r} must be 1-64 lowercase letters, digits, single hyphens"))
        if name != folder_name:
            problems.append(Problem(where, 1, f"name {name!r} must match its folder name {folder_name!r}"))
    description = fields.get("description")
    if not isinstance(description, str) or not description.strip():
        problems.append(Problem(where, 1, "missing 'description'"))
    else:
        if len(description) > 1024:
            problems.append(Problem(where, 1, f"description is {len(description)} characters; the limit is 1024"))
        if re.search(r"</?[A-Za-z][^>]*>", description):
            problems.append(Problem(where, 1, "description must not contain angle brackets"))
    compat = fields.get("compatibility")
    if "compatibility" in fields and not (isinstance(compat, str) and 1 <= len(compat.strip()) <= 500):
        problems.append(Problem(where, 1, "compatibility must be a string of 1-500 characters"))
    meta, tools = fields.get("metadata"), fields.get("allowed-tools")
    if yaml is not None:  # the no-PyYAML fallback parser flattens nested values into strings
        if meta is not None and not (isinstance(meta, dict) and all(isinstance(k, str) and isinstance(v, str) for k, v in meta.items())):
            problems.append(Problem(where, 1, 'metadata must map string keys to string values (quote numbers: version: "1.0")'))
        if tools is not None and not isinstance(tools, str):
            problems.append(Problem(where, 1, "allowed-tools must be one space-separated string, not a list"))


def check_csv(root: Path, path: Path, text: str, problems: List[Problem]) -> None:
    where = rel(root, path)
    try:
        rows = list(csv.reader(lines_of(text)))
    except csv.Error as exc:  # e.g. NUL bytes on Python 3.9
        problems.append(Problem(where, 0, f"malformed CSV: {exc}"))
        return
    if not rows or not any(rows[0]):
        problems.append(Problem(where, 1, "CSV has no header row"))
        return
    header = rows[0]
    if len(set(header)) != len(header):
        problems.append(Problem(where, 1, "duplicate column names"))
    for number, row in enumerate(rows[1:], 2):
        if len(row) != len(header):
            problems.append(Problem(where, number, f"{len(row)} columns, header has {len(header)}"))


def check_privacy(where: str, text: str, deny: List[Tuple[int, "re.Pattern[str]"]],
                  problems: List[Problem]) -> None:
    for number, line in enumerate(lines_of(text), 1):
        for match in EMAIL.finditer(line):
            domain = match.group(1).lower()
            if match.group(0).lower() in ALLOWED_EMAIL_ADDRESSES:
                continue
            if not any(domain == d or domain.endswith("." + d) for d in ALLOWED_EMAIL_DOMAINS):
                problems.append(Problem(where, number, "email address (use an example.com address or remove it)"))
        for match in HOME_PATH.finditer(line):
            owner = (match.group(1) or match.group(2) or "").lower()
            if owner not in GENERIC_HOME_NAMES:
                problems.append(Problem(where, number, "absolute home-directory path (remove or generalize it)"))
        for label, pattern in PRIVACY_PATTERNS:
            if pattern.search(line):
                problems.append(Problem(where, number, label))
        for entry, pattern in deny:
            if pattern.search(line):
                problems.append(Problem(where, number, f"matches deny-list line {entry}"))


def check_whitespace(where: str, text: str, problems: List[Problem]) -> None:
    if "\r" in text:
        problems.append(Problem(where, 0, "CRLF line endings; use LF"))
    for number, line in enumerate(lines_of(text), 1):
        if line != line.rstrip():
            problems.append(Problem(where, number, "trailing whitespace"))
    if text and not text.endswith("\n"):
        problems.append(Problem(where, 0, "missing newline at end of file"))
    elif text.endswith("\n\n"):
        problems.append(Problem(where, 0, "extra blank line at end of file"))


def check_file_policy(root: Path, path: Path, problems: List[Problem]) -> None:
    where = rel(root, path)
    name = path.name
    if path.is_symlink():
        problems.append(Problem(where, 0, "symlinks are not allowed"))
    elif path.suffix.lower() in FORBIDDEN_SUFFIXES:
        problems.append(Problem(where, 0, f"{path.suffix} files must not be committed"))
    elif name in {".DS_Store", ".npmrc", ".env"} or (name.startswith(".env.") and not name.endswith((".example", ".sample", ".template"))):
        problems.append(Problem(where, 0, "local environment or config file must not be committed"))
    elif path.stat().st_size > MAX_FILE_BYTES:
        problems.append(Problem(where, 0, "file is larger than 1 MB"))


def load_deny_list(path: Path) -> List[Tuple[int, "re.Pattern[str]"]]:
    entries = []
    for number, raw in enumerate(path.read_text(encoding="utf-8-sig").splitlines(), 1):
        line = re.sub(r"\s+#.*$", "", raw.strip())  # a trailing "  # note" is a comment too, as documented
        if not line or line.startswith("#"):
            continue
        try:
            if line.startswith("re:"):
                body = line[3:].strip()
                if not body:
                    raise ValueError("empty regular expression")
                entries.append((number, re.compile(body, re.I)))
            else:
                entries.append((number, re.compile(r"(?<![^\W_])" + re.escape(line) + r"(?![^\W_])", re.I)))
        except (re.error, ValueError) as exc:
            raise ValueError(f"deny-list line {number}: {exc}")
    return entries


def run(root: Path, deny: Optional[List[Tuple[int, "re.Pattern[str]"]]] = None) -> Tuple[List[Problem], int]:
    root = root.resolve()
    deny = deny or []
    problems: List[Problem] = []
    files = list_files(root)
    texts: Dict[Path, str] = {}
    for path in files:
        where = rel(root, path)
        check_file_policy(root, path, problems)
        for entry, pattern in deny:
            if pattern.search(where):
                problems.append(Problem(where, 0, f"path matches deny-list line {entry}"))
        if path.is_symlink():
            continue
        is_text = path.suffix.lower() in TEXT_SUFFIXES
        try:
            if path.stat().st_size > MAX_FILE_BYTES:
                continue
            text = path.read_bytes().decode("utf-8")  # read_text() would fold CRLF into LF before check_whitespace sees it
        except UnicodeDecodeError:
            if is_text:
                problems.append(Problem(where, 0, "not valid UTF-8"))
            continue
        except OSError as exc:
            problems.append(Problem(where, 0, f"cannot read file: {exc.strerror or exc}"))
            continue
        if text.startswith("\ufeff"):
            problems.append(Problem(where, 1, "starts with a UTF-8 byte-order mark; save the file without BOM"))
            text = text[1:]
        check_privacy(where, text, deny, problems)
        if not is_text:
            continue
        texts[path] = text
        check_whitespace(where, text, problems)
        if path.suffix.lower() == ".csv":
            check_csv(root, path, text, problems)
        elif path.suffix.lower() == ".json":
            try:
                json.loads(text)
            except ValueError as exc:
                problems.append(Problem(where, 0, f"invalid JSON: {exc}"))
    info = scan_markdown(root, texts, problems)
    listed = set(files)
    for path, number, dest in info.links:
        if dest.is_file() and dest not in listed:
            problems.append(Problem(rel(root, path), number, f"link target {rel(root, dest)} is ignored by git, so it will not be published"))
    check_code_paths(root, info, problems)
    check_reachability(root, files, info, problems)
    check_skills(root, files, texts, info, problems)
    return sorted(problems, key=lambda p: (p.path, p.line, p.message)), len(files)


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parent.parent,
                        help="repository root (default: the parent of tools/)")
    parser.add_argument("--deny-list", type=Path, default=os.environ.get("PEER_KIT_DENY_LIST") or None,
                        help="private file of terms that must not appear (env: PEER_KIT_DENY_LIST)")
    args = parser.parse_args(argv)
    if not args.root.is_dir():
        print(f"repository root not found: {args.root}", file=sys.stderr)
        return 2
    deny = None
    if args.deny_list:
        deny_path = Path(args.deny_list).expanduser()
        if not deny_path.is_file():
            print(f"deny-list file not found: {deny_path}", file=sys.stderr)
            return 2
        try:
            deny = load_deny_list(deny_path)
        except (OSError, ValueError) as exc:  # UnicodeDecodeError is a ValueError
            print(f"cannot use deny-list {deny_path}: {exc}", file=sys.stderr)
            return 2
    problems, count = run(args.root, deny)
    for problem in problems:
        print(problem)
    suffix = f" (deny-list: {len(deny)} term(s))" if deny is not None else " (no deny-list supplied)"
    if problems:
        print(f"FAIL: {len(problems)} problem(s) in {count} files{suffix}")
        return 1
    print(f"OK: {count} files checked{suffix}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
