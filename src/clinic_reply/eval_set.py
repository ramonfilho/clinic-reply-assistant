"""Build the evaluation set: load, scrub, pair, split, write.

This is the first thing the pipeline produces (ADR 0004). Every later step, from the lexical
baseline to the generated replies, is measured on the held-out file written here.
"""

from __future__ import annotations

import re
from collections import Counter
from pathlib import Path

import pandas as pd

from clinic_reply.config import (
    CANNED_OPENER_MIN_COUNT,
    CUTOFF_DATE,
    NAME_MAX_MESSAGE_SHARE,
    NAME_MIN_CAPITALIZED_SHARE,
)
from clinic_reply.load import Export, load_export
from clinic_reply.pii import fold, name_words, scrub, words
from clinic_reply.split import split_by_conversation_start
from clinic_reply.turns import pair_turns

# A word that follows a lowercase letter or a comma and a space sits in the middle of a
# sentence, so its capital letter is not the one that opens a sentence.
_MID_SENTENCE = re.compile(r"(?<=[a-zà-ú,] )([^\W\d_]+)")


def build_name_set(
    export: Export,
    max_share: float = NAME_MAX_MESSAGE_SHARE,
    min_capitalized_share: float = NAME_MIN_CAPITALIZED_SHARE,
) -> tuple[frozenset[str], list[str]]:
    """The name words to scrub, and the profile words left out as ordinary language.

    Profile names on WhatsApp hold words such as "clinica", "tudo" or "olhos" next to real
    names. Two rules keep those words out. A word that appears in more than max_share of the
    messages is language. Below that, a word is a name only when it is written with a capital
    letter in at least min_capitalized_share of its appearances in the middle of a sentence,
    which is how names are written in chat ("Oi Maria") and common words are not ("seus
    olhos"). The attendants' names are always scrubbed, however often they appear.
    """
    candidates = name_words(export.patient_names)
    attendants = name_words(export.attendant_names)
    texts = [text for text in export.messages["text"] if text]
    document_frequency: Counter[str] = Counter()
    mid_sentence: Counter[str] = Counter()
    capitalized: Counter[str] = Counter()
    for text in texts:
        document_frequency.update(set(words(text)))
        for token in _MID_SENTENCE.findall(text):
            key = fold(token)
            if key in candidates:
                mid_sentence[key] += 1
                capitalized[key] += token[0].isupper()
    n_texts = max(len(texts), 1)
    language: set[str] = set()
    for word in candidates - attendants:
        if document_frequency[word] / n_texts > max_share:
            language.add(word)
        elif mid_sentence[word] and capitalized[word] / mid_sentence[word] < min_capitalized_share:
            language.add(word)
    return frozenset((candidates | attendants) - language), sorted(language)


def canned_opener_texts(pairs: pd.DataFrame, min_count: int = CANNED_OPENER_MIN_COUNT) -> set[str]:
    """Query texts that repeat verbatim at least min_count times among the training queries.

    These are the openers the click-to-chat ads fill in (ADR 0005). Only the training period
    counts, so a text that appears only after the cutoff is never a canned opener.
    """
    counts = pairs.loc[pairs["is_query"], "query"].value_counts()
    return set(counts[counts >= min_count].index)


def _counts(pairs: pd.DataFrame) -> dict:
    queries = pairs[pairs["is_query"]]
    return {
        "conversations": int(pairs["conversation_id"].nunique()),
        "pairs": int(len(pairs)),
        "queries": int(len(queries)),
        "canned_opener_queries": int(queries["canned_opener"].sum()),
    }


def build_eval_set(
    raw_dir: Path,
    out_dir: Path,
    cutoff: str = CUTOFF_DATE,
    max_name_share: float = NAME_MAX_MESSAGE_SHARE,
    canned_min_count: int = CANNED_OPENER_MIN_COUNT,
) -> dict:
    """Write pairs_index.parquet and pairs_eval.parquet to out_dir and return the counts."""
    export = load_export(raw_dir)
    names, left_out = build_name_set(export, max_name_share)
    messages = export.messages.copy()
    messages["text"] = [scrub(text, names) if text else text for text in messages["text"]]

    pairs = pair_turns(messages)
    index_pairs, eval_pairs = split_by_conversation_start(pairs, cutoff)
    canned = canned_opener_texts(index_pairs, canned_min_count)
    for frame in (index_pairs, eval_pairs):
        frame["canned_opener"] = frame["query"].isin(canned)

    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    index_pairs.to_parquet(out_dir / "pairs_index.parquet", index=False)
    eval_pairs.to_parquet(out_dir / "pairs_eval.parquet", index=False)
    (out_dir / "name_words_left_out.txt").write_text("\n".join(left_out) + "\n", encoding="utf-8")
    return {
        "cutoff": cutoff,
        "conversations": int(messages["conversation_id"].nunique()),
        "messages": int(len(messages)),
        "pairs": int(len(pairs)),
        "queries": int(pairs["is_query"].sum()),
        "index": _counts(index_pairs),
        "eval": _counts(eval_pairs),
        "canned_opener_texts": len(canned),
        "name_words_scrubbed": len(names),
        "name_words_left_out_as_language": len(left_out),
    }
