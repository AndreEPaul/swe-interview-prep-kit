# Contributing to peer-kit

peer-kit is a small toolkit of guides, AI coaching skills, and templates for experienced engineers preparing for interviews. The most useful contributions keep it accurate, private by default, and usable without any other setup.

## What fits

Welcome:

- Corrections: wrong or outdated claims, broken links, unclear wording.
- Changes to a guide or skill, ideally backed by a real case where the current text misled a reader or an assistant.
- Original, synthetic examples, clearly labeled as synthetic.
- Coverage for formats the kit does not handle yet (see the limits in the [README](./README.md)). For anything larger than a guide section, open an issue first.

Out of scope:

- Question banks, or "real questions asked at company X".
- Anything that helps someone during a live assessment whose rules forbid outside help.
- Promises of outcomes. No guaranteed offers, and no causal claims from personal experience.

## Privacy rules

This repository is public, so nothing in it can be private. Never include:

- Employer code, configuration, internal designs, or customer and internal identifiers.
- Assessment questions, paid-source text or screenshots, or other people's copyrighted material.
- Real resumes, story banks, practice records, offer letters, compensation figures, or private messages.
- Names of interviewers, recruiters, colleagues, or candidates, and links into a private workspace.
- Quotes you have not verified and have permission to use.

Keep real inputs, extracted text, and filled templates in a private folder outside this repository. Ignore rules are only a backup: read the exact diff before you push.

## Skills must stand alone

Each folder under `skills/` has to work when it is copied on its own or pasted into a chat.

- No links to, or references to, other files in this repository: not guides, templates, or other skills. Mention a sibling skill by name and say what to do if it is not installed.
- Define everything the skill relies on inside the skill, such as the help labels and the practice-record format.
- Follow the open [Agent Skills format](https://agentskills.io/specification): `name` matches the folder name (lowercase letters, digits, single hyphens, at most 64 characters), and `description` is at most 1024 characters and says both what the skill does and when to use it. The checker is a little stricter than the spec: it rejects angle brackets in descriptions, which some tools' validators do, and caps `SKILL.md` at 500 lines, the length the spec recommends.
- The first reply should deliver something useful before asking anything, and then ask at most three questions. For a setup choice, state the default you will assume. For a fact only the candidate knows, leave it unknown instead of guessing.
- Never save the candidate's material without a location they confirm that is outside any git repository. Decline to help with a live assessment whose rules forbid outside help, and offer practice or a debrief afterward.

## Checks

```bash
python3 tools/check.py
python3 -m unittest discover -s tools -v
npx markdownlint-cli2 "**/*.md"
```

The last command needs Node.js. It enforces ordinary Markdown style (heading levels, list markers, a language on every code fence) with the settings in `.markdownlint-cli2.yaml`. Line length is deliberately not limited, because each paragraph is one line.

The checker needs Python 3.9 or newer and no packages. If PyYAML is installed it parses skill frontmatter with it. It checks Markdown links and anchors (file names must match their exact capitalization, as on Linux), backticked repository paths, that every guide, skill, and template is reachable from the README, skill frontmatter and standalone-ness, CSV shape, line endings, forbidden file types (documents, archives, keys, images, recordings, transcripts, and mail or calendar exports, any of which can hold private details), and privacy patterns in every text file: email addresses, phone numbers, home-directory paths, secrets, and links that point at a person, a meeting, a private workspace, or a hiring or assessment system. A fictional 555 number or a placeholder such as `your-name` passes. CI runs all three commands on every pull request.

To also catch names that must never appear, put one term per line in a file outside this repository: employers, colleagues, interviewers, product names. A line starting with `re:` is a regular expression, and `#` at the start of a line or after whitespace starts a comment. Terms match case-insensitively as whole words within a single line, so a term wrapped across two lines is missed. Then run:

```bash
python3 tools/check.py --deny-list ~/peer-kit-deny.txt
```

You can set `PEER_KIT_DENY_LIST` instead of passing the flag. A match is reported by file and line number, not by the matched text. A file path that itself contains a term is still printed. The last line says how many terms were loaded.

The checker's link patterns and their tests name some services. If a term is also one of those names, it matches inside `tools/` too, so narrow it with a `re:` line that skips those lines.

Those checks read the files as they are now. A leak that was added in one commit and removed in the next is gone from the files but still in the history, and it is published with the first push. Check the commits as well:

```bash
python3 tools/check.py --history HEAD --deny-list ~/peer-kit-deny.txt
python3 tools/check.py --history origin/main..HEAD --deny-list ~/peer-kit-deny.txt
```

The first command audits every commit, which is worth doing once before the repository is first published. The second checks only the commits that are not on `origin/main` yet. The range can be anything `git log` accepts. With `--history`, the commits are checked instead of the working tree: each commit's message, added lines, and added file paths get the same rules as above, and deleting a forbidden file is not reported. A merge commit is checked by its message only, because its changes were checked in the commits it merged. Binary files are checked by name only. Commit identities are public by design, so only author and committer email addresses are checked, and only against the deny-list, which catches a commit made by mistake under an employer's address when that employer is on the list. Each problem starts with the short commit hash. Fixing one means rewriting history, so do it before you push.

CI runs the checker over the files on every pull request and over the pull request's commits too (the `commits` job). It cannot see your deny-list, and it runs only after a push, when a leak is already on GitHub. So the deny-list and the history check are worth running before you push. To have git do both for you, turn on the pre-push hook once per clone, and set the deny-list path in your shell profile:

```bash
git config core.hooksPath .githooks
export PEER_KIT_DENY_LIST=~/peer-kit-deny.txt
```

The hook checks exactly the commits being pushed (for a new branch, the commits no remote-tracking branch has yet) and refuses the push if the checker finds a problem or cannot run. It is off until you enable it, git then ignores hooks in `.git/hooks` for this clone, and `git push --no-verify` skips it once.

## Testing a skill change

Static checks cannot tell you whether a coach behaves well. For any change to a skill's behavior:

1. **Write down what a good reply looks like before you read one.** For example: at most three questions, no invented facts, the candidate attempts first, help is labeled, nothing is saved.
2. **Test cold.** In a fresh session, give an assistant only the skill file and a synthetic candidate message, and ask it to reply and then report what was unclear:

   > Use only the skill text below (or the attached SKILL.md). Act as the assistant it describes and answer the candidate message below in plain chat. Then add READER NOTES: what you were not given, what was unclear or contradictory, what you would cut, and what would break in a different AI tool.

3. **Include a trap.** Examples: vague resume bullets with a request for numbers, a story with an unsupported claim, a pasted bug that has a tempting full fix.
4. **Retest with a different message.** If your test message ends up as an example in the skill, the skill will pass by echoing it.
5. **Sort the failures.** Wording in the skill and gaps in setup docs are worth fixing. A one-off model slip is not: run it again before you change any text.

Say in your pull request what you ran and what changed.

## Style

- Candidate first: the person attempts, the coach gives the smallest useful help, and help is labeled so a practice record stays honest.
- Evidence over scores. Do not invent ratings, percentages, or readiness verdicts.
- Claim only what you verified. Tool behavior changes, so cite the documentation and the version or date you checked. Run any code snippet before you commit it.
- Label synthetic examples. Do not present an invented resume bullet or story as someone's real result.
- If you cite progression statistics, give raw counts, the period, stage definitions, how the data was collected, and alternative explanations. Do not call a change significant without an appropriate analysis.
- Write plainly, and define jargon where it first appears.
