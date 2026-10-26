"""The judge of ADR 0006: does a retrieved reply say the same thing as the real reply?

The judge is one function shared by every row of the results table, and it never uses the
retriever. The retrievers compare patient turns, the judge compares clinic replies, with a
similarity of its own: TF-IDF over character n-grams of the replies, cosine. Its threshold
is set once on the 50 hand-labeled cases (scripts/fit_judge_threshold.py) and stays fixed.
"""

from __future__ import annotations

from collections.abc import Iterable

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel

from clinic_reply.pii import fold


class ReplyJudge:
    """Similarity between clinic replies, and the yes/no of "says the same thing"."""

    def __init__(self, threshold: float) -> None:
        self.threshold = threshold
        self._vectorizer = TfidfVectorizer(analyzer="char_wb", ngram_range=(3, 5))

    def fit(self, replies: Iterable[str]) -> ReplyJudge:
        """Learn the n-gram vocabulary from the index replies."""
        self._vectorizer.fit([fold(reply) for reply in replies])
        return self

    def similarity(self, candidates: list[str], real: str) -> np.ndarray:
        """Cosine similarity of each candidate reply to the real one, in [0, 1]."""
        if not candidates:
            return np.zeros(0)
        matrix = self._vectorizer.transform([fold(text) for text in candidates])
        target = self._vectorizer.transform([fold(real)])
        return linear_kernel(matrix, target)[:, 0]

    def hit(self, candidates: list[str], real: str) -> bool:
        """True when at least one candidate reaches the threshold."""
        scores = self.similarity(candidates, real)
        return bool(len(scores) and scores.max() >= self.threshold)
