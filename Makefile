.PHONY: test install build notebooks lint format benchmark

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

benchmark:
	uv run python -m symbol_mutator.benchmark --targets-dir data/benchmark/targets --providers openai --intensities 1 2 3 4 5