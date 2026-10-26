import numpy as np
import pandas as pd

from clinic_reply.retrieve import (
    exact_match_replies,
    index_of,
    most_frequent_replies,
    nearest_replies,
    random_replies,
    tfidf_replies,
)

OPENER = "Oi! Gostaria de saber mais sobre a campanha"


def _index():
    rows = [
        ("2026-03-01", OPENER, "Oi! Já te explico a campanha", True),
        ("2026-03-02", "Qual o valor do botox?", "O botox está R$ 900", True),
        ("2026-03-03", "Onde fica a clínica?", "Ficamos na Rua das Flores, 10", True),
        ("2026-03-04", OPENER, "Oi! Te explico a campanha agora", True),
        ("2026-03-05", "Sim", "Perfeito, vou agendar", False),
        ("2026-03-06", OPENER, "Oi! Já te explico a campanha", True),
    ]
    return pd.DataFrame(
        {
            "ts": pd.to_datetime([r[0] for r in rows]),
            "query": [r[1] for r in rows],
            "reply": [r[2] for r in rows],
            "is_query": [r[3] for r in rows],
        }
    )


def test_index_keeps_the_queries_oldest_first():
    index = index_of(_index().iloc[::-1])
    assert list(index["query"])[:2] == [OPENER, "Qual o valor do botox?"]
    assert "Sim" not in set(index["query"])


def test_random_is_the_same_draw_on_every_run_and_has_no_repeats():
    index = index_of(_index())
    first = random_replies(index, ["a", "b"], k=3)
    second = random_replies(index, ["a", "b"], k=3)
    assert first == second
    assert len(first[0]) == 3 and len(set(first[0])) == 3


def test_most_frequent_returns_the_same_top_list_for_every_query():
    index = index_of(_index())
    replies = most_frequent_replies(index, ["a", "b"], k=2)
    assert replies[0] == replies[1]
    assert replies[0][0] == "Oi! Já te explico a campanha"


def test_exact_match_returns_distinct_replies_most_recent_first_or_nothing():
    index = index_of(_index())
    replies = exact_match_replies(index, [OPENER, "Quanto custa?"], k=5)
    assert replies[0] == ["Oi! Já te explico a campanha", "Oi! Te explico a campanha agora"]
    assert replies[1] == []


def test_tfidf_ranks_the_reply_of_the_closest_query_first():
    index = index_of(_index())
    replies = tfidf_replies(index, ["quanto custa o BOTOX?"], k=2)
    assert replies[0][0] == "O botox está R$ 900"
    assert len(replies[0]) == 2


def _word_encoder(texts):
    """A stand-in for the embedding model: one dimension per word, unit length."""
    vocab = ["botox", "valor", "clinica", "fica", "campanha"]
    rows = []
    for text in texts:
        words = text.lower().replace("?", "").replace("í", "i").split()
        vec = np.array([float(w in words) for w in vocab]) + 1e-6
        rows.append(vec / np.linalg.norm(vec))
    return np.array(rows)


def test_nearest_replies_answers_from_the_closest_vector_without_repeats():
    index = index_of(_index())
    [botox, where, opener] = nearest_replies(
        index, ["botox valor", "onde fica a clinica", OPENER], k=2, encode=_word_encoder
    )
    assert botox[0] == "O botox está R$ 900"
    assert where[0] == "Ficamos na Rua das Flores, 10"
    assert opener[0] in {"Oi! Já te explico a campanha", "Oi! Te explico a campanha agora"}
    assert len(opener) == len(set(opener)) == 2
