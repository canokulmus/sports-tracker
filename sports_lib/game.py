from datetime import datetime
from time import monotonic
from typing import Any, Dict, List, Tuple, Optional

from .team import Team
from .constants import GameState, GameSettings
from .helpers import TimeHelper, PlayerHelper, ScoreHelper


class Game:
    """Manages the state and logic of a single game between two teams.

    Refactored for Phase 3:
    - Removed Observer pattern (watch/unwatch).
    - Removed print statements (statelessness).
    - Added exception handling for invalid state transitions.
    """

    def __init__(
        self,
        home: Team,
        away: Team,
        id_: int,
        datetime: datetime,
        state: GameState = GameState.READY,
        group: Optional[str] = None,
    ) -> None:
        self.home_ = home
        self.away_ = away
        self.id_ = id_
        self.datetime = datetime
        self.state = state
        self.group = group

        self.total_time = GameSettings.DEFAULT_TIME
        self.gametime = GameSettings.DEFAULT_TIME

        self.home_score = GameSettings.DEFAULT_SCORE
        self.away_score = GameSettings.DEFAULT_SCORE

        self.home_players = {
            name: {"no": data["no"], "score": GameSettings.DEFAULT_SCORE}
            for name, data in home.players.items()
        }
        self.away_players = {
            name: {"no": data["no"], "score": GameSettings.DEFAULT_SCORE}
            for name, data in away.players.items()
        }

        self.timeline: List[Tuple[str, str, str, int]] = []

    def __str__(self) -> str:
        """Returns the string representation of the Game."""
        return f"Game: {self.home().team_name} vs {self.away().team_name}"

    def id(self) -> int:
        """Returns the unique identifier for the game."""
        return self.id_

    def home(self) -> Team:
        """Returns the home team object."""
        return self.home_

    def away(self) -> Team:
        """Returns the away team object."""
        return self.away_

    def start(self) -> None:
        """Transitions the game from READY to RUNNING state.

        Raises:
            ValueError: If the game is not in the READY state.
        """
        if self.state == GameState.READY:
            self.state = GameState.RUNNING
            self.gametime = monotonic()
        else:
            if self.state == GameState.RUNNING:
                raise ValueError("Game is already running.")
            elif self.state == GameState.PAUSED:
                raise ValueError("Game is paused. Use resume() to continue.")
            elif self.state == GameState.ENDED:
                raise ValueError("Game is already ended.")
            else:
                raise ValueError(f"Cannot start game in state {self.state}")

    def pause(self) -> None:
        """Transitions the game from RUNNING to PAUSED state.

        Raises:
            ValueError: If the game is not RUNNING.
        """
        if self.state == GameState.RUNNING:
            self.total_time += monotonic() - self.gametime
            self.state = GameState.PAUSED
        else:
            if self.state == GameState.PAUSED:
                raise ValueError("Game is already paused.")
            elif self.state == GameState.ENDED:
                raise ValueError("Game is already ended.")
            else:
                raise ValueError("Cannot pause: Game is not running.")

    def resume(self) -> None:
        """Transitions the game from PAUSED back to RUNNING state.

        Raises:
            ValueError: If the game is not PAUSED.
        """
        if self.state == GameState.PAUSED:
            self.state = GameState.RUNNING
            self.gametime = monotonic()
        else:
            if self.state == GameState.RUNNING:
                raise ValueError("Game is already running.")
            elif self.state == GameState.READY:
                raise ValueError("Game has not started yet.")
            else:
                raise ValueError("Game is already ended.")

    def end(self) -> None:
        """Transitions the game to the ENDED state, finalizing the time.

        Raises:
            ValueError: If the game is already ENDED.
        """
        if self.state == GameState.ENDED:
            raise ValueError("Game is already ended.")

        if self.state == GameState.RUNNING:
            self.total_time += monotonic() - self.gametime

        self.state = GameState.ENDED

    def score(self, points: int, team: Team, player: Optional[str] = None) -> None:
        """Records a score for a team and optionally a player.

        Raises:
            ValueError: If the game is not RUNNING or the team is invalid.
        """
        if self.state != GameState.RUNNING:
            raise ValueError("Cannot score, game is not running.")

        current_time = TimeHelper.calculate_current_time(
            self.state, self.total_time, self.gametime
        )
        time_str = TimeHelper.format_game_time(current_time)
        player_name = PlayerHelper.get_player_name(player)

        if team == self.home_:
            self._score_for_team(
                team_type="Home",
                points=points,
                time_str=time_str,
                player=player,
                player_name=player_name,
                players_dict=self.home_players,
            )
            self.home_score += points

        elif team == self.away_:
            self._score_for_team(
                team_type="Away",
                points=points,
                time_str=time_str,
                player=player,
                player_name=player_name,
                players_dict=self.away_players,
            )
            self.away_score += points
        else:
            raise ValueError(
                f"Team '{team.team_name}' is not participating in this game."
            )

    def _score_for_team(
        self,
        team_type: str,
        points: int,
        time_str: str,
        player: Optional[str],
        player_name: str,
        players_dict: Dict[str, Dict[str, int]],
    ) -> None:
        """Internal helper to encapsulate the logic of recording a score."""
        timeline_entry = ScoreHelper.create_timeline_entry(
            time_str, team_type, player_name, points
        )
        self.timeline.append(timeline_entry)
        PlayerHelper.update_player_score(players_dict, player, points)

    def stats(self) -> Dict[str, Any]:
        """Returns a dictionary containing the current game statistics."""
        current_time = TimeHelper.calculate_current_time(
            self.state, self.total_time, self.gametime
        )

        time_display = TimeHelper.get_time_display(self.state, current_time)

        return {
            "Home": {
                "Name": self.home_.team_name,
                "Pts": self.home_score,
                "Players": {
                    name: data["score"] for name, data in self.home_players.items()
                },
            },
            "Away": {
                "Name": self.away_.team_name,
                "Pts": self.away_score,
                "Players": {
                    name: data["score"] for name, data in self.away_players.items()
                },
            },
            "Time": time_display,
            "Timeline": self.timeline,
        }
