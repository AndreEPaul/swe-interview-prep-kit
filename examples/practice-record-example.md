# Example: a filled practice record (synthetic)

**Everything below is invented to show the format.** The session did not happen, so don't read it as a benchmark or a target. Use the [blank template](../templates/practice-record.md) for your own sessions, and keep the filled copy in a private folder outside this repository.

- Date / format / timebox: a weekday evening, coached mock of a coding screen, 45 minutes including review.
- Requirement or prompt source: original (written by the coach).
- Starting state: blank.
- Mode: coached practice.
- What I attempted: a search box that waits 300 ms after the last keystroke before requesting results and ignores responses to older queries, in React and TypeScript.
- Help received: hint, once, when the coach asked what `query` held inside the delayed callback. Then explanation, once, when I stalled on stale responses: the coach explained that clearing a timer cannot cancel a request that has already started. No scaffold and no reference.
- If AI-assisted: not applicable.
- What I explained: why the timer and the in-flight request need separate handling, and why the latest-input check has to run when the response arrives, before the state update.
- Actual checks run and outputs: two tests with fake timers, a threshold test (no call at 299 ms, one call at 300 ms) and a stale-response test that delivered the old response while the next timer was still waiting. The threshold test passed first. The stale-response test failed, then passed after the fix. I pasted both outputs to the coach.
- Candidate tests versus infrastructure/reference tests: both tests were mine. There was no reference solution.
- Failure/root cause: a slow response to an earlier query overwrote the newer results, because nothing tied a response to the latest input. My first version only noticed a newer input when its request started, so a response landing during the debounce wait still got through.
- What changed and why: I added a counter that increments on every keystroke, passed it into the request, and compared it before setting state, so only the latest input can update the results.
- Still unverified: updating state after the component unmounts, and the empty-query case, which I assumed instead of asking.
- One next target: write the stale-response test before the implementation.
- Stop/recovery plan: stopped at the agreed 45 minutes. If I am stuck for five minutes, ask for a hint instead of guessing.

The help labels describe what was supplied, not how well it went. A session with an explanation in it is still useful practice, and the record says so plainly.
