# Design practice worksheet

- Format: frontend / backend / project deep dive:
- User goal:
- Required behavior and non-goals:
- Important constraints / open questions:
- Estimates that change decisions:

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

Draw regions/components. Label arrows with events/data; do not use unlabeled boxes as a substitute for explanation.

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
