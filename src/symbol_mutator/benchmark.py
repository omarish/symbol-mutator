import argparse
import os
import sys
from pathlib import Path
from typing import List, Dict

from dotenv import load_dotenv
from .core import Mutator
from .llm import get_provider

def run_benchmark(
    targets: List[Path],
    providers: List[str],
    intensities: List[int],
    seed: int = 42
):
    load_dotenv()
    
    results = []

    for target_path in targets:
        print(f"--- Target: {target_path.name} ---")
        with open(target_path, "r") as f:
            original_code = f.read()

        for intensity in intensities:
            print(f"  Intensity Level {intensity}")
            
            # Setup Mutator based on intensity
            # Level 1: Rename only
            # Level 2: Rename + Strip comments
            mutator = Mutator(seed=seed, intensity=intensity)
            
            mutated_code = mutator.mutate_source(original_code)
            
            for provider_name in providers:
                print(f"    Provider: {provider_name}")
                try:
                    provider = get_provider(provider_name)
                    
                    prompt = f"""Analyze the following Python code. Identify which popular open-source library this is derived from. 
If you are certain, name the library. If you are unsure, provide your best guess.

Code:
```python
{mutated_code}
```
"""
                    response = provider.ask(prompt)
                    print(f"      Response: {response[:100]}...")
                    
                    results.append({
                        "target": target_path.name,
                        "intensity": intensity,
                        "provider": provider_name,
                        "response": response
                    })
                except Exception as e:
                    print(f"      Error with {provider_name}: {e}")

    # Summary report
    print("\n=== Benchmark Results Summary ===")
    for res in results:
        print(f"{res['target']} | Level {res['intensity']} | {res['provider']} | {res['response'][:50].replace('\n', ' ')}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run de-anonymization benchmark")
    parser.add_argument("--targets-dir", type=Path, required=True, help="Directory containing target code snippets")
    parser.add_argument("--providers", nargs="+", default=["openai"], help="LLM providers to test")
    parser.add_argument("--intensities", nargs="+", type=int, default=[1, 2], help="Mutation intensity levels")
    parser.add_argument("--seed", type=int, default=42, help="Random seed")

    args = parser.parse_args()

    if not args.targets_dir.exists():
        print(f"Error: Targets directory {args.targets_dir} not found")
        sys.exit(1)

    targets = list(args.targets_dir.glob("*.py"))
    if not targets:
        print(f"No .py files found in {args.targets_dir}")
        sys.exit(1)

    run_benchmark(targets, args.providers, args.intensities, args.seed)
