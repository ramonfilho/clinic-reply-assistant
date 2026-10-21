# ADR 0002: Each client is evaluated on its own cases, from its history when it has one and from a cold start when it does not

Status: accepted, 2026-10-20

Origin: this ADR is maintained with the product base and mirrored into this repository on 2026-10-21. The repository copy is updated from that origin.

## Context

ADRs 0004, 0006 and 0007 of the clinic repository built the evaluation from the history of the first client: cases split by date, four baselines before any model, and a judge separate from the retriever, with its threshold set on 80 cases the author labeled by hand. The aesthetic clinic has 13,583 conversations of history (ADR 0001 of the clinic repository), and the author's hand judgments on them are the reference for the automatic judge. A new client of the base (ADR 0001) may have no conversation history at all, and then there is nothing to split by date.

## Decision

1. Every client has its own test cases and its own results table, and no method reaches a client before its row exists in that table.
2. A client with history keeps the method of ADRs 0004 to 0007 of the clinic repository. Cases come from its own history split by date, the table opens with the four baselines, the judge is separate from the retriever, and choices between methods are made on the month before the evaluation month.
3. A client without history starts cold. Its test questions are drawn from its own frequently asked questions and documents, and a second language model plays the judge.
4. The automatic judge is checked against the author's hand labels on the first client before it scores any client, and its agreement with those labels is reported next to every number it produces.
5. The method is inherited and the code is rewritten as one common piece of the base. promptfoo (MIT) and Ragas (Apache 2.0) can serve the judge, and Langfuse stores the traces and the judge's verdicts per client (ADR 0004).

## Alternatives considered

One shared test set for every client was rejected, because each client answers from different content. A model judge with no hand labels behind it was rejected for the reason of ADR 0006 of the clinic repository: a judge that nobody checked can make any method look good.

## Consequences

A cold-start number comes from questions written from documents, with no real user behind them, so the README says which kind each number is. The rule of ADR 0007 of the clinic repository that names July as the development month becomes, per client, the month before the evaluation month. The conversations a cold-start client receives become the history that later moves it to decision 2, and monitoring shows per client the replies the judge failed (ADR 0001).
