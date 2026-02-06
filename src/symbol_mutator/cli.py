import argparse
import sys
from pathlib import Path

from .core import Mutator


def main():
    parser = argparse.ArgumentParser(description="Deterministically obfuscate a Python codebase.")
    parser.add_argument("--target", type=Path, required=True, help="Path to the library to mutate")
    parser.add_argument(
        "--output", type=Path, required=True, help="Directory to save the mutated library"
    )
    parser.add_argument(
        "--seed", type=int, default=42, help="Random seed for deterministic renaming"
    )
    parser.add_argument(
        "--theme", choices=["gibberish", "fantasy"], default="gibberish", help="Naming theme"
    )
    parser.add_argument(
        "--internal-prefix",
        action="append",
        help="Prefix of internal modules (e.g. 'flask') to allow renaming import targets.",
    )

    args = parser.parse_args()

    if not args.target.exists():
        print(f"Error: Target path {args.target} does not exist.")
        sys.exit(1)

    mutator = Mutator(seed=args.seed, theme=args.theme, internal_prefixes=args.internal_prefix)

    if args.target.is_file():
        # Single file case
        print(f"Mutating single file: {args.target}")
        with open(args.target) as f:
            code = f.read()

        mutated_code = mutator.mutate_source(code)

        args.output.parent.mkdir(parents=True, exist_ok=True)
        with open(args.output, "w") as f:
            f.write(mutated_code)
        print(f"Written mutated file to {args.output}")

    elif args.target.is_dir():
        print(f"Mutating directory: {args.target}")
        from .core import mutate_directory

        mutate_directory(args.target, args.output, mutator=mutator)

        print(f"Mutation complete. Mapped {len(mutator.mapping)} symbols.")


if __name__ == "__main__":
    main()
