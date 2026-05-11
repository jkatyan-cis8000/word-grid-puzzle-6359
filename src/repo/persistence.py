"""Package init for repo persistence."""

import json
from pathlib import Path
from datetime import date

from src.repo.schemas import PuzzleSchema
from src.types import Puzzle


class PuzzleRepo:
    """Daily puzzle persistence using JSON files."""

    def __init__(self, puzzles_dir: str = "puzzles"):
        self._base_dir = Path(puzzles_dir)

    def save_daily_puzzle(self, puzzle_date: date, puzzle: Puzzle) -> None:
        """Save a puzzle for a specific date."""
        filename = self._base_dir / f"{puzzle_date.isoformat()}.json"
        self._base_dir.mkdir(parents=True, exist_ok=True)

        schema = PuzzleSchema.from_puzzle(puzzle)
        with open(filename, "w") as f:
            json.dump(schema.to_dict(), f, indent=2)

    def load_daily_puzzle(self, puzzle_date: date) -> Puzzle:
        """Load a puzzle for a specific date."""
        filename = self._base_dir / f"{puzzle_date.isoformat()}.json"

        if not filename.exists():
            # Create default puzzle for today
            from src.service.game import GameService
            from src.types import Category

            words = [
                "apple", "banana", "cherry", "date", "elder", "fig", "grape", "honey",
                "kiwi", "lemon", "mango", "nectar", "orange", "papaya", "quince", "raisin"
            ]
            categories = [
                Category(name="FRUITS", words=["apple", "banana", "cherry", "date"]),
                Category(name="FRUITS2", words=["elder", "fig", "grape", "honey"]),
                Category(name="FRUITS3", words=["kiwi", "lemon", "mango", "nectar"]),
                Category(name="FRUITS4", words=["orange", "papaya", "quince", "raisin"]),
            ]

            game_service = GameService()
            puzzle = game_service.create_puzzle(puzzle_date.isoformat(), words, categories)
            self.save_daily_puzzle(puzzle_date, puzzle)
            return puzzle

        with open(filename) as f:
            data = json.load(f)

        schema = PuzzleSchema.from_dict(data)
        return schema.to_puzzle()


# Global singleton instance
puzzle_repo = PuzzleRepo()
