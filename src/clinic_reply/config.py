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

# Conversations that start on or after this date form the held-out set (ADR 0004).
CUTOFF_DATE = "2026-08-01"

# A patient turn needs at least this many content words to count as a query (ADR 0005).
MIN_CONTENT_WORDS = 3
