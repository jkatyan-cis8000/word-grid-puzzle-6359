"""Package init for providers random."""

import random

from src.types import Word


class RandomProvider:
    """Cross-cutting random number provider.

    Allows mocking for tests while keeping random logic centralized.
    """

    def shuffle_words(self, words: list[Word]) -> list[Word]:
        """Shuffle a list of words."""
        shuffled = words.copy()
        random.shuffle(shuffled)
        return shuffled
