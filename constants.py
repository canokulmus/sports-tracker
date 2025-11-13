# constants.py
"""Defines centralized constants and messages for the application.

Using a dedicated module for constants avoids magic strings and numbers,
improving maintainability and readability across the codebase.
"""

from enum import Enum, auto
from typing import Final

# ========== ENUMS ==========


class GameState(Enum):
    """Represents the lifecycle states of a game."""

    READY = auto()
    RUNNING = auto()
    PAUSED = auto()
    ENDED = auto()


class CupType:
    """Defines the available tournament formats."""

    LEAGUE = "LEAGUE"
    LEAGUE2 = "LEAGUE2"
    ELIMINATION = "ELIMINATION"
    ELIMINATION2 = "ELIMINATION2"
    GROUP = "GROUP"
    GROUP2 = "GROUP2"


# ========== GAME MESSAGES ==========


class GameMessages:
    """A container for all user-facing game-related messages."""

    # Start messages
    GAME_STARTED: Final[str] = "Game started"
    GAME_ALREADY_RUNNING: Final[str] = "Game is already running."
    GAME_PAUSED_USE_RESUME: Final[str] = "Game is paused. Use resume() to continue."
    GAME_ALREADY_ENDED: Final[str] = "Game is already ended."
    GAME_NOT_STARTED: Final[str] = "Game has not started yet. Use start()."

    # Pause messages
    GAME_PAUSED: Final[str] = "Game paused"
    GAME_ALREADY_PAUSED: Final[str] = "Game is already paused."
    GAME_NOT_RUNNING: Final[str] = "Game is not running."

    # Resume messages
    GAME_RESUMED: Final[str] = "Game resumed"

    # End messages
    GAME_ENDED: Final[str] = "Game has ended."

    # Score messages
    CANNOT_SCORE_NOT_RUNNING: Final[str] = "Cannot score, game is not running."

    @staticmethod
    def team_scored(team_name: str, points: int) -> str:
        """Generates a message for a team scoring points."""
        return f"{team_name} scored {points} points."


# ========== GAME SETTINGS ==========


class GameSettings:
    """Defines default settings and configurations for game mechanics."""

    # Time format
    TIME_FORMAT_FULL_TIME: Final[str] = "Full Time"
    TIME_FORMAT_PATTERN: Final[str] = "{minutes:02d}:{seconds:05.2f}"

    # Default values
    DEFAULT_SCORE: Final[int] = 0
    DEFAULT_TIME: Final[float] = 0.0

    # Player settings
    UNKNOWN_PLAYER_NAME: Final[str] = "Unknown"


# ========== TEAM MESSAGES ==========


class TeamMessages:
    """A container for all user-facing team-related messages."""

    @staticmethod
    def player_not_found(player_name: str) -> str:
        """Generates a warning for a non-existent player."""
        return f"Warning: Player '{player_name}' not found."

    @staticmethod
    def setting_attribute(key: str, value: str) -> str:
        """Generates a message for setting a generic attribute."""
        return f"Setting generic attribute {key} to {value}"


# ========== EXPORT ==========
__all__ = [
    "GameState",
    "GameMessages",
    "GameSettings",
    "TeamMessages",
]
