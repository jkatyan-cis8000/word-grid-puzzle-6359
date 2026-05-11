"""Game service layer - business logic for the word puzzle."""

from datetime import date

from src.types import Puzzle, Category, Word, GameState, GameStatus, FoundGroup


class GameService:
    """Business logic for the word puzzle game."""

    def create_puzzle(
        self, puzzle_date: str, words: list[str], categories: list[dict]
    ) -> Puzzle:
        """Create a puzzle from raw data.

        Args:
            puzzle_date: Date string (YYYY-MM-DD)
            words: List of 16 word strings
            categories: List of dicts with 'name' and 'words' keys

        Returns:
            A Puzzle instance
        """
        if len(words) != 16:
            raise ValueError("Exactly 16 words required")

        if len(categories) != 4:
            raise ValueError("Exactly 4 categories required")

        # Validate each category has 4 words
        for cat in categories:
            if len(cat["words"]) != 4:
                raise ValueError(f"Category '{cat['name']}' must have 4 words")

        # Create Word objects
        word_objs = [Word(text=w) for w in words]

        # Create Category objects
        category_objs = []
        for cat in categories:
            cat_words = [Word(text=w) for w in cat["words"]]
            category_objs.append(Category(name=cat["name"], words=cat_words))

        return Puzzle(
            id=puzzle_date,
            date=puzzle_date,
            categories=category_objs,
            words=word_objs,
        )

    def save_puzzle(self, puzzle_date: str, puzzle: Puzzle) -> None:
        """Save a puzzle to storage."""
        from src.repo.persistence import puzzle_repo
        from datetime import date as dt
        puzzle_repo.save_daily_puzzle(dt.fromisoformat(puzzle_date), puzzle)

    def load_puzzle(self, puzzle_date: str) -> Puzzle:
        """Load a puzzle from storage."""
        from src.repo.persistence import puzzle_repo
        from datetime import date as dt
        return puzzle_repo.load_daily_puzzle(dt.fromisoformat(puzzle_date))

    def check_guess(self, puzzle: Puzzle, words: list[str]) -> str | None:
        """Check if a guess forms a valid category.

        Args:
            puzzle: The puzzle to check against
            words: List of 4 word strings (case-insensitive)

        Returns:
            Category name if correct, None if incorrect
        """
        word_set = set(w.lower() for w in words)

        for category in puzzle.categories:
            cat_words = set(w.text.lower() for w in category.words)
            if word_set == cat_words:
                return category.name

        return None

    def process_guess(
        self, puzzle: Puzzle, state: GameState, words: list[str]
    ) -> tuple[bool, str]:
        """Process a user's guess.

        Returns:
            Tuple of (game_continues, message)
        """
        if len(words) != 4:
            return True, "Guess must contain exactly 4 words."

        # Check if words exist in puzzle
        puzzle_word_texts = {w.text.lower() for w in puzzle.words}
        for w in words:
            if w.lower() not in puzzle_word_texts:
                return True, f"Word '{w}' not in puzzle."

        # Check if words already used
        used_words = set()
        for group in state.groups_found:
            used_words.update(w.lower() for w in group.words)
        for w in words:
            if w.lower() in used_words:
                return True, f"Word '{w}' already used in a group."

        # Validate the category
        category_name = self.check_guess(puzzle, words)

        if category_name:
            new_group = FoundGroup(category=category_name, words=tuple(words))
            new_state = state.add_group(new_group)
            return True, f"Correct! You found: {category_name}."
        else:
            new_mistakes = state.mistakes + 1
            new_state = state.replace(mistakes=new_mistakes)
            return True, "Incorrect."

    def is_game_won(self, state: GameState, total_categories: int) -> bool:
        """Check if the game has been won."""
        return len(state.groups_found) == total_categories

    def is_game_over(self, state: GameState, max_mistakes: int) -> bool:
        """Check if the game is over due to too many mistakes."""
        return state.mistakes >= max_mistakes
