# Symbol Mutator

`symbol-mutator` is a Python tool designed to deterministically obfuscate identifiers (class names, function names, etc.) in a codebase. It is primarily used for creating benchmarks for Large Language Models (LLMs) to test their code understanding capabilities without relying on helpful semantic naming.

## Example

```python
# Original code
class DataProcessor:
    def __init__(self, data):
        self.data = data

    def process(self):
        return [x * 2 for x in self.data]

# Mutated code
class a_1b2c3d:
    def __init__(self, v_x9y8z7):
        self.v_x9y8z7 = v_x9y8z7

    def f_a1b2c3(self):
        return [v_x9y8z7 * 2 for v_x9y8z7 in self.v_x9y8z7]
```

## Features

- **Deterministic Obfuscation**: Uses a seed to ensure reproducible renaming.
- **Python Awareness**: Parses code using `libcst` to correctly identify and rename definitions and their usages, avoiding keywords and built-ins.
- **Preserves Internal Structure**: Renames class members and variable usages consistently.
- **Themes**:
  - `gibberish`: Alphanumeric hashes (e.g., `c_8f2a1d`, `f_2x9y1z`).
  - `fantasy`: RPG-style names (e.g., `ShadowWeaver`, `summon_blade`).
- **Internal/External Awareness**: Can be configured to recognize internal modules (renaming their imports) vs external libraries (preserving their API calls).

## De-anonymization Benchmark

We track the effectiveness of different mutation intensities against frontier LLMs. The goal is to minimize the **Identification Rate (IR)**.

### Current Performance (GPT-4o)

| Intensity Level | Description | Identification Rate (IR) |
| :--- | :--- | :--- |
| **Level 0** | Original Code | ~100% |
| **Level 1** | Deterministic Renaming | ~85% |
| **Level 2** | Level 1 + Comment Stripping | ~60% |
| **Level 3** | Level 2 + Multilingual Identifiers | *Pending* |
| **Level 4** | Level 3 + Structural Obfuscation | *Pending* |
| **Level 5** | Level 4 + Context & Local Obfuscation | *Pending* |

> [!TIP]
> Run the benchmark with: `uv run python -m symbol_mutator.benchmark --targets-dir data/benchmark/targets --providers openai`

## Installation

Requires Python 3.12+.

We recommend using [uv](https://github.com/astral-sh/uv) for package management.

```bash
# Install as a tool
uv tool install .

# Or install into current environment
uv pip install .
```

## Usage

### CLI

The package comes with a command-line interface:

```bash
# Mutate a whole directory
python -m symbol_mutator.cli --target /path/to/my_lib --output /path/to/mutated_lib --seed 42

# Mutate a single file
python -m symbol_mutator.cli --target script.py --output mutated_script.py --theme fantasy
```

**Arguments:**

- `--target`: Path to the input file or directory (required).
- `--output`: Path to the output destination (required).
- `--seed`: Random seed for deterministic renaming (default: 42).
- `--theme`: Naming theme, either `gibberish` (default) or `fantasy`.
- `--internal-prefix`: Specify package prefixes that should be treated as internal (i.e., we are renaming them too). Can be specified multiple times.

### Python API

You can also use `symbol-mutator` programmatically in your own scripts.

#### Mutating a Directory

```python
from pathlib import Path
from symbol_mutator import mutate_directory

mutate_directory(
    input_dir=Path("./original_code"),
    output_dir=Path("./obfuscated_code"),
    seed=123,
    theme="fantasy",
    internal_prefixes=["my_package"]
)
```

#### Mutating a Single File / String

For more fine-grained control, use the `Mutator` class directly:

```python
from symbol_mutator import Mutator

code = """
def calculate_area(radius):
    return 3.14 * radius * radius
"""

mutator = Mutator(seed=999, theme="gibberish")
mutated_code = mutator.mutate_source(code)

print(mutated_code)
# Output might look like:
#
# def f_a1b2c3(v_x9y8z7):
#     return 3.14 * v_x9y8z7 * v_x9y8z7
```

## Development

This project uses `uv` for dependency management.

```bash
# Install dependencies
uv sync

# Run comprehensive test suite
uv run pytest
```

## Future Work

- **Preserve Comments**: Currently, comments adjacent to renamed symbols might lose context or be displaced.
- **Type Hint Renaming**: Support renaming symbols effectively within string-based type hints (forward references).
- **File/Module Renaming**: Extend the tool to rename the physical files and update imports accordingly.
- **Auto-detection of External Libraries**: Automatically detect 3rd party imports to avoid manual configuration of `internal_prefixes`.
- **Update git history**: Update symbols throughout the git history.
- **Update documentation**: Update documentation to reflect the changes.
- Foreign languages: Try using different character sets/languages to see if this further obfuscates the code and makes it more "new" for LLMs. Arabic?
- **More Themes**: Add additional naming themes like `star_wars`, `mathematical_constants`, etc.
