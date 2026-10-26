"""Temporal split (ADR 0004).

Conversations that start on or after the cutoff date are held out, whole. A conversation that
starts before the cutoff and runs past it stays in the training side, so no held-out case has
an earlier turn of its own conversation in the index the system retrieves from.
"""

from __future__ import annotations

import pandas as pd

from clinic_reply.config import CUTOFF_DATE, TIMEZONE


def split_by_conversation_start(
    pairs: pd.DataFrame, cutoff: str = CUTOFF_DATE
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Return (index_pairs, eval_pairs) by the start of each case's conversation."""
    held_out = pairs["conversation_start"] >= pd.Timestamp(cutoff, tz=TIMEZONE)
    return pairs[~held_out].reset_index(drop=True), pairs[held_out].reset_index(drop=True)
