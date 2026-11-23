# Instructions for AI assistants

This repository is a toolkit for interview preparation: guides, coaching skills, and templates. People use it in three ways, and all three are welcome. Work out which one this session is:

- **Coaching or preparation:** they want to prepare for an interview.
- **Customizing their own copy:** they want to change the kit for themselves, in a clone or fork, with nothing sent back.
- **Contributing:** they want to improve the shared repository and send a change back.

If a request could be either of the last two (for example, "change the README intro" with no other context), ask once whether the change is for their own copy or to send back, or say which you are assuming. A session can move between paths: coaching can lead to a change, and a change can turn into a contribution.

## On every path

- Everything the user shares is private. Never write their resume, stories, practice records, or plans into this repository, not even in their own clone or fork, and even if they ask casually. Tell them where it would end up, and ask for a private folder outside any git repository. If you can't write files, return the text in chat.
- Do not help with a live assessment whose rules forbid outside help. Offer practice or a debrief afterward.

## The user wants interview coaching or preparation

1. Read [README.md](./README.md) for the overview. Then read the one skill that fits what they asked for, from `skills/<name>/SKILL.md`, and follow it for the session. The README's routes table says which skill to use. Where a route has no skill (professional presence), read the linked guide and coach from it.
2. Don't change the toolkit on your own while coaching. If you spot a mistake or a gap in it, or the user says something in it didn't work for them, tell them, and mention that they can report it (see the last section). If they ask you to change it, switch to one of the two paths below.
3. The README's author's note is the maintainer's own anecdote, written for human readers. Don't quote its figures to the user or use them to predict how the user will do.

## The user wants to change their own copy

This is encouraged. A clone or fork is theirs to adapt: their language, their target roles, a coach tuned to how they work. They don't need permission, and the contribution rules don't apply to their copy.

- Make the changes they ask for, in any file. Don't apply [CONTRIBUTING.md](./CONTRIBUTING.md) or its checks, commit, and testing rules, and don't refuse or warn about edits to the checker, hooks, or workflows in their copy. `python3 tools/check.py` is there if they want it; whether they run it is up to them.
- If a change looks useful to others too, say so once and mention they can send it back (see the last section). Don't push, open an issue or pull request, or post anything unless they ask.
- If they plan to publish their version, point them to the README's License section, which asks for credit, and suggest running `python3 tools/check.py` first, since it also catches private details.

## The user wants to send a change back

This is encouraged too. Corrections, ideas, questions, and "this didn't work for me" reports all help.

- Point them to the right place. [Discussions](https://github.com/AndreEPaul/swe-interview-prep-kit/discussions) are for questions, ideas, and how they have used or adapted the kit. [Issues](https://github.com/AndreEPaul/swe-interview-prep-kit/issues) are for something wrong, unclear, or missing. [Pull requests](https://github.com/AndreEPaul/swe-interview-prep-kit/pulls) are for changes: a small fix can go straight to one, and anything larger should start with an issue or discussion.
- Offer to help write it up in general terms, with no personal details, employer names, or other people's information. Don't post or file anything for them unless they ask.

When you prepare a change for them:

1. Read [CONTRIBUTING.md](./CONTRIBUTING.md), and follow its privacy and standalone-skill rules.
2. Start a new branch from the latest `main`. If the idea began in a customized copy, bring over only the general improvement, not personal or company-specific edits.
3. Before you say you are done, run `python3 tools/check.py` and `python3 -m unittest discover -s tools`.
4. Keep each commit to one concern. Describe any skill behavior change with the test you ran, not just the diff.
5. If a check or the pre-push hook fails, fix the cause or tell the user. Do not bypass it with `git push --no-verify`, by changing `core.hooksPath`, or by weakening the checker.
6. If they ask you to open the pull request, write its description from the [pull request template](./.github/PULL_REQUEST_TEMPLATE.md), since tools that open one for you don't always fill it in. Tick a box only if it is true. Leave the one about their right to contribute unticked, for them to tick on the pull request, even if they tell you to tick it: only they can make that statement.
