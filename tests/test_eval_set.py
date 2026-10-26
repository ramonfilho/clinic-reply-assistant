import pandas as pd

from clinic_reply.eval_set import build_eval_set, build_name_set, canned_opener_texts
from clinic_reply.load import Export


def test_build_writes_scrubbed_pairs_and_counts(raw_dir, tmp_path):
    out_dir = tmp_path / "processed"
    summary = build_eval_set(raw_dir, out_dir, cutoff="2030-01-01", max_name_share=1.0)
    index_pairs = pd.read_parquet(out_dir / "pairs_index.parquet")
    assert summary["pairs"] == 1
    assert summary["eval"]["pairs"] == 0
    assert index_pairs.loc[0, "query"] == "Quero saber da campanha. Meu número é [PHONE]"
    assert index_pairs.loc[0, "reply"] == "Oi [NAME], tudo bem?\nPosso te passar a campanha?"


def test_profile_words_that_are_ordinary_language_are_not_scrubbed():
    messages = pd.DataFrame({"text": ["tudo bem?", "tudo certo", "oi Marina", "tudo pronto"]})
    export = Export(messages, frozenset({"Marina Tudo"}), frozenset({"Bia Prado"}))
    names, left_out = build_name_set(export, max_share=0.5)
    assert names == {"marina", "bia", "prado"}
    assert left_out == ["tudo"]


def test_profile_words_written_in_lower_case_are_language_not_names():
    texts = ["oi Marina, tudo bem?", "seus olhos ficaram lindos", "cuidar dos olhos e da boca"]
    export = Export(pd.DataFrame({"text": texts}), frozenset({"Marina Olhos"}), frozenset())
    names, left_out = build_name_set(export, max_share=1.0)
    assert names == {"marina"}
    assert left_out == ["olhos"]


def test_canned_opener_is_a_query_text_that_repeats_in_the_training_period():
    opener = "Oi! Gostaria de saber mais sobre a campanha"
    pairs = pd.DataFrame(
        {
            "query": [opener, opener, "Quanto custa o botox?", opener],
            "is_query": [True, True, True, False],
        }
    )
    assert canned_opener_texts(pairs, min_count=2) == {opener}
    assert canned_opener_texts(pairs, min_count=3) == set()


def test_build_flags_canned_openers_from_the_training_count(raw_dir, tmp_path):
    out_dir = tmp_path / "processed"
    summary = build_eval_set(
        raw_dir, out_dir, cutoff="2030-01-01", max_name_share=1.0, canned_min_count=1
    )
    index_pairs = pd.read_parquet(out_dir / "pairs_index.parquet")
    assert summary["canned_opener_texts"] == 1
    assert summary["index"]["canned_opener_queries"] == 1
    assert bool(index_pairs.loc[0, "canned_opener"]) is True
