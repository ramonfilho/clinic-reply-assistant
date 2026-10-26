"""Label the 50 judge cases in the terminal, one at a time, saving after every answer.

Shows the patient query, the reply the clinic really gave and the reply the baseline
retrieved, and asks whether the retrieved reply says the same thing: 1 for yes, 0 for no,
s to skip for now, q to quit. Cases already labeled are not shown again, so the run resumes.

Usage: uv run python scripts/label_cases.py [--file judge_labels_round2.csv]
"""

from __future__ import annotations

import argparse

import pandas as pd

from clinic_reply.config import PROCESSED_DIR


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--file", default="judge_labels.csv")
    args = parser.parse_args()
    label_file = PROCESSED_DIR / args.file
    cases = pd.read_csv(label_file)
    todo = cases.index[cases["label"].isna()]
    print(f"{len(todo)} of {len(cases)} cases to label.")
    print("1 = same thing, 0 = not, s = skip, q = quit")
    for n, i in enumerate(todo, start=1):
        row = cases.loc[i]
        print(f"\n=== case {row.case} ({n} of {len(todo)}) ===")
        print(f"PATIENT:   {row.query}")
        print(f"REAL:      {row.real_reply}")
        print(f"RETRIEVED: {row.retrieved_reply}")
        while True:
            answer = input("same thing? [1/0/s/q] ").strip().lower()
            if answer in {"1", "0", "s", "q"}:
                break
        if answer == "q":
            break
        if answer == "s":
            continue
        cases.loc[i, "label"] = int(answer)
        cases.to_csv(label_file, index=False)
    left = int(cases["label"].isna().sum())
    print(f"\nsaved. {left} cases still without label.")


if __name__ == "__main__":
    main()
