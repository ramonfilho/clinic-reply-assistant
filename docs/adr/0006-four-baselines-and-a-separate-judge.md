# ADR 0006: The metric script opens with four baselines and a judge separate from the retriever

Status: accepted, 2026-09-29

## Context

ADR 0004 and item 4 of the brief ask for "a lexical baseline" as the first row of the results table without saying which one. The author's project checklist, read on 2026-09-26 before this block (items 1 and 2, which follow rules 1 and 2 of Zinkevich's "Rules of Machine Learning" and the first steps of Karpathy's "A Recipe for Training Neural Networks"), asks for a baseline without machine learning, measured on the same evaluation set before the model, so that the gain of the model is a number against that line. The lead scoring system at Bring Data started with a random forest and no baseline, and the gain over a plain rule never became a number. Of the 2,031 held-out queries, 924 are canned openers whose reply is the same script every time (ADR 0005), and a baseline that answers them without a model shows how much of the metric they carry on their own.

## Decision

1. The metric script computes recall at 5 (ADR 0002) for four methods before any embedding, each one a row of the results table, on all queries and on the queries that are not a canned opener. The index every method searches is the training pairs whose patient turn is a query (rule 3 of ADR 0005): a short turn such as "Sim" gets a reply that depends on the clinic's previous question, so it would answer a new patient out of context.
   1. Random: five replies drawn at random from the index, with a fixed seed. The floor.
   2. Most frequent: the five most frequent replies of the index, the same for every query. The floor of a system that never reads the message.
   3. Exact match: the replies given to index queries whose text is identical to the new query, most recent first, when any exists. Answers the canned openers with no model.
   4. Lexical: TF-IDF over the patient turns of the index, cosine similarity, top five. The lexical baseline the brief asks for.
2. The judge that decides "says the same thing" between a retrieved reply and the real reply is one function shared by every row, and it never uses the retriever: the retrievers compare patient turns, the judge compares clinic replies, with a similarity of its own. Its threshold is set once on the 50 hand-labeled cases of ADR 0002 and does not change between rows.
3. Every later method (an embedding model, another k, the previous clinic turn added to the query) is one more row measured by the same script, and the README states the gain of each row over row 4 next to its cost per 1,000 queries and its median latency.

## Alternatives considered

Starting with the embedding model and adding a baseline afterwards was rejected because a baseline written after the model gets tuned to lose. BM25 in place of TF-IDF was considered and stays as a possible row: TF-IDF comes first because scikit-learn is already a dependency and the vocabulary fit is the only fitting of stage one. One baseline instead of four was rejected because each answers a different question: what chance gives, what never reading the message gives, what the canned openers give by themselves, and what the words give.

## Consequences

The results table opens with four rows before the first embedding row. Rows 1 and 2 are floors, row 3 measures what the canned openers give on their own, and row 4 is the line every model has to beat. A method cannot score itself, because the judge is not the retriever. The 50 hand-labeled cases come before the first number, and the agreement between the labels and the threshold is reported in the README.

## Amendment (2026-09-30)

The first round of 50 labels (2026-09-29) set the threshold at 0.13 with 49 of 50 in agreement, and the random row then scored 0.569 on the queries that are not canned openers, which says the judge was too lenient rather than the retrievers good. Two causes showed up in the sample: 25 of the 50 cases sat above 0.8 of similarity, 20 of them canned openers that any threshold gets right, and every case came from the TF-IDF row, while the judge scores all four. A second round of 30 cases draws only non-canned queries from the band between 0.05 and 0.60, half from the random row and half from TF-IDF, and the threshold is set once on the 80 cases together. The README reports the agreement per round.

The same day the author asked for recall at 1 next to recall at 5, and the script reports both. With the judge set on the 80 cases (threshold 0.14, 86% agreement), a single random reply matches the real one in about one query in seven, because the clinic answers from a script with few steps, and five random replies reach about half the queries. Recall at 1 separates the methods where recall at 5 compresses them.
