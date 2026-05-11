"""Main entrypoint for the word puzzle game."""

import sys
from datetime import date

from src.config import PUZZLES_DIR, COMMAND_SHUFFLE, COMMAND_SOLVE, COMMAND_QUIT
from src.repo import puzzle_repo
from src.runtime import runtime
from src.types import Puzzle
from src.ui import cli


def main() -> int:
    """Main game loop."""
    try:
        # Initialize
        runtime.initialize()
        puzzle = runtime.get_ui_puzzle()

        cli.display_welcome()

        # Game loop
        game_continues = True
        while game_continues:
            cli.display_grid(puzzle)
            cli.display_found_groups(runtime.get_game_state().groups_found)
            cli.display_status(runtime.get_game_state().mistakes)

            user_input = cli.get_user_input()

            # Check for commands
            if user_input.lower() in (COMMAND_SHUFFLE, COMMAND_SOLVE, COMMAND_QUIT):
                game_continues, message = runtime.process_command(user_input)
                cli.display_message(message)
                if not game_continues:
                    break
                # Refresh grid after shuffle
                if user_input.lower() == COMMAND_SHUFFLE:
                    puzzle = runtime.get_ui_puzzle()
                    continue

            # Process guess
            try:
                guess_words = cli.parse_guess(user_input)
            except ValueError as e:
                cli.display_message(f"Error: {e}")
                continue

            game_continues, message = runtime.process_user_guess(guess_words)
            is_correct = "Correct" in message
            cli.display_result(is_correct, message)

        # Game ended - show final state
        if runtime.get_game_state().mistakes < 4:
            cli.display_found_groups(runtime.get_game_state().groups_found)

        cli.display_goodbye()
        return 0

    except KeyboardInterrupt:
        cli.display_goodbye()
        return 0
    except RuntimeError as e:
        print(f"Error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
