# Example: a filled experience ledger (synthetic)

**Everything below is invented to show the format.** The projects, numbers, and people are not real, so don't copy the wording into your own materials. Use the [blank template](../templates/experience-ledger.md) for your own claims, and keep the filled copy in a private folder outside this repository.

The template is a wide table. This example lays the same fields out as rows so it is easier to read.

## Entry 1: a measured result with a mismatch

| Field | Entry |
| --- | --- |
| Project / event | Search page rewrite in an internal support tool |
| Claim as written | "Rewrote the search page, cutting load time by 60%." |
| User problem | Support staff waited several seconds for each search and often ran it again. |
| My role | I designed and wrote the client-side fetching and caching. A teammate owned the API changes. |
| Actual decision/action | Replaced a request on every keystroke with a debounced request that ignores stale responses, and cached recent queries. I also considered server-side pagination alone, and rejected it because the API team could not change that endpoint that quarter. |
| Outcome | Median page load went from 2.4 s to 1.1 s on the team's performance dashboard, comparing the two weeks before and after release. |
| Evidence / scope / open question | A dashboard screenshot is saved privately. The claim says 60%, but 2.4 s to 1.1 s is about a 54% cut. Open question: which figure do I state? |
| Measured / estimated / planned / unknown | Measured (median, two-week windows). Source: externally corroborated by the dashboard. |

- What colleagues owned: the API changes (a teammate) and the dashboard instrumentation (the platform team).
- Metric baseline/population/time period: median page load across all searches, two weeks before and two weeks after release.
- What I can explain under technical follow-up: how the stale-response check works, why the cache key includes the filters as well as the query, and what the user sees on an error.
- Claim still needing verification: the 60%. Use the dashboard figure.

## Entry 2: a figure with no source yet

| Field | Entry |
| --- | --- |
| Project / event | Automating a weekly report |
| Claim as written | "Saved the team 10 hours a week." |
| User problem | The report was assembled by hand in a spreadsheet every Monday. |
| My role | I wrote the job. The product manager asked for it. |
| Actual decision/action | Replaced the spreadsheet steps with a scheduled script that emails the report. |
| Outcome | The manual assembly stopped. |
| Evidence / scope / open question | The 10 hours is my recollection, with no timesheet or ticket behind it. Open questions: how long did one Monday really take, and how many people did it? |
| Measured / estimated / planned / unknown | Estimated. Source: candidate-reported. Not safe to state as fact yet. |

A resume bullet drafted from this entry keeps the gap visible instead of filling it: "Automated a weekly manual report with a scheduled job, ending the Monday spreadsheet assembly [time saved: add only if I can establish it]."

## What the ledger caught

- A claim that did not match its own evidence (60% against about 54%), found before an interviewer asked.
- An estimate that was about to be stated as a fact. It stays an estimate until it has a source.
- What colleagues owned, written down, so each bullet says what I did and not what the team did.
