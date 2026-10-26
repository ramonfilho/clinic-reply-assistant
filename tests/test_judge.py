from clinic_reply.judge import ReplyJudge

REPLIES = [
    "O botox está R$ 900, com avaliação inclusa",
    "Ficamos na Rua das Flores, 10",
    "Oi! Já te explico a campanha",
]


def _judge(threshold=0.5):
    return ReplyJudge(threshold).fit(REPLIES)


def test_identical_replies_score_one_and_unrelated_replies_score_low():
    judge = _judge()
    scores = judge.similarity(REPLIES, REPLIES[0])
    assert scores[0] > 0.999
    assert scores[1] < 0.2


def test_a_rewording_scores_above_an_unrelated_reply():
    judge = _judge()
    scores = judge.similarity(["O Botox esta R$ 900 com avaliacao", REPLIES[1]], REPLIES[0])
    assert scores[0] > scores[1]


def test_hit_needs_one_candidate_at_the_threshold_and_an_empty_list_misses():
    judge = _judge(threshold=0.5)
    assert judge.hit([REPLIES[1], REPLIES[0]], REPLIES[0])
    assert not judge.hit([REPLIES[1]], REPLIES[0])
    assert not judge.hit([], REPLIES[0])
