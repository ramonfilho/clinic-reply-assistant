"""Show what the name filter keeps and what it leaves out, so the two thresholds can be checked.

The filter (ADR 0003 amendment) takes every word of the patients' profile names as a name
candidate and drops two kinds as ordinary language: words that appear in more than
NAME_MAX_MESSAGE_SHARE of the messages, and rarer words that are written in lower case in the
middle of a sentence more than NAME_MIN_CAPITALIZED_SHARE of the time. This script prints the
words each rule drops, with their counts, and the attendants' names as the kept side.

It prints words and counts only, never a message and never a full profile name.

Usage: CLINIC_RAW_DIR=/path/to/export uv run python scripts/inspect_name_filter.py [--top 15]
"""

from __future__ import annotations

import argparse
from collections import Counter

from clinic_reply.config import NAME_MAX_MESSAGE_SHARE, NAME_MIN_CAPITALIZED_SHARE, RAW_DIR
from clinic_reply.eval_set import _MID_SENTENCE
from clinic_reply.load import load_export
from clinic_reply.pii import fold, name_words, words


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--top", type=int, default=15, help="rows to print per table")
    args = parser.parse_args()

    export = load_export(RAW_DIR)
    attendants = name_words(export.attendant_names)
    candidates = name_words(export.patient_names) - attendants
    texts = [text for text in export.messages["text"] if text]
    n_texts = len(texts)

    in_messages: Counter[str] = Counter()
    mid_sentence: Counter[str] = Counter()
    capitalized: Counter[str] = Counter()
    for text in texts:
        in_messages.update(set(words(text)))
        for token in _MID_SENTENCE.findall(text):
            key = fold(token)
            if key in candidates or key in attendants:
                mid_sentence[key] += 1
                capitalized[key] += token[0].isupper()

    def share(word: str) -> float:
        return in_messages[word] / n_texts

    def capitalized_share(word: str) -> float:
        return capitalized[word] / mid_sentence[word] if mid_sentence[word] else float("nan")

    frequent = sorted((w for w in candidates if share(w) > NAME_MAX_MESSAGE_SHARE), key=share)
    frequent.reverse()
    lower_case = sorted(
        (
            w
            for w in candidates
            if share(w) <= NAME_MAX_MESSAGE_SHARE
            and mid_sentence[w]
            and capitalized_share(w) < NAME_MIN_CAPITALIZED_SHARE
        ),
        key=lambda w: -mid_sentence[w],
    )
    kept = len(candidates) - len(frequent) - len(lower_case) + len(attendants)

    print(f"messages with text: {n_texts:,}")
    print(f"profile name candidates: {len(candidates):,}, attendant name words: {len(attendants)}")
    print(f"kept as names: {kept:,}, dropped as language: {len(frequent) + len(lower_case)}")

    print(
        f"\nRule 1: in more than {NAME_MAX_MESSAGE_SHARE:.1%} of the messages "
        f"({len(frequent)} words)"
    )
    print(f"{'word':16s} {'messages':>9s} {'share':>7s}")
    for word in frequent[: args.top]:
        print(f"{word:16s} {in_messages[word]:9,d} {share(word):7.1%}")

    print(
        f"\nRule 2: below that, capitalized mid-sentence less than "
        f"{NAME_MIN_CAPITALIZED_SHARE:.0%} of the time ({len(lower_case)} words)"
    )
    print(f"{'word':16s} {'mid-sentence':>12s} {'capitalized':>11s} {'share':>7s}")
    for word in lower_case[: args.top]:
        print(
            f"{word:16s} {mid_sentence[word]:12,d} {capitalized[word]:11,d} "
            f"{capitalized_share(word):7.0%}"
        )

    print("\nKept side, the attendants' names (always scrubbed, whatever their share):")
    print(f"{'word':16s} {'messages':>9s} {'share':>7s} {'mid-sentence':>12s} {'capitalized':>11s}")
    for word in sorted(attendants):
        print(
            f"{word:16s} {in_messages[word]:9,d} {share(word):7.2%} "
            f"{mid_sentence[word]:12,d} {capitalized_share(word):11.0%}"
        )


if __name__ == "__main__":
    main()
