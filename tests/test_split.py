import pandas as pd

from clinic_reply.split import split_by_conversation_start


def _case(conversation_id, start, ts):
    tz = "America/Sao_Paulo"
    return {
        "conversation_id": conversation_id,
        "conversation_start": pd.Timestamp(start, tz=tz),
        "ts": pd.Timestamp(ts, tz=tz),
    }


def test_a_conversation_stays_whole_on_the_side_where_it_started():
    pairs = pd.DataFrame(
        [
            _case("old", "2026-07-30 10:00", "2026-07-30 10:00"),
            _case("old", "2026-07-30 10:00", "2026-08-02 09:00"),  # runs past the cutoff
            _case("new", "2026-08-01 00:00", "2026-08-01 00:00"),
        ]
    )
    train, heldout = split_by_conversation_start(pairs, "2026-08-01")
    assert list(train["conversation_id"]) == ["old", "old"]
    assert list(heldout["conversation_id"]) == ["new"]
