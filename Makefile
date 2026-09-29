.PHONY: setup test lint eval-set inspect-names

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
