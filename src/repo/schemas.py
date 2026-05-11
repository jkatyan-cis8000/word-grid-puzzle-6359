"""Package init for repo schemas."""

import json
from dataclasses import dataclass
from typing import List, Dict, Any

from src.types import Puzzle, Category as CategoryType, Word as WordType


@dataclass
class WordSchema:
    """Schema for word serialization."""
    text: str

    @classmethod
    def from_word(cls, word: WordType) -> "WordSchema":
        return cls(text=word.text)

    def to_word(self) -> WordType:
        return WordType(text=self.text)


@dataclass
class CategorySchema:
    """Schema for category serialization."""
    name: str
    words: List[str]

    @classmethod
    def from_category(cls, category: CategoryType) -> "CategorySchema":
        words = [w.text for w in category.words]
        return cls(name=category.name, words=words)

    def to_category(self) -> CategoryType:
        words = [WordType(text=w) for w in self.words]
        return CategoryType(name=self.name, words=words)


@dataclass
class PuzzleSchema:
    """Schema for puzzle serialization."""
    id: str
    date: str
    categories: List[Dict[str, Any]]
    words: List[str]

    @classmethod
    def from_puzzle(cls, puzzle: Puzzle) -> "PuzzleSchema":
        categories = []
        for cat in puzzle.categories:
            words = [w.text for w in cat.words]
            categories.append({"name": cat.name, "words": words})
        word_texts = [w.text for w in puzzle.words]
        return cls(
            id=puzzle.id,
            date=puzzle.date,
            categories=categories,
            words=word_texts,
        )

    def to_puzzle(self) -> Puzzle:
        from src.types import Puzzle as PuzzleType
        categories = []
        for cat_data in self.categories:
            words = [WordType(text=w) for w in cat_data["words"]]
            categories.append(CategoryType(name=cat_data["name"], words=words))
        word_objs = [WordType(text=w) for w in self.words]
        return PuzzleType(
            id=self.id,
            date=self.date,
            categories=categories,
            words=word_objs,
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "date": self.date,
            "categories": self.categories,
            "words": self.words,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "PuzzleSchema":
        return cls(
            id=data["id"],
            date=data["date"],
            categories=data["categories"],
            words=data["words"],
        )
