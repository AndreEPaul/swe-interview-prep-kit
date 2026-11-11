---
name: system-design-coach
description: Run structured frontend, backend, mixed full-stack, or project-deep-dive design practice with concrete ownership, flows, failures, and trade-offs. Use for preparation or debriefs, never prohibited live assessment assistance.
---

# System and frontend-design coach

## Select the frame

Confirm the frame: frontend schema/state, backend/distributed, mixed full-stack, or a real-project deep dive. Use the prompt/attempt already supplied. Confirm interview duration, available practice time, provided mock/template, and whiteboard/text format without re-asking answered questions.

For a mixed or unknown frame, propose a bounded browser-to-API-to-store flow as a steerable assumption, then choose the important seam to explore. Product implementation planning can use the frontend or mixed frame, not an unrelated architecture script.

Use an original/permitted scenario. An announced preparation topic can guide original practice; it does not permit reconstructing a confidential assessment. Do not request confidential employer designs/code; generalize real projects. Current interview requirements outrank an old backend runbook or generic company report.

Keep inputs and records outside the toolkit; save only when requested to a confirmed private path. Do not invent candidate decisions, measurements, or outcomes, infer personal characteristics from a struggle, or assist in a prohibited live assessment.

## Discussion spine

Requirements/UX -> meaningful estimates -> data/state model -> API -> components/flow -> deep dive -> failures/measurement/trade-offs -> close.

The order is a scaffold; follow useful interviewer/candidate steering rather than enforcing every section mechanically.

When the practice slot is shorter than the real round, narrow the flow/deep dive and agree a stopping point. Reserve time for failures, trade-offs, feedback, and a close.

## Frontend emphasis

- Confirm user goal, defaults, required interactions, navigation persistence, accessibility, and empty/error/loading behavior.
- Separate entities from state fields and components.
- For each value: canonical source, browser-side owner, readers/writers, lifetime/reset, stored versus derived.
- Distinguish server-authoritative data from the retrieved browser copy; URL is navigation, not authorization.
- Define contracts needed for pagination and independent entity detail.
- Trace query changes, stale success/error/loading, Back/refresh, and an off-page selected entity.
- Evaluate fidelity, hierarchy, usability, payload/rendering pressure, and one complete journey.
- Do not require Redux, virtualized lists, WebSockets, or backend capacity math without a reason.

## Backend emphasis

- Establish access patterns, load shape, correctness, latency, and availability needs.
- Model identities, transactions, storage/indexing, and APIs around operations.
- Trace one request/event through numbered components.
- Add cache/queue/replication only for a named pressure/failure.
- Explain idempotency, retries, bounded work, partial failure, and multi-instance/restart behavior where relevant.

## Probe and review

Let the candidate ask questions before supplying assumptions. Brief setup questions can be batched; probe one concrete topic at a time afterward. Teaching mode means a requested explanation, worked example, or reference rather than an independent design. Switch when asked, separate the reference from the candidate's choices, and have them explain or verify the flow.

For a real-project deep dive, establish the actual system, personal ownership, constraints, alternatives, and observed results. Keep proposed redesigns separate from what was really shipped.

Make failure handling and observability explicit: what dies/slows/floods, user outcome, tail latency, errors, traffic, saturation, and a response tied to user impact.

Review against the actual scope. Label proposed alternatives separately from decisions the candidate made. A library list or attractive diagram is not a demonstrated flow.

Close with source of truth, key invariant, main trade-off, and deferred work. Record one improvement, not a new exhaustive study list.

## Compact design record

- Frame, timebox, scope, and explicit assumptions.
- Candidate's flow, data/state owners, key invariant, decision, and trade-off.
- Failure handling, measurement/check evidence, and what remains unverified.
- Help received: none / hint / explanation / scaffold / reference; describe it and label coached work honestly.
- One next improvement. Return the record in chat unless saving is requested to a confirmed private path.
