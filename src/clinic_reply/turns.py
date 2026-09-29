"""Turns and cases (ADR 0005).

A turn is a run of consecutive messages from the same side of the conversation. A case pairs
a patient turn that has text with the clinic turn that follows it, keeping only the text a
person wrote. A case is a query when the patient turn keeps at least MIN_CONTENT_WORDS words
after greetings and one-word acknowledgments are removed.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field

import pandas as pd

from clinic_reply.config import MIN_CONTENT_WORDS
from clinic_reply.pii import fold

# Words that carry no content on their own: greetings, thanks and one-word acknowledgments.
GREETINGS = frozenset(
    "oi oii oiii ola oie bom boa dia tarde noite tudo bem obrigado obrigada obg brigada brigado "
    "sim nao ok okay certo blz beleza entendi ah aham uhum ta perfeito otimo legal show vlw "
    "valeu td pode ser claro isso tb tambem entao ne kk kkk rs rsrs haha".split()
)
_TOKEN = re.compile(r"[^\W_]+")

PAIR_COLUMNS = [
    "conversation_id",
    "conversation_start",
    "ts",
    "query",
    "reply",
    "attendant",
    "n_content_words",
    "is_query",
]


def content_words(text: str) -> list[str]:
    """Words of the text, folded, without greetings and acknowledgments."""
    return [word for word in _TOKEN.findall(fold(text)) if word not in GREETINGS]


@dataclass
class Turn:
    sender: str
    ts: pd.Timestamp
    texts: list[str] = field(default_factory=list)
    attendant: str | None = None

    @property
    def text(self) -> str:
        return "\n".join(self.texts)


def turns_of(conversation: pd.DataFrame) -> list[Turn]:
    """Group the messages of one conversation, already in order, into turns.

    A turn keeps the text a person wrote: every patient text, and the clinic text that has an
    attendant behind it. Audio, images and the clinic messages with no author add nothing.
    """
    turns: list[Turn] = []
    for row in conversation.itertuples(index=False):
        if not turns or turns[-1].sender != row.sender:
            turns.append(Turn(row.sender, row.ts))
        if row.kind != "text" or (row.sender == "clinic" and row.author != "human"):
            continue
        text = row.text.replace("\r\n", "\n").strip()
        if not text:
            continue
        turn = turns[-1]
        turn.texts.append(text)
        if turn.attendant is None and row.sender == "clinic":
            turn.attendant = row.attendant
    return turns


def pair_turns(messages: pd.DataFrame) -> pd.DataFrame:
    """One row per case: a patient turn with text and the clinic's human reply right after it."""
    rows = []
    for conversation_id, conversation in messages.groupby("conversation_id", sort=False):
        turns = turns_of(conversation)
        for patient, clinic in zip(turns, turns[1:], strict=False):
            if patient.sender != "patient" or not patient.text or not clinic.text:
                continue
            n_content_words = len(content_words(patient.text))
            rows.append(
                {
                    "conversation_id": conversation_id,
                    "conversation_start": conversation["ts"].iloc[0],
                    "ts": patient.ts,
                    "query": patient.text,
                    "reply": clinic.text,
                    "attendant": clinic.attendant,
                    "n_content_words": n_content_words,
                    "is_query": n_content_words >= MIN_CONTENT_WORDS,
                }
            )
    return pd.DataFrame(rows, columns=PAIR_COLUMNS)
