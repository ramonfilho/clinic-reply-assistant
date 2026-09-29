# ADR 0004: The evaluation exists before the retrieval code

Status: accepted, 2026-09-24

## Context

The study of hiring practices done on 2026-09-18 found that take-home reviewers treat a missing evaluation as a red flag. The Spotter take-home delivered on 2026-09-22 was built the same way, with a chronological holdout defined before any model.

## Decision

The first code in the repository builds the evaluation set. A cutoff date splits the conversations, the ones after it form the held-out set, and the metric of ADR 0002 is computed by one script that every later change has to run. The retrieval code comes after.

## Alternatives considered

Building the retrieval first and evaluating at the end was rejected because the metric then bends to fit the system.

## Consequences

Every retrieval decision, such as the embedding model or the value of k, becomes a row in the same results table, like the model table of the Spotter take-home. Cost per thousand queries and latency per query are logged next to the metric.
