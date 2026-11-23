# Security policy

This repository holds guides, coaching skills, templates, and a small checker. It runs no service and collects no data, so the realistic problems are narrow:

- A flaw in the checker (`tools/check.py`), the pre-push hook (`.githooks/pre-push`), or the GitHub Actions workflow (`.github/workflows/check.yml`). For example, a way to make them run a command or read a file you did not intend, or to pass a check that should fail.
- Text in a skill or in `AGENTS.md` that could lead an assistant to leak, publish, or save someone's private material, or to run something harmful.
- Private or personal information that has ended up in the repository, a pull request, an issue, or a discussion.

## Report it privately

Use GitHub's private reporting: [report a vulnerability](https://github.com/AndreEPaul/swe-interview-prep-kit/security/advisories/new), or open the repository's Security tab and choose **Report a vulnerability**. The report is visible only to you and the repository's administrators.

Please don't open a public issue, discussion, or pull request for any of these, so the problem is not public before it is fixed. Say what you found, where (the file and line, or the exact text), and how to reproduce it. Don't paste real private material: describe it, or use a synthetic example.

## What to expect

This is a small project, so replies are best-effort: there is no guaranteed response time and no bounty. Fixes go into `main` and the next release, and only the latest release and `main` are supported. If you would like to be credited, say so in your report.

Anything else, such as a wrong claim, a broken link, or a suggestion, is not a security matter. See [CONTRIBUTING](./CONTRIBUTING.md) for how to raise it.
