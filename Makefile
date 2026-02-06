.PHONY: test install build notebooks lint format

test:
	uv run pytest

install:
	uv sync --all-extras

build:
	uv build

lint:
	uv run ruff check .

format:
	uv run ruff format .

notebooks:
	uv run jupyter execute notebooks/deanonymization.ipynb