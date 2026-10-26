# ADR 0008: Retrieval uses a local embedding model, and the language model of stage two runs on the author's machine

Status: proposed, 2026-09-30

## Context

Stage one has to find, for each new patient message, the most similar of the 22,694 patient turns in the index. A language model cannot do that pass: the index holds 275,712 words of patient turns and 815,789 words of replies, far past the context of the models that run on a laptop, and reading it once per message would cost seconds and money on every question. An embedding model turns each text into a vector once, and the search becomes one product of vectors per query. A language model is worth its cost on a short list, to rerank the top 20 or 50 or to write the reply from the top five.

Stage two (ADR 0002) sends the patient message and the five retrieved clinic replies to a language model. The text is scrubbed (ADR 0003), but the scrubbing has measured holes: one patient name reached an index reply, and 378 profile words are kept as ordinary language. The data is health data, a sensitive category under article 11 of the LGPD. A company that sends it to a commercial API does so with a data processing agreement, zero data retention, a legal basis given by the clinic as controller, and, when the provider is abroad, the standard clauses of ANPD Resolution 19/2024. None of those contracts exists for this repository.

## Decision

1. Stage one embeds with `intfloat/multilingual-e5-small` (384 dimensions, about 118 million parameters, Portuguese in its training data), on the author's machine. Both sides get the prefix "query: ", because the search compares a patient turn with patient turns. Vectors are normalized, so cosine similarity is a dot product. It is row 5 of the results table, chosen before any measurement, and the only model measured on August without a July choice. A second model is chosen on July (ADR 0007).
2. Stage two runs an open model of 7 to 8 billion parameters on the author's machine through Ollama, quantized to 4 bits (about 5 GB in 24 GB of memory). The first candidate is Qwen3 8B. No real text leaves the machine.
3. A commercial API is called only on the synthetic sample of ADR 0003, for the public demo, never on the real corpus.

## Alternatives considered

A commercial API on the scrubbed text was rejected for the reasons in the context: the scrubbing has holes and the contracts do not exist. It is the route a clinic in production would take, with those contracts signed. A language model for the first pass was rejected for size and cost. A larger embedding model (`multilingual-e5-base` or `-large`) and BM25 stay as candidates for the July choice.

## Consequences

The cost per 1,000 queries of both stages is machine time, measured on an Apple M5 with 24 GB, and the README reports it as such. An 8 billion parameter model writes worse than a frontier model, and the 100-case judgment of stage two shows by how much. The code calls the language model through one function, so the switch to an API in production changes one file.
