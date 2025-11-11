from typing import List
from game import Game


class Cup:
    """A container for a collection of games (e.g., a tournament)."""

    def __init__(self) -> None:
        self.games: List[Game] = []

    def __str__(self) -> str:
        """Returns the string representation of the Cup."""
        return "Cup Tournament"
