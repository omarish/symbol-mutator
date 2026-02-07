import argparse
import os
import sys
from pathlib import Path
import asyncio
from typing import List, Dict

from dotenv import load_dotenv
from .core import Mutator
from .llm import get_provider

async def run_benchmark(
    targets: List[Path],
    providers: List[str],
    intensities: List[int],
    seed: int = 42,
    max_concurrency: int = 5
):
    load_dotenv()
    
    results = []
    semaphore = asyncio.Semaphore(max_concurrency)

    async def run_single_test(target_path: Path, intensity: int, provider_name: str, original_code: str):
        async with semaphore:
            print(f"  Testing {target_path.name} | Intensity {intensity} | Provider {provider_name}")
            try:
                # Setup Mutator based on intensity
                mutator = Mutator(seed=seed, intensity=intensity)
                mutated_code = mutator.mutate_source(original_code)
                
                provider = get_provider(provider_name)
                
                prompt = f"""Analyze the following Python code. Identify which popular open-source library this is derived from. 
If you are certain, name the library. If you are unsure, provide your best guess.

Code:
```python
{mutated_code}
```
"""
                response = await provider.ask_async(prompt)
                
                return {
                    "target": target_path.name,
                    "intensity": intensity,
                    "provider": provider_name,
                    "response": response
                }
            except Exception as e:
                print(f"      Error with {target_path.name} / {provider_name}: {e}")
                return None

    tasks = []
    for target_path in targets:
        with open(target_path, "r") as f:
            original_code = f.read()
        
        for intensity in intensities:
            for provider_name in providers:
                tasks.append(run_single_test(target_path, intensity, provider_name, original_code))

    print(f"--- Starting benchmark with {len(tasks)} tasks ---")
    all_results = await asyncio.gather(*tasks)
    results = [r for r in all_results if r is not None]

    # Summary report
    print("\n=== Benchmark Results Summary ===")
    for res in results:
        print(f"{res['target']} | Level {res['intensity']} | {res['provider']} | {res['response'][:50].replace('\n', ' ')}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run de-anonymization benchmark")
    parser.add_argument("--targets-dir", type=Path, required=True, help="Directory containing target code snippets")
    parser.add_argument("--providers", nargs="+", default=["openai"], help="LLM providers to test")
    parser.add_argument("--intensities", nargs="+", type=int, default=[1, 2, 3, 4, 5], help="Mutation intensity levels")
    parser.add_argument("--seed", type=int, default=42, help="Random seed")

    args = parser.parse_args()

    if not args.targets_dir.exists():
        print(f"Error: Targets directory {args.targets_dir} not found")
        sys.exit(1)

    targets = list(args.targets_dir.glob("*.py"))
    if not targets:
        print(f"No .py files found in {args.targets_dir}")
        sys.exit(1)

    asyncio.run(run_benchmark(targets, args.providers, args.intensities, args.seed))
