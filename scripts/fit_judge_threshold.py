"""Set the judge threshold from the hand-labeled cases and report the agreement (ADR 0006).

Reads every data/processed/judge_labels*.csv (all rounds together), tries every threshold
from 0.05 to 0.95, keeps the one that agrees with the most labels, and writes it to
reports/judge.json with the agreement. The metric script reads the threshold from there and
never changes it.

Usage: uv run python scripts/fit_judge_threshold.py
"""

from __future__ import annotations

import json
from datetime import date

import numpy as np
import pandas as pd

from clinic_reply.config import PROCESSED_DIR, REPORTS_DIR

JUDGE_FILE = REPORTS_DIR / "judge.json"


def main() -> None:
    files = sorted(PROCESSED_DIR.glob("judge_labels*.csv"))
    cases = pd.concat([pd.read_csv(f).assign(round=f.stem) for f in files], ignore_index=True)
    missing = cases["label"].isna().sum()
    if missing:
        raise SystemExit(
            f"{missing} of {len(cases)} cases have no label yet in {[f.name for f in files]}"
        )
    labels = cases["label"].astype(int).to_numpy()
    similarity = cases["similarity"].to_numpy()

    grid = np.round(np.arange(0.05, 0.96, 0.01), 2)
    agreement = [((similarity >= t).astype(int) == labels).mean() for t in grid]
    best = max(agreement)
    # Among the thresholds that tie, take the middle one, so the choice sits inside the band.
    ties = [t for t, a in zip(grid, agreement, strict=True) if a == best]
    threshold = float(ties[len(ties) // 2])

    summary = {
        "threshold": threshold,
        "agreement": round(float(best), 3),
        "cases": int(len(cases)),
        "rounds": {f.stem: int((cases["round"] == f.stem).sum()) for f in files},
        "labeled_same": int(labels.sum()),
        "tied_thresholds": [float(t) for t in ties],
        "labeled_on": date.today().isoformat(),
    }
    REPORTS_DIR.mkdir(exist_ok=True)
    JUDGE_FILE.write_text(json.dumps(summary, indent=2) + "\n")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
