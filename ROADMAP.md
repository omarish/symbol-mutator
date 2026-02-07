# Symbol Mutator Roadmap

## Strategic Goal

To create a tool that modifies code sufficiently to prevent LLMs from recognizing it as "memorized" data, while preserving functionality. This enables true "out-of-distribution" reasoning tests.

## Proposed Improvements

### 1. Advanced Structural Obfuscation

Renaming symbols is the first step. To truly break pattern matching, we need to alter the AST structure:

- **Statement Reordering**: Swap independent statements where data dependency allows.
- **Control Flow Variation**:
  - Invert `if/else` logic (`if a: x else: y` $\to$ `if not a: y else: x`).
  - Convert `for` loops to `while` loops.
- **Syntactic Sugar Removal/Addition**: Expand list comprehensions into loops or vice versa.

### 2. Context Removal

- **Comment Stripping**: Remove all comments and docstrings.
- **Docstring Rewriting**: Replace helpful docstrings with generated, abstract, or misleading (but harmless) text.
- **Metadata Scrubbing**: Remove `__author__`, `@version`, and non-functional decorators.

### 3. "Foreign" & Exotic Encodings

- **Unicode Identifiers**: Use valid non-ASCII characters for identifiers (e.g., Arabic, Cyrillic, Emoji) as permitted by Python 3. This forcefully breaks tokenization patterns trained primarily on English ASCII code.
  - *Example*: `class DataProcessor` $\to$ `class معالج_البيانات`
- **Whitespace Perturbation**: Vary indentation (within syntax rules) and vertical spacing.

### 4. Repository-Level Mutation

- **Git History Rewriting**: `git filter-repo` integration to mutate the entire history. This prevents models from inferring context from commit messages or older versions if the test environment includes git metadata.
- **Documentation Sync**: Automatically update `README.md` and other docs to match the renamed symbols, so the "manual" provided to the LLM is consistent with the obfuscated code.

## Validation Strategy: "The Newness Test"

How do we know it works? We propose a **De-anonymization Benchmark**.

### Methodology

1. **Select Targets**: Choose 50 popular, highly memorized PyPI packages (e.g., `requests`, `flask`, `numpy`).
2. **Mutate**: Apply `symbol-mutator` with varying intensity (Rename only $\to$ Structure change $\to$ Comment stripping).
3. **Attack**: Prompt frontier LLMs (GPT-4, Claude 3.5, Gemini 1.5) with the mutated code.
    - *Prompt*: "Analyze this code. Identify which open-source library this is derived from."
4. **Metric**: **Identification Rate (IR)**.
    - *Goal*: Push IR from ~100% (original code) to <5% (mutated code).

### Secondary Metric: Perplexity

Run the mutated code through a base language model.

- **Hypothesis**: True "new" code should have higher perplexity (be more "surprising") than the memorized original training data.

### Verification of Functionality

We must ensure we haven't broken the code.

- **Automated Regression Testing**: Run the library's original test suite against the mutated codebase. PASS rate must be 100%.

## Next Steps

1. [x] Implement **Comment Stripping** (Low effort, high impact).
2. [x] Build the **De-anonymization Benchmark** script.
3. [x] Implement **Unicode/Multilingual Themes** (High impact on tokenization).
4. [x] Implement **Structural Obfuscation** (Statement reordering, if/else inversion).
5. [x] Implement **Context Removal** (Scrubbing metadata, full variable renaming).
6. [x] Implement **Whitespace Perturbation**.
7. [ ] Implement **Syntactic Sugar Removal/Addition**.
