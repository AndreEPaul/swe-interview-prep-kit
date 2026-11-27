# Example: a filled interview debrief (synthetic)

**Everything below is invented to show the format.** The interview did not happen, so don't read it as a typical round, a benchmark, or a target. Use the [blank template](../templates/interview-debrief.md) for your own, and keep the filled copy in a private folder outside this repository.

- Date / round and format / length: written the evening of the interview, a 60-minute system design round, the second round of a loop.
- Rules I was given, and where each came from: a shared whiteboard, no running code, and no AI assistant (written, in the scheduling email). I could ask clarifying questions at any point (told to me, at the start).
- What I was asked, in my own words: design a service that sends reminders by email and push, with retries.
- What I did, and how I spent the time: about 15 minutes on requirements and an API sketch, 20 on the main flow, then failure handling. I ran out of time before monitoring.
- Where I got stuck, and what I did about it: preventing duplicate reminders after a retry. I said I wasn't sure, proposed an idempotency key, and couldn't say what happens when the key store is down.
- What the interviewer probed, pushed on, or said: retries twice and the key store once. Paraphrase of one question: what does the user see if the push provider is down for an hour?
- What went well: I stated my assumptions out loud, and the interviewer kept building on my flow instead of asking me to start over.
- What surprised me: failure handling came up around minute 30, much earlier than I had planned for.
- What I know versus what I infer: I know I ran out of time and stalled on the key store. I infer, without knowing, that failure handling mattered most to them. I can't tell how the round was judged.
- Feedback I was given, and who gave it: none yet.
- What happens next, as I was told, and what I still need to ask: the recruiter said to expect an update within a week (told to me). To ask: whether the next round is another design round, and what its rules are.
- Outcome: pending, as of the date of this note.
- Patterns across my debriefs so far, if any: the coding screen earlier in this loop also ran out of time on its last step. Two rounds is a guess to test, not a diagnosis.
- Records to update: the process row (furthest stage, outcome pending with an as-of date) and my practice record.
- One next target: redo the failure-handling part of a new, original design prompt, starting it at minute 20 of a 35-minute timebox.

The note keeps what happened apart from what I infer, and a pending outcome stays pending.
