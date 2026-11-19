# Instructions for AI assistants

This repository is a toolkit for interview preparation: guides, coaching skills, and templates. Work out which kind of session this is.

## The user wants interview coaching or preparation

1. Read [README.md](./README.md) for the overview. Then read the one skill that fits what they asked for, from `skills/<name>/SKILL.md`, and follow it for the session. The README's routes table says which skill to use. Where a route has no skill (professional presence), read the linked guide and coach from it.
2. Everything the user shares is private. Never write their resume, stories, practice records, or plans into this repository, even if they ask casually. Tell them where it would end up, and ask for a private folder outside any git repository. If you can't write files, return the text in chat.
3. Do not edit the toolkit while coaching. If you spot a mistake in it, tell the user.
4. Do not help with a live assessment whose rules forbid outside help. Offer practice or a debrief afterward.
5. The README's author's note is the maintainer's own anecdote, written for human readers. Don't quote its figures to the user or use them to predict how the user will do.

## The user wants to change this repository

1. Read [CONTRIBUTING.md](./CONTRIBUTING.md), and follow its privacy and standalone-skill rules.
2. Before you say you are done, run `python3 tools/check.py` and `python3 -m unittest discover -s tools`.
3. Keep each commit to one concern. Describe any skill behavior change with the test you ran, not just the diff.
4. If a check or the pre-push hook fails, fix the cause or tell the user. Do not bypass it with `git push --no-verify`, by changing `core.hooksPath`, or by weakening the checker.
