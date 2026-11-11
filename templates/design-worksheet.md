# Design practice worksheet

- Frame: frontend schema/state / backend/distributed / mixed full-stack / real-project deep dive:
- Interview duration / available practice time / agreed stopping point:
- User goal:
- Required behavior and non-goals:
- Important constraints / open questions:
- Estimates that change decisions:
- Important access patterns and, where relevant, storage/indexing/transaction needs:

## Model and ownership

- Entities/IDs:

| Value / entity | Source of truth | Owner / readers / writers | Lifetime / reset | Stored or derived |
| --- | --- | --- | --- | --- |
| Fill deliberately | | | | |

## API / event contracts

| Operation | Input | Output / metadata | Error / permission behavior |
| --- | --- | --- | --- |
| Fill for a required interaction | | | |

## Components and communication

Draw regions/components or use a numbered text flow for a text-only round. Label communication with events/data; do not use unlabeled boxes as a substitute for explanation.

## Interaction trace

Event -> state/navigation -> request -> response relevance -> rendered/stored outcome.

- Normal flow:
- Error or partial-failure flow:
- Pending/obsolete work:
- Important invariant:

## Deep dive and close

- Actual bottleneck:
- Targeted response and its cost:
- UX/accessibility or reliability concern:
- Concrete measurement and action:
- Important test:
- Trade-off and revisit condition:
- Deferred work:
- Help received: none / hint / explanation / scaffold / reference; describe it:
- One next improvement:

For a real-project deep dive, separate actual decisions/results from proposed redesigns. For a short session, narrow the flow but keep a failure, a trade-off, and the close. Keep filled worksheets outside the toolkit and save only when requested to a confirmed private path.
