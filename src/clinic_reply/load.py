"""Read the BotConversa export into one table of messages.

The export is a folder of JSON files. Each file holds a list of conversations, and each
conversation holds its messages from the newest to the oldest. This module puts the
messages in chronological order, recovers the attendant's name when it comes as a bold
prefix in the text, and marks every clinic message as written by a person or by nobody
we can identify (the out-of-hours template and the bot flow carry no author).
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path

import pandas as pd

from clinic_reply.config import TIMEZONE

# "*Ana Prado*\n\nPosso te passar a campanha?" -> attendant "Ana Prado"
_NAME_PREFIX = re.compile(r"^\*([^*\n]{2,40})\*[ \t]*(?:\r?\n)+")

COLUMNS = ["conversation_id", "message_id", "ts", "sender", "kind", "text", "attendant", "author"]


@dataclass(frozen=True)
class Export:
    """The messages plus the names the PII step has to remove from them."""

    messages: pd.DataFrame
    patient_names: frozenset[str]
    attendant_names: frozenset[str]


def split_name_prefix(text: str, attendants: frozenset[str]) -> tuple[str | None, str]:
    """Return (attendant, text without the prefix) when the text opens with *Name*.

    Bold text at the start of a message is a signature only when it names an attendant that
    the export shows in the attendant field. Any other bold opening, such as the heading of a
    price list, is content and stays in the text.
    """
    match = _NAME_PREFIX.match(text)
    if match and match.group(1).strip() in attendants:
        return match.group(1).strip(), text[match.end() :]
    return None, text


def _attendants_in_field(conversations: list[dict]) -> frozenset[str]:
    """The set of names seen in the attendant field, across every message."""
    names = set()
    for conversation in conversations:
        for message in conversation["mensagens"]:
            name = (message.get("atendente") or "").strip()
            if name:
                names.add(name)
    return frozenset(names)


def _rows(conversation: dict, attendants: frozenset[str]) -> list[dict]:
    """Turn each message of one conversation into one row with the 8 columns."""
    rows = []
    for message in conversation["mensagens"]:
        prefix_name, text = split_name_prefix(message.get("texto") or "", attendants)
        attendant = (message.get("atendente") or "").strip() or prefix_name
        if not message["de_mim"]:
            sender, author = "patient", "patient"
        elif attendant:
            sender, author = "clinic", "human"
        else:
            sender, author = "clinic", "unknown"
        rows.append(
            {
                "conversation_id": conversation["chat_id"],
                "message_id": message["id"],
                "ts": int(message["ts"]),
                "sender": sender,
                "kind": message.get("tipo") or "unknown",
                "text": text,
                "attendant": attendant,
                "author": author,
            }
        )
    return rows


def load_export(raw_dir: Path) -> Export:
    """Load every JSON file in raw_dir. Messages come out in chronological order.

    The patient and attendant names come back apart from the table, for the PII step.
    """
    files = sorted(Path(raw_dir).glob("*.json"))
    if not files:
        raise FileNotFoundError(f"no JSON export found in {raw_dir}")
    conversations: list[dict] = []
    for file in files:
        with open(file, encoding="utf-8") as handle:
            conversations.extend(json.load(handle)["conversas"])
    attendants = _attendants_in_field(conversations)
    rows: list[dict] = []
    patient_names: set[str] = set()
    for conversation in conversations:
        if conversation.get("nome"):
            patient_names.add(conversation["nome"])
        rows.extend(_rows(conversation, attendants))
    messages = pd.DataFrame(rows, columns=COLUMNS)
    messages["ts"] = pd.to_datetime(messages["ts"], unit="s", utc=True).dt.tz_convert(TIMEZONE)
    messages["attendant"] = messages["attendant"].astype("string")  # missing -> pd.NA
    messages = messages.sort_values(
        ["conversation_id", "ts", "message_id"], kind="stable"
    ).reset_index(drop=True)
    attendant_names = frozenset(messages["attendant"].dropna().unique())
    return Export(messages, frozenset(patient_names), attendant_names)
