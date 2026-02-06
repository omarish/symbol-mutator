.PHONY: test install build

test:
	uv run pytest

install:
	uv sync

build:
	uv build
