# peer-kit

Interview preparation for experienced engineers: practical guides, AI coaching skills, and templates for coding screens, design rounds, behavioral stories, resumes, and rounds that allow an AI assistant.

The "peer" in peer-kit means fellow engineers: it is shared by one experienced engineer with others who want help preparing for interviews.

The coaching skills are plain Markdown instructions that you can paste into any AI chat or install in tools that load skills. Each one asks the assistant to work from what you bring (an attempt, a draft, or your notes), give the smallest useful help, say what help it gave, and never invent details about your experience. The guides and templates are useful without any AI.

Use it alongside whatever already works for you: courses, problem sites, books, official interview guidance, and feedback from other people. It supplements human feedback and doesn't replace it, especially for resume reviews and mock interviews (see the [author's note](#authors-note)). It suits engineers returning to interviews after a long gap, preparing for a particular round, or keeping a light practice habit.

> **Early release.** Corrections and ideas are welcome (see [CONTRIBUTING.md](./CONTRIBUTING.md)), and the [limits](#limits) are real.

## What's inside

- **Guides:** short preparation notes on resumes, coding screens, AI-assisted rounds, design, behavioral stories, and professional presence.
- **Coaching skills:** instructions that make an AI assistant a practice partner for each of those topics except professional presence, plus an optional planner that turns scattered interview details into a short brief.
- **Templates:** blank worksheets for briefs, stories, evidence, design practice, and practice records.
- **A [coaching protocol](./COACHING_PROTOCOL.md):** the ground rules behind every skill, explained in full.

## How the coaching works

In the practice coaches you go first, and the assistant gives the smallest useful help and says what help it gave. It is told not to make up details about your experience, and to decline help in a live assessment that forbids outside help. The [coaching protocol](./COACHING_PROTOCOL.md) explains the ground rules in full.

<details>
<summary>The six ground rules</summary>

- **You go first.** In the practice coaches the assistant plays the interviewer: you restate the task, attempt it, and explain your thinking before it helps. The resume coach and planner review what you bring instead. You can ask for an explanation at any time, and it is simply labeled as help.
- **Smallest useful help, labeled.** Hints come before explanations, and explanations before reference answers. Help is recorded as none, hint, explanation, scaffold, or reference. The labels describe what was supplied. They are not a score.
- **No made-up details.** The coach is told not to invent metrics, quotes, or decisions. Missing facts become visible `[placeholders]` and questions for you. Assistants can still slip, so check what it writes against what really happened.
- **Short starts.** The first reply is useful on its own. It asks at most three questions and says what it will assume for any setup question you skip.
- **Evidence over verdicts.** It reviews the code or draft you actually pasted, says what it couldn't check, and doesn't predict outcomes or rate your readiness.
- **Practice only.** The coach declines to help in a live assessment that forbids outside help. It is told to save nothing unless you ask, and then only to a folder you confirm. What you paste still goes to your AI provider; see [Keep your material private](#keep-your-material-private).

</details>

<details>
<summary>What it looks like: a sample exchange</summary>

An illustrative excerpt, abridged from a test run of [behavioral-coach](./skills/behavioral-coach/SKILL.md) on a made-up story. Results vary by model and run, and this isn't a transcript of real use.

**You:**

> Can you polish this story? The question is "Tell me about a time you disagreed with a coworker." My draft: "On my last team we had to pick a message queue for the new notifications service. A senior engineer wanted Kafka and I wanted SQS because we were already on AWS and the team was small. I pushed back in the design review and eventually we went with SQS. It reduced latency by 40% and everyone was happy. My manager said it was a great call." Also please add some detail about how I convinced them. I don't remember exactly what I said but something persuasive would be good.

**Coach:**

> What works: it's a real technical disagreement with a clear stake. You give your own reasons (already on AWS, small team). […]
>
> Biggest gap: the decision itself. "I pushed back… and eventually we went with SQS" skips how it was resolved, and the senior engineer's side is just a label. As written it reads as "I was right and won", which is where follow-ups will dig.
>
> I can't make up how you convinced them. Anything you don't actually remember doing won't survive a follow-up, and it would be my story, not yours. Exact words don't matter, but a rough account of what you did does. Two questions:
>
> 1. What was the senior engineer's actual case for Kafka?
> 2. Roughly, what did you do between the design review and the final decision (a comparison, numbers, a prototype, a side conversation, something else)?
>
> If nothing comes back, a disagreement you remember better will serve you more than this one. Meanwhile, here is a draft built only from what you've told me. It's coached framing, not your unaided answer, so put it in your own words before you rehearse it:
>
> > On my last team we had to choose a message queue for a new notifications service. A senior engineer wanted Kafka [their reasons]. I wanted SQS because we were already on AWS and the team was small. I pushed back in the design review [what you said or showed]. [How it was resolved and who made the final call.] We went with SQS. [Result: latency reduced by 40%. Say whether measured or estimated, and against what.] My manager said it was a great call. [What you'd do differently, or what you took from it.]
>
> I dropped "everyone was happy" because nobody can check it. I kept your manager's line as praise, not a result. I tagged the 40% because an interviewer will ask what it was measured against, and I can't tell yet.
>
> Help so far: scaffold (I supplied a partial draft; every fact is yours). […]

</details>

## Get started

Whichever way you start, say what you want and the assistant should pick the matching skill. If it doesn't, name one: "use the behavioral-coach skill".

**1. Paste a skill into any chat (no setup).** Open an AI assistant, paste the raw text of one skill's `SKILL.md` (linked in the table below), and put your first message under it. Each skill stands alone, so you don't need the other files.

**2. Open your assistant in a clone.**

```bash
git clone https://github.com/AndreEPaul/peer-kit.git ~/peer-kit
cd ~/peer-kit
```

Assistants that read `AGENTS.md` or `CLAUDE.md` (Copilot CLI and Claude Code do) are told to read this README, pick the matching skill, and save nothing inside the clone. That makes this a good way to try the kit. For your real resume and stories, prefer option 1 or 3 from a private folder, so your privacy doesn't depend on the assistant following that rule.

**3. Register the skills once and use them from any folder.** Clone as above (adjust the paths if you cloned elsewhere), register the skills with your tool, then start your assistant from a private practice folder outside any git repository, so files it saves there stay out of version control. Skills are instructions your assistant will follow, so skim one before you install it. These are short and contain no scripts.

<details>
<summary>Register the skills: Copilot CLI, Claude Code, other tools</summary>

- GitHub Copilot CLI: `copilot skill add ~/peer-kit/skills`, then `copilot skill list` to check. This points at your clone, so `git pull` updates the skills. (Checked with Copilot CLI 1.0.114.)
- Claude Code: `mkdir -p ~/.claude/skills && cp -r ~/peer-kit/skills/* ~/.claude/skills/`. This is a copy that overwrites any skill of the same name, so look at `ls ~/.claude/skills` first, and repeat the copy after `git pull` to update. You can then type `/behavioral-coach` and so on, or just describe what you want. See [Claude Code's skills documentation](https://code.claude.com/docs/en/skills).
- Other tools: the skills use the open [Agent Skills format](https://agentskills.io/specification). Check where your tool loads skills from, and if you can't find out, paste the file instead.

</details>

**If the coach drifts.** In a long chat an assistant can lose track of its instructions. If it hands you answers before you have tried, or fills in details you didn't give, say so plainly (for example, "hint only" or "don't invent that"), or start a fresh chat and paste the skill again.

## Pick a starting point

| If you want to... | Read | Practice with |
| --- | --- | --- |
| Work out where to start, or organize recruiter notes, a job description, and dates into a short brief | No guide | [interview-prep-planner](./skills/interview-prep-planner/SKILL.md) |
| Make your resume show real impact | [Resume](./guides/resume.md) | [resume-coach](./skills/resume-coach/SKILL.md) |
| Get fluent in live coding again | [Practical technical screens](./guides/technical-screens.md) | [technical-screen-coach](./skills/technical-screen-coach/SKILL.md) |
| Prepare for a round that allows an AI assistant | [AI-assisted interviews](./guides/ai-assisted-interviews.md) | [ai-assisted-interview-coach](./skills/ai-assisted-interview-coach/SKILL.md) |
| Give design answers more structure | [System and frontend design](./guides/system-design.md) | [system-design-coach](./skills/system-design-coach/SKILL.md) |
| Tell project stories with real depth | [Behaviorals](./guides/behaviorals.md) | [behavioral-coach](./skills/behavioral-coach/SKILL.md) |
| Keep your public profile clear and consistent | [Professional presence](./guides/professional-presence.md) | No skill yet; start with the guide |

<details>
<summary>Example first messages</summary>

Replace the brackets, and leave out what you don't know:

- **Planner:** "I have a [role] interview loop around [date] and about [time] to prepare. The recruiter sent this: [paste]. Where should I start?"
- **Resume:** "Review this resume for [target role]. Start with a diagnostic, not a rewrite. [paste]"
- **Technical:** "I want a [length] mock coding screen in [language]. Give me a small task and let me attempt it first."
- **AI-assisted:** "My next round allows an AI coding assistant. The rules I was given are [paste, or 'I don't know']. Help me practice."
- **Design:** "Practice a design round with me on [topic]. I have [time]."
- **Behavioral:** "Help me tighten my answer to [question]: [paste]."

</details>

## Templates

Blank, optional worksheets for briefs, stories, evidence, design practice, and practice records, plus a CSV for tracking your interview processes. Fill them in a private folder outside this repository.

<details>
<summary>The templates and filled examples</summary>

- [Session brief](./templates/session-brief.md): what you know about an interview, with sources and dates.
- [Experience ledger](./templates/experience-ledger.md): the facts behind your resume claims, separating what was measured from what was estimated.
- [STAR card](./templates/star-card.md): one real story with its evidence and likely follow-ups.
- [Recall sheet](./templates/recall-sheet.md): a one-page review for the last day or two, built from stories you have already confirmed.
- [Design worksheet](./templates/design-worksheet.md): a plan and review for a design practice session.
- [Practice record](./templates/practice-record.md): what you tried, what help you had, and your next target.
- [Process inventory](./templates/process-inventory.csv): optional tracking of your interview processes, one row each. It is not a scorecard. The [field guide](./templates/process-inventory-fields.md) explains each column.

Filled examples, all synthetic and labeled as such: an [experience ledger](./examples/experience-ledger-example.md) and a [practice record](./examples/practice-record-example.md).

</details>

## References

Practice sites and tools I used or looked at, with my take on each: LeetCode and NeetCode, HackTheRounds, interviewing.io, GreatFrontEnd, Hello Interview, and whiteboarding tools. See [References](./guides/references.md).

## Keep your material private

- Keep resumes, stories, practice records, and plans in a private folder outside any git repository, and confirm the save path before an assistant writes anything. Ignore rules are only a backup. Create the folder, then check it with `git -C ~/prep-notes rev-parse --is-inside-work-tree`: you want "not a git repository", and if it prints `true`, pick another folder. Skip folders that sync to a service you don't want holding your resume.
- Your text goes to whichever AI provider you use. Chat apps may keep history or memory, so check those settings before you paste a real resume or story.
- Use material you are permitted to use. Generalize employer details instead of pasting confidential code, designs, or customer data.
- If you review a friend's resume, get their permission first. That is not permission to upload it anywhere else.
- Never use an assistant during an assessment that prohibits outside help. Permission to prepare is not permission to use help in the interview.
- Assistants make mistakes. Check facts and results, and keep your own voice.

## One possible first week

A light plan for when you don't have an interview date yet: a short inventory, then one rep each for coding, design, and a behavioral story, plus a resume pass if you need it.

<details>
<summary>The five steps</summary>

1. **Inventory, 20 minutes:** list the interview formats you actually face, what you know about them, and one goal or uncertainty. The planner or the session brief can help.
2. **Technical rep, 30 to 45 minutes:** one original task, running code, one review. Record the hints and the evidence, not just a score.
3. **Design, 30 to 45 minutes:** one user journey with state ownership, a request flow, one failure, and one trade-off.
4. **Behavioral, 20 minutes:** one true story and two probing follow-ups.
5. **Resume, if needed:** revise two high-value bullets from an evidence ledger, not the whole career at once.

These are options, not a quota. As an interview approaches, prioritize its verified format and the specific gap that could matter. Don't turn maintenance into permanent cramming. If you have a real date, give it and your available time to the planner so it plans around them instead of this generic week.

</details>

## Limits

- It is not a complete curriculum, a question bank, or a prediction of any company's questions, and it guarantees no offer.
- It doesn't cover classic algorithm drills, take-home projects, or offer negotiation. Worked examples lean toward JavaScript, TypeScript, React, and Python.
- AI assistants make mistakes and behave differently across tools and models. The skills were smoke-tested by giving fresh sessions run through GitHub Copilot CLI only a skill file and made-up candidate messages, then checking each reply against criteria written beforehand. That is not proof they work in every tool or model.
- The Copilot CLI install command was run. The Claude Code steps follow its documentation and haven't been run. The shell commands assume macOS or Linux; on Windows, paste a skill instead or adapt the steps.
- The methods come from one engineer's experience with AI coaching (see the [author's note](#authors-note)), not from a controlled study.

## Author's note

peer-kit is meant to supplement human feedback, not replace it, and that goes especially for resume reviews and mock interviews. I believe the best way to prepare is real interviews, followed by mock interviews with a peer. But people are busy and those sessions are hard to coordinate, so this is for the reps in between. When you can get a person to review your resume or run a mock interview with you, take it.

For what it's worth, here is my own anecdote. I kept a log of my interview processes. Before I started working with an AI interview coach, 3 of 14 (21.4%) reached the final round. Since then, 9 of 17 (52.9%) have. Those coaching sessions are where peer-kit's methods come from, so these figures describe that coaching, not a test of the kit as published. I saw an observable improvement in my own interviewing, and that is why I'm sharing it. It is one person and a small sample, so please read it as an anecdote, not as evidence that it will work for you.

<details>
<summary>How I counted</summary>

- **Data and period:** the interview processes in my own log, spanning a little over a year. None of them straddled the date I started working with the coach, so each one falls in exactly one group.
- **"Reached the final round":** got to the final loop with the hiring team, which is the last interview stage of a process, whether or not an offer followed.
- **Other explanations:** more interviews behind me, which roles and companies I applied to, and the job market could account for some or all of the difference. One process moves a rate by about 6 to 7 points, and with groups this small, a gap like this could also appear by chance alone.

</details>

## Contributing

See [CONTRIBUTING.md](./CONTRIBUTING.md) for what fits, the privacy rules, and how to test a skill change.
