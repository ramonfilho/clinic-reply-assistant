"""Measure recall at 1 and at 5 for every retriever on the held-out queries (ADR 0002, 0006).

Recall at 1 judges only the first reply of each list, recall at 5 the whole list. One row per
retriever, on all queries and on the queries that are not a canned opener, with two costs:
the one-time setup (loading a model, fitting or encoding the index), measured by a call with
no queries, and the seconds per 1,000 queries after it. The judge threshold comes from
reports/judge.json, written from the hand labels, and the script stops without it: the 50
labeled cases come before the first number.

Usage: uv run python scripts/evaluate.py
"""

from __future__ import annotations

import json
import time
from datetime import date

import pandas as pd

from clinic_reply.config import PROCESSED_DIR, REPORTS_DIR, TOP_K
from clinic_reply.judge import ReplyJudge
from clinic_reply.retrieve import RETRIEVERS, index_of

JUDGE_FILE = REPORTS_DIR / "judge.json"
RESULTS_FILE = REPORTS_DIR / "results.json"


def main() -> None:
    if not JUDGE_FILE.exists():
        raise SystemExit(f"{JUDGE_FILE} is missing: label the 50 cases and run fit_judge_threshold")
    judge_info = json.loads(JUDGE_FILE.read_text())

    index_pairs = pd.read_parquet(PROCESSED_DIR / "pairs_index.parquet")
    eval_pairs = pd.read_parquet(PROCESSED_DIR / "pairs_eval.parquet")
    index = index_of(index_pairs)
    queries = eval_pairs[eval_pairs["is_query"]].reset_index(drop=True)
    judge = ReplyJudge(judge_info["threshold"]).fit(index["reply"])
    not_canned = ~queries["canned_opener"].to_numpy()

    rows = []
    for name, retriever in RETRIEVERS.items():
        start = time.perf_counter()
        retriever(index, [], TOP_K)
        setup = time.perf_counter() - start
        start = time.perf_counter()
        retrieved = retriever(index, list(queries["query"]), TOP_K)
        per_query = max(time.perf_counter() - start - setup, 0.0) / len(queries)
        cases = list(zip(retrieved, queries["reply"], strict=True))
        hits = pd.Series([judge.hit(replies, real) for replies, real in cases])
        first = pd.Series([judge.hit(replies[:1], real) for replies, real in cases])
        rows.append(
            {
                "method": name,
                "recall_at_1_all": round(float(first.mean()), 3),
                "recall_at_1_not_canned": round(float(first[not_canned].mean()), 3),
                "recall_at_5_all": round(float(hits.mean()), 3),
                "recall_at_5_not_canned": round(float(hits[not_canned].mean()), 3),
                "setup_seconds": round(setup, 1),
                "seconds_per_1000_queries": round(per_query * 1000, 2),
            }
        )

    results = {
        "measured_on": date.today().isoformat(),
        "k": TOP_K,
        "index_pairs": int(len(index)),
        "queries": int(len(queries)),
        "queries_not_canned": int(not_canned.sum()),
        "judge": judge_info,
        "rows": rows,
    }
    RESULTS_FILE.write_text(json.dumps(results, indent=2) + "\n")
    table = pd.DataFrame(rows).to_string(index=False)
    print(f"{len(queries)} held-out queries, {int(not_canned.sum())} not canned, k={TOP_K}")
    print(table)


if __name__ == "__main__":
    main()
