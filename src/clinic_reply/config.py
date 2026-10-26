"""Paths and the few constants that every step shares."""

from __future__ import annotations

import os
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = REPO_ROOT / "data"
SAMPLE_DIR = DATA_DIR / "sample"  # synthetic, committed
PROCESSED_DIR = DATA_DIR / "processed"  # derived from real data, never committed
REPORTS_DIR = REPO_ROOT / "reports"

# The raw export is read from this folder and never copied into the repository.
RAW_DIR = Path(os.environ.get("CLINIC_RAW_DIR", DATA_DIR / "raw"))

TIMEZONE = "America/Sao_Paulo"

# Conversations that start on or after this date form the held-out set (ADR 0004).
CUTOFF_DATE = "2026-08-01"

# A patient turn needs at least this many content words to count as a query (ADR 0005).
MIN_CONTENT_WORDS = 3

# A query text that repeats verbatim at least this many times in the training period is a
# canned opener, such as the message the click-to-chat ad fills in (ADR 0005).
CANNED_OPENER_MIN_COUNT = 50

# A word from a profile name that appears in more than this share of the messages is ordinary
# language ("clinica", "tudo") and is not scrubbed as a name (ADR 0003).
NAME_MAX_MESSAGE_SHARE = 0.005

# Below that share, a profile word is a name when it is written with a capital letter in at
# least this share of its appearances in the middle of a sentence ("Oi Maria" against
# "seus olhos").
NAME_MIN_CAPITALIZED_SHARE = 0.5

# Every retriever returns this many replies per query, and recall is measured at this k
# (ADR 0002).
TOP_K = 5

# The seed of the random baseline, so its row is the same on every run (ADR 0006).
RANDOM_SEED = 0

# The embedding model of row 5, run on the author's machine, and the prefix it expects on
# both sides when it compares a text with texts of the same kind (ADR 0008).
EMBEDDING_MODEL = "intfloat/multilingual-e5-small"
EMBEDDING_PREFIX = "query: "
