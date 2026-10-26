"""The retrievers: the four baselines of ADR 0006 and the embedding row of ADR 0008.

Every retriever has the same shape: it takes the index (the queries before the cutoff) and
a list of query texts, and returns one list of up to k reply texts per query, best first,
with no repeated text. The metric script measures each one as a row of the same table.
"""

from __future__ import annotations

from collections.abc import Callable

import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel

from clinic_reply.config import EMBEDDING_MODEL, EMBEDDING_PREFIX, RANDOM_SEED, TOP_K
from clinic_reply.pii import fold

Retriever = Callable[[pd.DataFrame, list[str], int], list[list[str]]]
Encoder = Callable[[list[str]], np.ndarray]


def index_of(pairs: pd.DataFrame) -> pd.DataFrame:
    """The pairs the retrievers search: the queries of the index period, oldest first."""
    return pairs[pairs["is_query"]].sort_values("ts", kind="stable").reset_index(drop=True)


def _distinct(replies: list[str], k: int) -> list[str]:
    """The first k distinct texts, in the order given."""
    seen: set[str] = set()
    out: list[str] = []
    for reply in replies:
        if reply not in seen:
            seen.add(reply)
            out.append(reply)
        if len(out) == k:
            break
    return out


def random_replies(index: pd.DataFrame, queries: list[str], k: int = TOP_K) -> list[list[str]]:
    """Row 1: k replies drawn at random from the index, the same draw on every run."""
    rng = np.random.default_rng(RANDOM_SEED)
    replies = index["reply"].drop_duplicates().to_numpy()
    size = min(k, len(replies))
    return [list(rng.choice(replies, size=size, replace=False)) for _ in queries]


def most_frequent_replies(
    index: pd.DataFrame, queries: list[str], k: int = TOP_K
) -> list[list[str]]:
    """Row 2: the k most frequent replies of the index, the same list for every query."""
    top = index["reply"].value_counts().index[:k].tolist()
    return [list(top) for _ in queries]


def exact_match_replies(index: pd.DataFrame, queries: list[str], k: int = TOP_K) -> list[list[str]]:
    """Row 3: the replies given to index queries with the same text, most recent first.

    A query with no identical text in the index gets an empty list.
    """
    by_text: dict[str, list[str]] = {}
    for text, reply in zip(index["query"], index["reply"], strict=True):
        by_text.setdefault(text, []).append(reply)
    return [_distinct(list(reversed(by_text.get(query, []))), k) for query in queries]


def tfidf_replies(
    index: pd.DataFrame, queries: list[str], k: int = TOP_K, batch: int = 256
) -> list[list[str]]:
    """Row 4: TF-IDF over the index queries, cosine similarity, the replies of the top matches.

    Texts are folded (lower case, no accents) before the vocabulary is fit, so "Botox" and
    "botox" are one word. Queries run in batches to keep the similarity matrix small.
    """
    vectorizer = TfidfVectorizer()
    matrix = vectorizer.fit_transform(index["query"].map(fold))
    replies = index["reply"].to_numpy()
    out: list[list[str]] = []
    for start in range(0, len(queries), batch):
        chunk = [fold(query) for query in queries[start : start + batch]]
        scores = linear_kernel(vectorizer.transform(chunk), matrix)
        for row in scores:
            order = np.argsort(-row, kind="stable")
            out.append(_distinct([replies[i] for i in order[: 4 * k]], k))
    return out


def e5_encoder(model_name: str = EMBEDDING_MODEL) -> Encoder:
    """Load the embedding model once and return a function that turns texts into unit vectors.

    The import sits inside the function so the baselines run without loading the model.
    """
    from sentence_transformers import SentenceTransformer

    model = SentenceTransformer(model_name)

    def encode(texts: list[str]) -> np.ndarray:
        prefixed = [EMBEDDING_PREFIX + text for text in texts]
        return model.encode(prefixed, batch_size=64, normalize_embeddings=True)

    return encode


def nearest_replies(
    index: pd.DataFrame, queries: list[str], k: int, encode: Encoder, batch: int = 256
) -> list[list[str]]:
    """The replies of the index queries whose vectors are closest to each query's vector.

    The vectors are unit length, so the dot product is the cosine similarity.
    """
    matrix = encode(list(index["query"]))
    replies = index["reply"].to_numpy()
    out: list[list[str]] = []
    for start in range(0, len(queries), batch):
        scores = encode(queries[start : start + batch]) @ matrix.T
        for row in scores:
            order = np.argsort(-row, kind="stable")
            out.append(_distinct([replies[i] for i in order[: 4 * k]], k))
    return out


def embedding_replies(index: pd.DataFrame, queries: list[str], k: int = TOP_K) -> list[list[str]]:
    """Row 5: the embedding model of ADR 0008 over the index queries, top matches' replies."""
    return nearest_replies(index, queries, k, e5_encoder())


RETRIEVERS: dict[str, Retriever] = {
    "random": random_replies,
    "most_frequent": most_frequent_replies,
    "exact_match": exact_match_replies,
    "tfidf": tfidf_replies,
    "embedding": embedding_replies,
}
