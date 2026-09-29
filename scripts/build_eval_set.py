"""Build the evaluation set from the raw export and write its counts to reports/eval_set.json.

Usage: CLINIC_RAW_DIR=/path/to/export uv run python scripts/build_eval_set.py
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from clinic_reply.config import CUTOFF_DATE, PROCESSED_DIR, RAW_DIR, REPORTS_DIR
from clinic_reply.eval_set import build_eval_set


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--raw-dir", type=Path, default=RAW_DIR)
    parser.add_argument("--out-dir", type=Path, default=PROCESSED_DIR)
    parser.add_argument("--cutoff", default=CUTOFF_DATE)
    args = parser.parse_args()

    summary = build_eval_set(args.raw_dir, args.out_dir, cutoff=args.cutoff)
    REPORTS_DIR.mkdir(exist_ok=True)
    (REPORTS_DIR / "eval_set.json").write_text(json.dumps(summary, indent=2) + "\n")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
