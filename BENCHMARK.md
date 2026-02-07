# De-anonymization Benchmark

We track the effectiveness of different mutation intensities against frontier LLMs. The goal is to minimize the **Identification Rate (IR)**.

## Current Performance (GPT-4o)

| Intensity Level | Description | Identification Rate (IR) |
| :--- | :--- | :--- |
| **Level 0** | Original Code | ~100% |
| **Level 1** | Deterministic Renaming | 79% |
| **Level 2** | Level 1 + Comment Stripping | 73% |
| **Level 3** | Level 2 + Multilingual Identifiers | 83% |
| **Level 4** | Level 3 + Structural Obfuscation | 79% |
| **Level 5** | Level 4 + Context & Local Obfuscation | **51%** |

> [!TIP]
> Run the benchmark with: `uv run python -m symbol_mutator.benchmark --targets-dir data/benchmark/targets --providers openai`

## Methodology

The benchmark uses a set of simplified snippets from popular Python libraries:

- `fastapi`
- `flask`
- `loguru`
- `numpy`
- `pydantic`
- `requests`
- `wheel`

Each snippet is mutated at different intensity levels and then presented to an LLM with a prompt to identify the original library. The model provides a confidence score and reasoning in a structured JSON format.
