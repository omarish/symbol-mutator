.PHONY: test install build notebooks

test:
	uv run pytest

install:
	uv sync

build:
	uv build

notebooks:
	uv run jupyter execute notebooks/deanonymization.ipynb