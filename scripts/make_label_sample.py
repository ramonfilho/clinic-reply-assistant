"""Write the cases the author labels by hand to set the judge threshold (ADR 0002, 0006).

Each case is a held-out query, the reply the clinic really gave, and the first reply a
retriever returns for it. Cases are drawn by similarity band, so the labels cover the range
where the threshold can fall, and the file stays in data/processed/ (never committed). The
author fills the "label" column: 1 when the retrieved reply says the same thing as the real
one, 0 when it does not.

Round 1 (2026-09-29) drew 50 cases from the TF-IDF retriever over the whole range, and half
of them were canned openers at similarity 1.0. Round 2 draws from the band where the decision
lives, leaves the canned openers out, and takes half of the cases from the random retriever,
because the judge scores every row and not only the best one.

Usage: uv run python scripts/make_label_sample.py --out judge_labels_round2.csv \
           --cases 30 --exclude-canned --min-sim 0.05 --max-sim 0.60 --sources tfidf,random
"""

from __future__ import annotations

import argparse

import numpy as np
import pandas as pd

from clinic_reply.config import PROCESSED_DIR, RANDOM_SEED
from clinic_reply.judge import ReplyJudge
from clinic_reply.retrieve import RETRIEVERS, index_of


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", default="judge_labels.csv")
    parser.add_argument("--cases", type=int, default=50)
    parser.add_argument("--sources", default="tfidf")
    parser.add_argument("--exclude-canned", action="store_true")
    parser.add_argument("--min-sim", type=float, default=0.0)
    parser.add_argument("--max-sim", type=float, default=1.0)
    parser.add_argument("--bands", type=int, default=6)
    parser.add_argument("--force", action="store_true", help="overwrite a file that has labels")
    args = parser.parse_args()
    out = PROCESSED_DIR / args.out
    if out.exists() and not args.force:
        labeled = pd.read_csv(out)["label"].notna().sum()
        if labeled:
            raise SystemExit(f"{out} has {labeled} labels; pass --force to overwrite them")

    index_pairs = pd.read_parquet(PROCESSED_DIR / "pairs_index.parquet")
    eval_pairs = pd.read_parquet(PROCESSED_DIR / "pairs_eval.parquet")
    index = index_of(index_pairs)
    queries = eval_pairs[eval_pairs["is_query"]].reset_index(drop=True)
    if args.exclude_canned:
        queries = queries[~queries["canned_opener"]].reset_index(drop=True)
    judge = ReplyJudge(threshold=0.0).fit(index["reply"])

    pool = []
    for source in args.sources.split(","):
        retrieved = RETRIEVERS[source](index, list(queries["query"]), 1)
        for row, replies in zip(queries.itertuples(), retrieved, strict=True):
            if not replies:
                continue
            similarity = float(judge.similarity(replies, row.reply)[0])
            if args.min_sim <= similarity <= args.max_sim:
                pool.append((source, row.query, row.reply, replies[0], similarity))
    cases = pd.DataFrame(
        pool, columns=["source", "query", "real_reply", "retrieved_reply", "similarity"]
    )

    # The same number of cases from each band and each source, drawn at random inside them.
    rng = np.random.default_rng(RANDOM_SEED)
    edges = np.linspace(args.min_sim, args.max_sim, args.bands + 1)
    cases["band"] = pd.cut(cases["similarity"], edges, include_lowest=True)
    picked = []
    per_cell = -(-args.cases // (args.bands * len(args.sources.split(","))))  # rounded up
    for _, cell in cases.groupby(["band", "source"], observed=True):
        take = min(per_cell, len(cell))
        picked.append(cell.sample(n=take, random_state=int(rng.integers(1 << 30))))
    sample = pd.concat(picked)
    if len(sample) > args.cases:
        sample = sample.sample(n=args.cases, random_state=int(rng.integers(1 << 30)))
    sample = sample.sample(frac=1.0, random_state=int(rng.integers(1 << 30))).drop(columns="band")
    sample.insert(0, "case", range(1, len(sample) + 1))
    sample["label"] = ""
    out.parent.mkdir(parents=True, exist_ok=True)
    sample.to_csv(out, index=False)
    print(f"{len(sample)} cases written to {out}")
    print(
        sample.groupby("source")["similarity"].describe()[["count", "min", "50%", "max"]].round(2)
    )


if __name__ == "__main__":
    main()
