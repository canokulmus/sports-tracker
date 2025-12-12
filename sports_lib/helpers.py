# helpers.py
"""Provides helper classes to encapsulate and simplify common game logic.

These helpers manage concerns like time formatting, player data, and score
tracking, keeping the main Game class cleaner and more focused on state
management.
"""

from time import monotonic
from typing import Tuple

from .constants import GameSettings, GameState


class TimeHelper:
    """A collection of static methods for time-related calculations."""

    @staticmethod
    def format_game_time(seconds: float) -> str:
        """Formats a duration in seconds into a MM:SS.ff string."""
        minutes = int(seconds // 60)
        remaining_seconds = seconds % 60
        return GameSettings.TIME_FORMAT_PATTERN.format(
            minutes=minutes, seconds=remaining_seconds
        )

    @staticmethod
    def calculate_current_time(
        state: GameState, total_time: float, gametime: float
    ) -> float:
        """Calculates the elapsed game time based on the current game state."""
        if state == GameState.RUNNING:
            return total_time + (monotonic() - gametime)
        return total_time

    @staticmethod
    def get_time_display(state: GameState, current_time: float) -> str:
        """Returns the appropriate time string for display.

        This will be 'Full Time' if the game has ended, otherwise it returns
        the formatted current time.
        """
        if state == GameState.ENDED:
            return GameSettings.TIME_FORMAT_FULL_TIME
        return TimeHelper.format_game_time(current_time)


class PlayerHelper:
    """Helper class for player-related operations."""

    """A collection of static methods for player-related logic."""

    @staticmethod
    def get_player_name(player: str | None) -> str:
        """Returns the player's name or a default if the name is not provided."""
        return player if player is not None else GameSettings.UNKNOWN_PLAYER_NAME

    @staticmethod
    def update_player_score(
        players_dict: dict[str, dict[str, int]], player: str | None, points: int
    ) -> None:
        """Adds points to a player's score within the provided dictionary."""
        if player is not None and player in players_dict:
            players_dict[player]["score"] += points


class ScoreHelper:
    """A collection of static methods for score-related logic."""

    @staticmethod
    def create_timeline_entry(
        time_str: str, team_type: str, player_name: str, points: int
    ) -> Tuple[str, str, str, int]:
        """Constructs a standardized tuple for a timeline event."""
        return (time_str, team_type, player_name, points)
