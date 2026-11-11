# Interview fluency for experienced engineers

A reusable preparation kit for people who are capable in their jobs but out of practice at interviews. The goal is to make existing judgment visible under unfamiliar constraints, not treat professional experience as a substitute for practice.

This is a **standalone, anonymized draft toolkit**. It contains no personal story bank, named reviewers, company interview reports, or copied assessment questions. Nothing has been published, and no hiring outcome is guaranteed.

## Start with the problem you actually have

| Need | Guide | Optional agent skill |
| --- | --- | --- |
| Resume undersells impact, is hard to scan, or needs comparison with earlier versions | [Resume](./guides/resume.md) | [resume-coach](./skills/resume-coach/SKILL.md) |
| Rusty in coding screens despite daily engineering work | [Practical technical screens](./guides/technical-screens.md) | [technical-screen-coach](./skills/technical-screen-coach/SKILL.md) |
| Design answers remain high-level or lose structure | [System and frontend design](./guides/system-design.md) | [system-design-coach](./skills/system-design-coach/SKILL.md) |
| Real project depth gets lost in behavioral answers | [Behaviorals](./guides/behaviorals.md) | [behavioral-coach](./skills/behavioral-coach/SKILL.md) |

Use the shared [coaching protocol](./COACHING_PROTOCOL.md) to keep practice honest, evidence-based, and sustainable.

The methods adapt to the actual role and language. Worked technical explanations lean JavaScript/TypeScript and React; the design guide includes a frontend example and backend principles. This is not an exhaustive algorithms curriculum or distributed-systems course.

## A small first week

1. **Inventory, 20 minutes:** list actual interview formats, known constraints, and one specific weakness. Use the [session brief](./templates/session-brief.md).
2. **Technical rep, 30-45 minutes:** one original problem, running code, one review. Record hints and evidence, not just a score.
3. **Design, 30-45 minutes:** one user journey with state/data ownership, a request flow, a failure, and a trade-off.
4. **Behavioral, 20 minutes:** one true story and two probing follow-ups.
5. **Resume, if needed:** revise two high-value bullets from an [evidence ledger](./templates/experience-ledger.md), not the whole career at once.

These are options, not a quota. As an interview approaches, prioritize its verified format and the specific gap that could matter. Do not turn maintenance into permanent cramming.

## Use with an AI assistant

### Start without installing anything

Open a fresh conversation in this folder and choose one prompt. Replace bracketed inputs; unknown details are fine.

| Goal | Opening prompt |
| --- | --- |
| Resume diagnostic | Read `skills/resume-coach/SKILL.md` and follow it for this session. Review `[resume path]` for `[target role]`. Start with a prioritized diagnostic, not a rewrite. I have `[time]`. |
| Technical practice | Read `skills/technical-screen-coach/SKILL.md` and follow it for this session. I want to practice `[format]` in `[language/runtime]` for `[time]`. Use small hints and let me attempt first. |
| Design practice | Read `skills/system-design-coach/SKILL.md` and follow it for this session. I have `[time]` for `[frontend/backend/mixed/project deep-dive]` practice. Clarify the frame before starting. |
| Behavioral refresh | Read `skills/behavioral-coach/SKILL.md` and follow it for this session. Help me rehearse `[prompt or real event]` for `[time]`, with one follow-up at a time. |

If the assistant cannot read local files, paste the complete selected `SKILL.md` and provide only the material needed for the session. Each skill includes its essential rules and a compact record format; guides and templates add depth but are not required.

For a clean local trial, add:

> Use only this toolkit and the documents or facts I provide, not previous conversations, account memories, or sibling folders. Do not edit the toolkit. Ask for a private working location before saving candidate material.

### Optional automatic discovery

Reading a skill file is not the same as registering it. This repository's top-level `skills/` folder is a distribution layout, not a default Copilot discovery path.

For tools that support `.github/skills/`, copy one complete skill folder into the intended practice workspace so the result is `.github/skills/<name>/SKILL.md`. Start a new conversation and check the host's available-skills list. In Copilot CLI, use `/skills` to inspect whether the expected name and source are available; if not, use explicit-file loading and consult that tool's current installation guidance. Other tools may use different discovery paths. Installing or editing global settings is optional, not part of using this kit.

### Keep the work private

- Keep resumes, extracted document text, story banks, reviews, and practice outputs in a separately chosen private location outside this toolkit. Confirm the save path before writing; ignore rules are a backup, not a privacy control.
- For a friend's document, confirm permission to review if not already established and keep factual questions easy to relay. Permission to review is not permission to publish or upload elsewhere.
- Use permitted material; generalize confidential employer code or designs instead of pasting them.
- Ask for explanations or separate references when useful. Record that help as coached work, not an unaided mock.
- Do not use the assistant during an assessment where assistance is prohibited. Preparation permission is not interview permission.

## Templates

- [Session brief](./templates/session-brief.md)
- [Experience/evidence ledger](./templates/experience-ledger.md)
- [STAR card](./templates/star-card.md)
- [Design worksheet](./templates/design-worksheet.md)
- [Practice/debrief record](./templates/practice-record.md)
- [Process inventory CSV](./templates/process-inventory.csv)

The inventory is optional personal tracking, not a scorecard: `furthest_stage` is your consistently defined stage label; `final_stage_reached` records true/false/unknown separately from the outcome. Use `source_type` to distinguish recollection, calendar, or recruiter communication. Keep the filled file private and do not infer missing dates or outcomes.

## Before sharing

Read [PUBLICATION.md](./PUBLICATION.md). Keep this toolkit in its own repository, separate from the private personal handoff and its history. Pick a license deliberately if publishing; none is silently assigned to other people's material. Do not add private employer code, paid problem statements, candidate reports, or identifying anecdotes.

The methods were distilled from a long-running practical coaching workflow, including mistakes and corrections. They are not universal rubrics, quoted reviewer feedback, or a controlled study of AI's effect on job outcomes.
