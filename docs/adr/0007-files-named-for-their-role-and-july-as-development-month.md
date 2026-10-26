# ADR 0007: The pair files are named for their role, and July is the development month

Status: proposed, 2026-09-30 (decision 1 approved by the author the same day, decision 2 waits)

## Context

The evaluation set of ADR 0004 was written as `pairs_train.parquet` and `pairs_heldout.parquet`. Nothing in stage one is trained on the first file: the retrievers search it, and the only fitting is the TF-IDF vocabulary. A reader who sees "train" looks for a training loop that does not exist.

Every choice between methods that is made by looking at the August number (which embedding model, which k, whether the query carries the clinic's previous turn) makes that number optimistic. With three models scored on the same 2,031 queries, the one that wins is partly the one that got lucky on those queries, and the README would report its luck as its quality. July holds 1,653 conversations, 2,883 queries and 1,562 queries that are not a canned opener, enough to choose on.

## Decision

1. The files are `pairs_index.parquet` (conversations that start before 2026-08-01, the pairs the retrievers search) and `pairs_eval.parquet` (conversations from 2026-08-01, the pairs the metric scores), and `reports/eval_set.json` uses the keys `index` and `eval`.
2. Choices between methods are made on July: the index is the pairs of conversations that start before 2026-07-01, and the queries are the July queries. The chosen method is then measured once on August, with the whole index before 2026-08-01. New hand labels for the judge are drawn from July.

## Alternatives considered

Keeping the names was rejected because the defense of the repository starts with what each file is. A random validation split inside the index was rejected for the reason of ADR 0004: a case from the same conversation or the same week as the query leaks the answer, and the date split is the one production has.

## Consequences

Each method row that follows a choice carries two numbers, July (where it was chosen) and August (where it is reported). The 80 labels of ADR 0006 were drawn from August queries, so the judge threshold was set on the evaluation month, one number fit on 80 of 2,031 queries, and the README says so. The rename changed no data: the rebuilt files are identical to the old ones and the results table did not move.
