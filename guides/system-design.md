# Design interviews: choose the right frame

Begin by identifying the frame: frontend schema/state, backend/distributed, mixed full-stack, or a real-project deep dive. Product implementation planning can use the frontend or mixed frame. A familiar runbook is a scaffold, not permission to answer a different question.

For a mixed or unknown frame, propose a bounded browser-to-API-to-store flow as an assumption the candidate can steer, then choose the important seam to explore. For a real-project deep dive, establish the actual system, personal ownership, constraints, decisions, alternatives, and outcomes; keep proposed redesigns separate from what was really shipped.

This guide provides a worked frontend example and backend principles, not a comprehensive distributed-systems course. Use original or permitted practice, including original exercises on an announced preparation topic; do not reconstruct confidential assessments or request employer-internal designs/code. Keep candidate material and requested records outside the toolkit in a confirmed private location.

## Shared spine

**Requirements -> meaningful estimates -> data/state model -> API -> components/flow -> deep dive -> failures/measurement/trade-offs -> close.**

Use the interviewer's order if provided. Check in, but do not wait to be led through every step.

If the practice slot is shorter than the real round, agree a smaller flow/deep dive and a stopping point. Keep time for failure handling, a trade-off, feedback, and the close. A requested explanation or reference is teaching mode: distinguish it from the candidate's independent choices and record the actual help, not an unaided score.

## What changes by format

| Beat | Backend/distributed emphasis | Frontend schema/state emphasis |
| --- | --- | --- |
| Requirements | Operations, correctness, availability, latency, load shape | User job, mock behavior, navigation, loading/error/empty states, accessibility |
| Estimates | Throughput, storage, bandwidth, fan-out where relevant | Dataset versus loaded/rendered rows, payload size, request frequency, acceptable freshness |
| Model | Entities, keys, transactions, indexes, consistency | Entities plus local/navigation/server/derived state, owner, lifetime, reset |
| API | Operations, contracts, auth/error semantics | Parameters and metadata needed by interactions, pagination and independent detail resolution |
| Components | Services/stores/queues only where justified | UI regions, state coordination, data down/events up |
| Deep dive | Bottleneck, partition, delivery, concurrency | Query changes, navigation, stale responses, detail selection, mutation reconciliation |
| Close | Failure modes, scaling lever, SLO/metrics, trade-off | UX fidelity, performance pressure, failure isolation, tests, observable user outcome |

Do arithmetic where a number changes a decision, not to fill time. Do not invent global product scale for a local screen-design prompt.

## Frontend worked skeleton: support-request dashboard

**Original illustrative scenario:** staff search/filter a large queue, load a page of 25 summaries, and open a detail panel. Links should restore the view.

1. **Clarify:** default order/status, read-only versus editable, what survives refresh/Back, required keyboard behavior, and whether exact counts matter.
2. **Estimate:** thousands of records are not thousands of DOM rows. Detail-body size determines whether list payloads should include full text.
3. **State inventory:**
   - Draft search: local interaction state.
   - Applied query/filter/sort/page: canonical navigation representation.
   - Rows/metadata: a browser copy of server-authoritative data.
   - Selected ID: navigation, independent of whether the entity is in this page.
   - List/detail loading and errors: separate relevant-request lifecycles.
   - Previous enabled: derive from page rather than storing a duplicate boolean.
4. **API:** list parameters, stable ordering/ties, IDs, pagination availability, detail lookup by ID, and meaningful unavailable/error handling.
5. **Components:** page coordinator, search/filter controls, result table, paginator, and detail region. Explain who changes each value before selecting a store library.
6. **Flow:** committing a new query resets page as appropriate, changes navigation, starts retrieval, and accepts only relevant results/errors/cleanup.
7. **Deep link:** detail outside the loaded page resolves independently; absence from 25 rows is not evidence the entity does not exist.
8. **Trade-off:** full detail in the page saves opening latency but increases payload; lazy detail needs its own loading/error UX. Test actual sizes and usage.

Skeleton versus retained old rows is a deliberate user-feedback choice. Explain it. Hover-only access is not a substitute for click/keyboard activation and focus behavior.

## Backend principles to make concrete

- Classify read/write shape and identify the actual pressure before adding machinery.
- A queue decouples work only if consumers, status, retry/failure policy, and backlog limits are explained.
- Retries need bounded attempts, backoff/jitter where appropriate, and idempotent effects. A unique key by itself does not make a multi-step database workflow atomic.
- In-memory locks/cache do not persist across restarts or automatically coordinate instances.
- Use storage around access patterns and transaction/consistency needs. SQL versus NoSQL is not a slogan or merely how "relational" the data feels.
- Distinguish replication, durability, backups, consistency, and availability instead of equating every technology with a fixed CAP label.

## Deliberate closing pass

For a critical component, ask:

- What if it dies, slows, or is flooded?
- What does the user observe?
- What is the single point of failure, and what reliability target justifies redundancy/failover?
- What work is bounded, retried, rejected, or degraded safely?
- How would we know?

Name concrete signals:

- **Latency:** tail percentiles for the important path; trace dependency/application time.
- **Errors:** distinguish expected invalid input from unexpected failures.
- **Traffic:** request/event rate, active users/connections as relevant.
- **Saturation:** queue depth/age, CPU/memory, or connection-pool pressure.

Do not add an identical monitoring paragraph to every system. Connect the measure to user impact, a target, and an actionable response. Correlate duplicate dependency symptoms without hiding independent user-facing failures.

## Whiteboard delivery

Use three readable zones: scope/questions, model/contracts, components/numbered flow. Label arrows with events/data. A state table and an interaction trace often communicate more than many boxes. For a text-only round, use headings, tables, and numbered flows instead of requiring a diagram.

Walk between the UX mock and the relevant model/component. Keep a small deferred list. Do not spend the round decorating the board or transcribing an essay.

## Finish in 30 seconds

Summarize the source of truth, request/data flow, main invariant, failure policy, trade-off, and what would make you revisit it. "Use a cache and a global store" is not a design explanation.

Use the [design worksheet](../templates/design-worksheet.md) for a practice attempt. After review, choose one weak transition to refine rather than repeat a full mock immediately.
