.PHONY: setup test lint eval-set inspect-names label-sample label judge-threshold evaluate

setup:
	uv sync

test:
	uv run pytest -q

lint:
	uv run ruff check src tests scripts && uv run ruff format --check src tests scripts

# Point CLINIC_RAW_DIR at the export folder. The output goes to data/processed/, never committed.
eval-set:
	uv run python scripts/build_eval_set.py

# Prints the profile words the name filter drops as language and the attendants' names it keeps.
inspect-names:
	uv run python scripts/inspect_name_filter.py

label-sample:
	uv run python scripts/make_label_sample.py

label-sample-2:
	uv run python scripts/make_label_sample.py --out judge_labels_round2.csv --cases 30 --exclude-canned --min-sim 0.05 --max-sim 0.60 --sources tfidf,random

label:
	uv run python scripts/label_cases.py --file $(or $(FILE),judge_labels.csv)

judge-threshold:
	uv run python scripts/fit_judge_threshold.py

evaluate:
	uv run python scripts/evaluate.py
