"""CLI tool for managing word puzzle data."""

import argparse
import json
import sys
from datetime import date

from src.repo import puzzle_repo
from src.service import game_service


def main() -> int:
    """CLI entrypoint."""
    parser = argparse.ArgumentParser(description="Word Puzzle Manager")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Generate puzzle command
    gen_parser = subparsers.add_parser("generate", help="Generate a new puzzle")
    gen_parser.add_argument("--date", required=True, help="Puzzle date (YYYY-MM-DD)")
    gen_parser.add_argument("--words", required=True, help="Comma-separated words")
    gen_parser.add_argument("--categories", required=True, help="Categories JSON")

    # List puzzles command
    subparsers.add_parser("list", help="List all puzzles")

    # Show puzzle command
    show_parser = subparsers.add_parser("show", help="Show a puzzle")
    show_parser.add_argument("--date", required=True, help="Puzzle date (YYYY-MM-DD)")

    args = parser.parse_args()

    if args.command == "generate":
        words = [w.strip() for w in args.words.split(",")]
        categories = json.loads(args.categories)

        if len(words) != 16:
            print("Error: Must have exactly 16 words")
            return 1

        if len(categories) != 4:
            print("Error: Must have exactly 4 categories")
            return 1

        for cat in categories:
            if len(cat["words"]) != 4:
                print(f"Error: Category '{cat['name']}' must have 4 words")
                return 1

        puzzle = game_service.create_puzzle(args.date, words, categories)
        game_service.save_puzzle(args.date, puzzle)
        print(f"Generated puzzle for {args.date}")
        return 0

    elif args.command == "list":
        import os
        from pathlib import Path

        puzzles_dir = Path("puzzles")
        if not puzzles_dir.exists():
            print("No puzzles directory found")
            return 0

        puzzles = sorted(puzzles_dir.glob("*.json"))
        if not puzzles:
            print("No puzzles found")
            return 0

        for p in puzzles:
            print(f"- {p.stem}")
        return 0

    elif args.command == "show":
        puzzle = game_service.load_puzzle(args.date)
        print(f"Puzzle for {args.date}:")
        for cat in puzzle.categories:
            words = ", ".join(w.text for w in cat.words)
            print(f"  {cat.name}: {words}")
        return 0

    else:
        parser.print_help()
        return 1


if __name__ == "__main__":
    sys.exit(main())
