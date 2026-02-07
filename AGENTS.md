# Agent Guide: Symbol Mutator

Welcome, fellow Agent. This document provides the context needed for you to productively contribute to `symbol-mutator`.

## Core Mission

The goal of this library is to **prevent Large Language Models (LLMs) from recognizing memorized code**. By obfuscating code in a semantics-preserving way, we create a "clean room" for evaluating an LLM's true reasoning capabilities, unshielded by its training data memory.

## Key Metric: Identification Rate (IR)

Our primary objective is to minimize the **Identification Rate (IR)**:

- **What it is**: The probability (0.0 to 1.0) that a frontier LLM (e.g., GPT-4o) can correctly name the original library derived from a mutated snippet.
- **How we measure it**: See `BENCHMARK.md`. We use a structured JSON prompt that asks for `{ "library": "...", "confidence_score": 0.x }`.
- **Goal**: Minimize IR while ensuring the code remains syntactically valid and semantically equivalent.

## Technical Architecture

### Core Components

- **`SymbolCollector`**: Uses `libcst` to walk the AST and identify renameable symbols (Classes, Functions, Parameters, Locals, Attributes).
- **`NameGenerator`**: Deterministic renamer. Supports themes like `gibberish`, `fantasy`, and `multilingual`.
- **`Mutator`**: The orchestrator. It manages the collection and transformation phases, applying different `cst.CSTTransformer` implementations based on the `intensity` level.

### Obfuscation Levels

1. **Symbol Renaming**: Deterministic mapping of identifiers.
2. **Comment Stripping**: Removal of docstrings and comments.
3. **Multilingual Renaming**: Uses non-Latin characters (Arabic, Cyrillic) to disrupt tokenizers.
4. **Structural Inversion**: Swapping `if/else` logic and reordering independent statements.
5. **Context Scrubbing**: Renaming internal variables/attributes and perturbing whitespace.

## How to Work on this Repository

### Verification

- **Unit Tests**: Run `make test` (or `uv run pytest`). All new transformers must have unit tests in `tests/test_mutator.py`.
- **Benchmarks**: Run `make benchmark`. This is the ultimate test of any new obfuscation technique.

### Development Guidelines

1. **Semantics First**: Never implement a transformation that could break the logic of the code.
2. **Deterministic**: All mutations must depend on the `seed`.
3. **AST-Based**: Always use `libcst` for transformations; never use regex for code manipulation.
4. **Benchmark-Driven**: Before proposing a change to the core library, consider its impact on the IR in `BENCHMARK.md`.

## Active Roadmap

- Syntactic sugar removal/addition (e.g., list comps to loops).
- Type hint obfuscation.
- Module-level file renaming.
