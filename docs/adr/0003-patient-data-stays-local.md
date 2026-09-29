# ADR 0003: Patient data never leaves the machine

Status: accepted, 2026-09-24

## Context

The corpus holds names, phone numbers and health-related messages from real patients of one clinic, and Brazilian data protection law (LGPD) applies to it.

## Decision

The raw export stays on the author's machine, outside the repository. The pipeline has a step that removes names, phone numbers, document numbers and e-mail addresses before any message is embedded or logged, and that step has tests. The repository ships a synthetic sample with the same schema, so the code runs end to end for a reader.

## Alternatives considered

Publishing anonymized real messages was rejected, because free text can still identify a person. Shipping no sample was rejected because it would leave a repository that nobody can run.

## Consequences

The README number comes from the real data, and the reader reproduces the pipeline on the sample. The logs never store the raw text of a message.
