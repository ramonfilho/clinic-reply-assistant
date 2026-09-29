.PHONY: setup test lint

setup:
	uv sync

test:
	uv run pytest -q

lint:
	uv run ruff check src tests scripts && uv run ruff format --check src tests scripts
