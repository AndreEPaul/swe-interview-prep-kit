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
- Anything that helps someone during a live assessment that forbids outside help.
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
- The first reply should deliver something useful before asking anything, and then ask at most three questions, each with a stated default.
- Never save the candidate's material without a location they confirm that is outside any git repository, and never help with a live assessment.

## Checks

```bash
python3 tools/check.py
python3 -m unittest discover -s tools -v
```

The checker needs Python 3.9 or newer and no packages. If PyYAML is installed it parses skill frontmatter with it. It checks Markdown links and anchors, backticked repository paths, that every guide, skill, and template is reachable from the README, skill frontmatter and standalone-ness, CSV shape, forbidden file types, and privacy patterns such as email addresses, home-directory paths, and secrets. CI runs both commands on every pull request.

To also catch names that must never appear, put one term per line in a file outside this repository: employers, colleagues, interviewers, product names. A line starting with `re:` is a regular expression, and `#` starts a comment. Then run:

```bash
python3 tools/check.py --deny-list ~/peer-kit-deny.txt
```

You can set `PEER_KIT_DENY_LIST` instead of passing the flag. Matches are reported by line number only, so the output never prints the term.

## Testing a skill change

Static checks cannot tell you whether a coach behaves well. For any change to a skill's behavior:

1. **Write down what a good reply looks like before you read one.** For example: at most three questions, no invented facts, the candidate attempts first, help is labeled, nothing is saved.
2. **Test cold.** In a fresh session, give an assistant only the skill file and a synthetic candidate message, and ask it to reply and then report what was unclear:

   > Read only this file: `<path to SKILL.md>`. Act as the assistant it describes and answer the candidate message below in plain chat. Then add READER NOTES: what you were not given, what was unclear or contradictory, what you would cut, and what would break in a different AI tool.

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
