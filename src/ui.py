"""UI layer - CLI interface.

Handles all user interaction: displaying the grid, reading input,
and showing messages.
"""

from typing import List

from src.config import GRID_SIZE, WORDS_PER_GRID
from src.types import Puzzle, GameState, FoundGroup


def display_welcome() -> None:
    """Display welcome message."""
    print("\n" + "=" * 50)
    print("       WORD GRID PUZZLE")
    print("=" * 50)
    print("Find 4 groups of 4 related words.")
    print(f"Commands: '{_format_cmd('shuffle')}', '{_format_cmd('solve')}', '{_format_cmd('quit')}'")
    print("=" * 50 + "\n")


def display_grid(puzzle: Puzzle) -> None:
    """Display the 4x4 grid of words."""
    words = [w.text for w in puzzle.words]
    # Chunk into rows
    rows = _chunk_list(words, GRID_SIZE)
    for row in rows:
        # Pad to uniform width
        padded = [w.ljust(12) for w in row]
        print("  " + "  ".join(padded))
    print()


def display_found_groups(groups: List[FoundGroup]) -> None:
    """Display found groups with their categories."""
    if not groups:
        return

    print("Found groups:")
    for group in groups:
        words_str = ", ".join(group.words)
        print(f"  {group.category}: {words_str}")
    print()


def display_status(mistakes: int) -> None:
    """Display current mistake count."""
    print(f"Mistakes: {mistakes} / 4")
    print()


def get_user_input() -> str:
    """Get user input from CLI."""
    return input("Enter 4 words (or command): ")


def parse_guess(user_input: str) -> List[str]:
    """Parse user input into list of words."""
    parts = user_input.strip().split()
    words = [w.strip().lower() for w in parts if w.strip()]
    if len(words) != 4:
        raise ValueError(f"Expected 4 words, got {len(words)}")
    return words


def display_result(is_game_continues: bool, message: str) -> None:
    """Display result of a guess."""
    print(f"  {message}")
    if not is_game_continues:
        print()
    else:
        print()


def display_message(message: str) -> None:
    """Display a generic message."""
    print(f"  {message}")
    print()


def display_goodbye() -> None:
    """Display goodbye message."""
    print("\nThanks for playing!\n")


def _format_cmd(cmd: str) -> str:
    """Format command for display."""
    return cmd


def _chunk_list(items: list, chunk_size: int) -> list:
    """Split list into chunks of given size."""
    return [items[i:i + chunk_size] for i in range(0, len(items), chunk_size)]
