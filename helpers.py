# helpers.py
"""
Helper functions for game operations.
Utility functions to keep game logic clean and maintainable.
"""

from time import monotonic
from typing import Tuple

from constants import GameSettings, GameState


class TimeHelper:
  """Helper class for time-related operations."""

  @staticmethod
  def format_game_time(seconds: float) -> str:
      """
      Formats game time in seconds to MM:SS.ff format.
      
      Args:
          seconds: Time in seconds (can be float)
          
      Returns:
          Formatted time string (e.g., "05:23.45")
      """
      minutes = int(seconds // 60)
      remaining_seconds = seconds % 60
      return GameSettings.TIME_FORMAT_PATTERN.format(
          minutes=minutes, seconds=remaining_seconds
      )

  @staticmethod
  def calculate_current_time(
      state: GameState, total_time: float, gametime: float
  ) -> float:
      """
      Calculates the current game time based on state.
      
      Args:
          state: Current game state
          total_time: Accumulated game time
          gametime: Start time of current segment
          
      Returns:
          Current game time in seconds
      """
      if state == GameState.RUNNING:
          return total_time + (monotonic() - gametime)
      return total_time

  @staticmethod
  def get_time_display(state: GameState, current_time: float) -> str:
      """
      Gets the display string for game time based on state.
      
      Args:
          state: Current game state
          current_time: Current game time in seconds
          
      Returns:
          Formatted time display string
      """
      if state == GameState.ENDED:
          return GameSettings.TIME_FORMAT_FULL_TIME
      return TimeHelper.format_game_time(current_time)


class PlayerHelper:
  """Helper class for player-related operations."""

  @staticmethod
  def get_player_name(player: str | None) -> str:
      """
      Returns player name or default unknown player name.
      
      Args:
          player: Player name or None
          
      Returns:
          Player name or "Unknown"
      """
      return player if player is not None else GameSettings.UNKNOWN_PLAYER_NAME

  @staticmethod
  def update_player_score(
      players_dict: dict[str, dict[str, int]], player: str | None, points: int
  ) -> None:
      """
      Updates player's score if player exists in dictionary.
      
      Args:
          players_dict: Dictionary of players
          player: Player name
          points: Points to add
      """
      if player is not None and player in players_dict:
          players_dict[player]["score"] += points


class ScoreHelper:
  """Helper class for score-related operations."""

  @staticmethod
  def create_timeline_entry(
      time_str: str, team_type: str, player_name: str, points: int
  ) -> Tuple[str, str, str, int]:
      """
      Creates a timeline entry tuple.
      
      Args:
          time_str: Formatted time string
          team_type: "Home" or "Away"
          player_name: Player's name
          points: Points scored
          
      Returns:
          Timeline entry tuple
      """
      return (time_str, team_type, player_name, points)


def format_time(seconds: float) -> str:
  """Shorthand for TimeHelper.format_game_time()"""
  return TimeHelper.format_game_time(seconds)


def get_player_name(player: str | None) -> str:
  """Shorthand for PlayerHelper.get_player_name()"""
  return PlayerHelper.get_player_name(player)