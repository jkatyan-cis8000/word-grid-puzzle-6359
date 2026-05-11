"""Runtime layer - application orchestration and dependency wiring.

This layer ties together all other layers to run the game.
It manages game state, processes commands, and coordinates between UI and business logic.
"""

from datetime import date
from typing import Tuple

from src.config import MAX_MISTAKES, COMMAND_SHUFFLE, COMMAND_SOLVE, COMMAND_QUIT
from src.providers import random_provider
from src.repo import puzzle_repo
from src.service import game_service
from src.types import GameState, GameStatus


class GameRuntime:
    """Orchestrates the game flow and manages runtime state."""

    def __init__(self):
        self._current_puzzle = None
        self._game_state = None
        self._today = date.today()

    def initialize(self) -> None:
        """Initialize the game: load today's puzzle and setup game state."""
        self._current_puzzle = puzzle_repo.load_daily_puzzle(self._today)
        self._game_state = GameState(
            mistakes=0,
            groups_found=[],
            status=GameStatus.PLAYING,
        )

    def get_ui_puzzle(self):
        """Get puzzle with shuffled grid for UI display."""
        if self._current_puzzle is None:
            raise RuntimeError("Game not initialized. Call initialize() first.")
        words = random_provider.shuffle_words(self._current_puzzle.words)
        return self._current_puzzle.replace(words=words)

    def get_game_state(self) -> GameState:
        """Get current game state."""
        if self._game_state is None:
            raise RuntimeError("Game not initialized. Call initialize() first.")
        return self._game_state

    def process_user_guess(
        self, words: list[str]
    ) -> Tuple[bool, str]:
        """Process a user's guess of 4 words forming a category."""
        if self._game_state is None:
            raise RuntimeError("Game not initialized. Call initialize() first.")

        if len(words) != 4:
            return True, "Guess must contain exactly 4 words."

        # Check if words exist in puzzle
        puzzle_word_texts = {w.text for w in self._current_puzzle.words}
        for w in words:
            if w not in puzzle_word_texts:
                return True, f"Word '{w}' not in puzzle."

        # Check if words already used
        used_words = set()
        for group in self._game_state.groups_found:
            used_words.update(group.words)
        for w in words:
            if w in used_words:
                return True, f"Word '{w}' already used in a group."

        # Validate the category
        category_name = game_service.check_guess(self._current_puzzle, words)

        if category_name:
            # Correct guess
            from src.types import FoundGroup
            new_group = FoundGroup(category=category_name, words=tuple(words))
            self._game_state = self._game_state.add_group(new_group)

            if game_service.is_game_won(self._game_state, len(self._current_puzzle.categories)):
                self._game_state = self._game_state.replace(status=GameStatus.WON)
                return False, f"Correct! You found: {category_name}. You won!"

            return True, f"Correct! You found: {category_name}."
        else:
            # Incorrect guess
            self._game_state = self._game_state.replace(mistakes=self._game_state.mistakes + 1)

            if game_service.is_game_over(self._game_state, MAX_MISTAKES):
                self._game_state = self._game_state.replace(status=GameStatus.LOST)
                return False, "Incorrect. 4 mistakes - game over!"

            return True, "Incorrect."

    def process_command(self, command: str) -> Tuple[bool, str]:
        """Process a command (shuffle, solve, quit)."""
        if self._game_state is None:
            raise RuntimeError("Game not initialized. Call initialize() first.")

        cmd = command.lower().strip()

        if cmd == COMMAND_SHUFFLE:
            # Shuffle the grid, keep same puzzle
            self._current_puzzle = self._current_puzzle.replace(
                words=random_provider.shuffle_words(self._current_puzzle.words)
            )
            return True, "Grid shuffled."

        elif cmd == COMMAND_SOLVE:
            # Reveal all categories
            self._game_state = self._game_state.replace(status=GameStatus.SOLVED)
            return False, "Puzzle solved."

        elif cmd == COMMAND_QUIT:
            return False, "Quit."

        else:
            return True, f"Unknown command: {command}"


# Global singleton instance
runtime = GameRuntime()
