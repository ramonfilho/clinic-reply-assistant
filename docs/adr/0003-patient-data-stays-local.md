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

## Amendment, 2026-09-24

The first build of the evaluation set fixed what the step replaces: e-mails (a comma in place of a dot included), Instagram handles, CPFs with separators, dates with a year, Brazilian phone numbers, any other run of 8 or more digits (a bare CPF, a foreign phone), and names. The names come from the export itself: the words of the patients' profile names and the attendants' names. Profile names hold ordinary words ("clinica", "olhos", "prazer"), so a profile word counts as a name only when it appears in at most 0.5% of the messages and is written with a capital letter in at least half of its appearances in the middle of a sentence. On the real export this keeps 5,022 words as names and leaves 378 as language. A name that is not in any profile goes through, and the README says so.
