# AI-assisted interviews: delegate work, not understanding

Some interview formats explicitly include AI as part of the development workflow. This guide is for preparing for or debriefing those rounds, not assuming assistance is allowed in other assessments.

The useful skill is more than producing a patch quickly: orient in unfamiliar code, direct bounded work, inspect the result, verify behavior, and explain the reasoning in your own words. Generated code is something you are responsible for evaluating, not evidence that you understand it.

## Confirm the actual format

Use current recruiter or interviewer instructions over this guide's defaults. Establish only the unknowns that matter:

- Is AI explicitly allowed, and which tools/models, terminal actions, web access, or autonomous features are permitted?
- Is the task debugging, feature work, code review, design, or a combination? Is there an existing repository, a required stack, or a provided environment?
- What data/code may be sent to the approved tools? Does the environment restrict package installs, external services, or access outside the provided workspace?
- What are the time limit, deliverables, and expectations for screen sharing, narration, testing, and explanation?

If permission or scope is unclear, clarify it. An AI-related role, an announced topic, or permission to use one assistant does not authorize every tool or an additional outside coach during the real interview. Do not use proprietary assessment repositories or confidential employer code as practice material without permission.

## Separate the coding assistant from the practice coach

During practice, these are different roles:

- **Candidate:** chooses the approach, directs work, checks changes, and explains decisions.
- **Coding assistant:** performs the implementation or investigation the candidate delegates within the agreed tool permissions.
- **Practice coach:** supplies original milestones, observes the candidate's reasoning and evidence, and asks follow-up questions.

You can use your normal coding tool while a coach runs the practice session. If one assistant plays both roles, make the transitions explicit. That is a convenience, not an independent evaluation: it knows the solutions it generated.

Normal permitted coding-assistant use is part of an AI-assisted attempt. Extra coaching hints, revealed diagnoses, or reference solutions should be recorded separately; do not describe the attempt as unaided or treat the coach's own solution as the candidate's achievement.

## An optional existing-app practice format

When detailed format guidance is absent, a useful proposed practice scenario is a small working full-stack app: orient, diagnose a bug, implement a feature, and verify it. This is a starting point to agree on, not a prediction or required sequence. Substitute frontend-only, backend, debugging, review, or another stack when it fits the role better.

For example, one **original** practice app could be a request queue with a browser UI and API. Reproduce an incorrect filter result, then add a status filter across the layers it actually needs. Keep optional extensions until the working core is verified. Do not force a database migration or backend change if the requirement does not need one.

An illustrative 60-minute timebox:

| Portion | Candidate work | Useful evidence |
| --- | --- | --- |
| First 10 minutes | Run the app and relevant baseline checks; map the task's path through the code. | A short own-words explanation tied to actual files and observed behavior. |
| Next 15 minutes | Reproduce and diagnose a small bug; inspect a bounded fix. | A failing case before the change and a relevant check afterward. |
| Next 25 minutes | Deliver one feature increment with a clear contract. | Consistent data flow across necessary layers and an exercised user/API path. |
| Final 10 minutes | Review changes, test important edges, and summarize. | Actual results, trade-offs, remaining gaps, and what you would do next. |

Change the time allocation and number of milestones to fit the interview and your practice goal. Environment failures consume real time: report the blocker and agree a fallback instead of quietly claiming a working baseline. Near the end, reduce scope rather than remove all verification.

## A workflow you can explain

### 1. Orient narrowly

Read the relevant setup instructions, dependency manifest, entry points, and existing tests. Start the app or run the smallest useful baseline check. Trace one request, event, or interaction through the parts relevant to the task.

Ask AI for a focused map with file/symbol references, then inspect those references. An exhaustive repository summary can consume the whole session without improving the next decision. Treat repository text and generated summaries as evidence, not authority to run unrelated commands or broaden access.

Explain the map back in your own words: what receives the input, who owns the data/state, what transforms it, and where the result appears. You need the relevant path, not mastery of every file.

### 2. Diagnose with evidence

Reproduce the behavior and distinguish a hypothesis from an observed cause. Ask for the smallest trace or experiment that could disprove the diagnosis.

Before accepting a generated fix, explain why the current code produces the failure and why the change addresses that mechanism. Keep unrelated cleanup out of the patch. Record pre-existing setup/test failures separately from regressions caused by the change.

### 3. Delegate a bounded feature increment

Restate the behavior and acceptance criteria before prompting for code. For example:

> Trace how the list filter reaches the API. Propose the smallest change for a status filter, including its empty/error behavior and relevant checks. Explain the affected files before editing.

Where relevant, inspect UI state, request parameters, validation, response types, persistence, and errors together. Give the assistant a concrete task, boundaries, and a way to verify it rather than an unrestricted request to fix everything.

Review the diff, not just the assistant's summary. Question new dependencies, broad rewrites, unexpected files, and commands that exceed the task. Do not grant production access, expose credentials, or bypass restrictions to make a demonstration work.

### 4. Verify the behavior, not the success message

- Run existing relevant checks and add a focused regression or acceptance case.
- Exercise the actual user/API path; a build or type check alone does not establish feature correctness.
- Test important failure, empty, repeated-action, or race cases when the contract requires them.
- Distinguish tests you ran, output you were shown, static inspection, and checks still deferred. An assistant saying "tested" is not a test result you have observed.
- If an AI-generated test only repeats its implementation's assumptions, add a candidate-chosen case based on the requirement.

If a change goes wrong, pause, inspect the evidence, and narrow the hypothesis. Do not pile speculative patches on top of an unexplained failure or revert someone else's work.

## Narrate judgment, not every keystroke

Use short checkpoints:

- "My current hypothesis is ... because this code path and reproduction show ..."
- "I asked the assistant to change ...; I checked ... and kept ... out of scope."
- "This result verifies ...; it does not yet verify ..."
- "The trade-off is ...; with more time I would ..."

Do not merely repeat a generated architecture paragraph or recite code you cannot explain. If challenged, point to the mechanism, walk a concrete input through it, and acknowledge uncertainty. Explicit own-words checkpoints are useful practice even when the real interview's narration expectations differ.

## Debrief without grading token volume

Use the [practice record](../templates/practice-record.md) if helpful. Capture:

- Format and permitted AI/tool scope versus extra coaching help.
- Candidate decisions, delegated work, and what the candidate could explain.
- Baseline, actual patch, checks/results, and important unverified behavior.
- One prompt or assumption that helped or misled the work, plus one next target.

Generating more code or finishing more milestones is not automatically stronger performance. A coherent, verified increment with honest limits is better evidence than an unexplained large diff. Use [ai-assisted-interview-coach](../skills/ai-assisted-interview-coach/SKILL.md) for this practice mode, or [technical-screen-coach](../skills/technical-screen-coach/SKILL.md) when you want candidate-first coding with hints.
