# constants.py
"""
Game constants and messages.
Centralized location for all game-related constant values and messages.
"""
from enum import Enum, auto
from typing import Final

# ========== ENUMS ==========

class GameState(Enum):
    """Enum for game states to prevent bugs from using invalid state strings."""

    READY = auto()
    RUNNING = auto()
    PAUSED = auto()
    ENDED = auto()

# ========== GAME MESSAGES ==========

class GameMessages:
  """All game-related messages."""
    
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
      """Returns formatted score message."""
      return f"{team_name} scored {points} points."


# ========== GAME SETTINGS ==========

class GameSettings:
  """Game configuration settings."""
  
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
  """Team-related messages."""
  
  @staticmethod
  def player_not_found(player_name: str) -> str:
      """Returns player not found warning."""
      return f"Warning: Player '{player_name}' not found."
  
  @staticmethod
  def setting_attribute(key: str, value: str) -> str:
      """Returns attribute setting message."""
      return f"Setting generic attribute {key} to {value}"


# ========== EXPORT ==========
__all__ = [
  "GameState",
  "GameMessages",
  "GameSettings",
  "TeamMessages",
]