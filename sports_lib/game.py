from datetime import datetime
from time import monotonic
from typing import Any, Dict, List, Tuple, Optional

from .team import Team
from .constants import GameState, GameSettings
from .helpers import TimeHelper, PlayerHelper, ScoreHelper


class Game:
    """Manages the state and logic of a single game between two teams.

    Updated to include Observer pattern and CRUD methods.
    """

    def __init__(
        self,
        home: Team,
        away: Team,
        datetime: datetime,
        **kwargs: Any,
    ) -> None:
        self.home_ = home
        self.away_ = away
        self.datetime = datetime
        
        # Handle optional arguments via kwargs to support Repo and Cup factories
        self.id_ = kwargs.get("id_", kwargs.get("id", -1))
        self.state = kwargs.get("state", GameState.READY)
        self.group = kwargs.get("group", None)

        self._observers: List[Any] = []

        self.total_time = GameSettings.DEFAULT_TIME
        self.gametime = GameSettings.DEFAULT_TIME

        self.home_score = GameSettings.DEFAULT_SCORE
        self.away_score = GameSettings.DEFAULT_SCORE

        self.home_players = {
            pid: {"name": data["name"], "no": data["no"], "score": GameSettings.DEFAULT_SCORE}
            for pid, data in home.players.items()
        }
        self.away_players = {
            pid: {"name": data["name"], "no": data["no"], "score": GameSettings.DEFAULT_SCORE}
            for pid, data in away.players.items()
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

    def watch(self, obj: Any) -> None:
        """Adds the obj as an observer for the game."""
        if obj not in self._observers:
            self._observers.append(obj)

    def unwatch(self, obj: Any) -> None:
        """Remove the obj from list of observers."""
        if obj in self._observers:
            self._observers.remove(obj)

    def _notify(self) -> None:
        """Notifies all observers of an update."""
        for observer in self._observers:
            if hasattr(observer, "update"):
                observer.update(self)

    def start(self) -> None:
        """Transitions the game from READY to RUNNING state.

        Raises:
            ValueError: If the game is not in the READY state.
        """
        if self.state == GameState.READY:
            self.state = GameState.RUNNING
            self.gametime = monotonic()
            self._notify()
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
            self._notify()
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
            self._notify()
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
        self._notify()

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

        # Find the internal player ID if a name was provided
        target_pid = None
        players_dict = self.home_players if team == self.home_ else self.away_players

        if player:
            for pid, pdata in players_dict.items():
                if pdata["name"] == player:
                    target_pid = pid
                    break

        if team == self.home_:
            self._score_for_team(
                team_type="Home",
                points=points,
                time_str=time_str,
                player=player,
                player_name=player_name,
                players_dict=self.home_players,
                player_id=target_pid
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
                player_id=target_pid
            )
            self.away_score += points
        else:
            raise ValueError(
                f"Team '{team.team_name}' is not participating in this game."
            )

        self._notify()

    def _score_for_team(
        self,
        team_type: str,
        points: int,
        time_str: str,
        player: Optional[str],
        player_name: str,
        players_dict: Dict[int, Dict[str, Any]],
        player_id: Optional[int] = None,
    ) -> None:
        """Internal helper to encapsulate the logic of recording a score."""
        timeline_entry = ScoreHelper.create_timeline_entry(
            time_str, team_type, player_name, points
        )
        self.timeline.append(timeline_entry)
        PlayerHelper.update_player_score(players_dict, player_id, points)

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
                    data["name"]: data["score"] for data in self.home_players.values()
                },
            },
            "Away": {
                "Name": self.away_.team_name,
                "Pts": self.away_score,
                "Players": {
                    data["name"]: data["score"] for data in self.away_players.values()
                },
            },
            "Time": time_display,
            "Timeline": self.timeline,
        }

    # CRUD Methods

    def get(self) -> str:
        """Returns a textual representation of the item."""
        return str(self.stats())

    def update(self, **kw: Any) -> None:
        """Updates the game with new values."""
        if "datetime" in kw:
            self.datetime = kw["datetime"]
        if "group" in kw:
            self.group = kw["group"]
        
        # Handle team updates (re-initializes players)
        if "home" in kw:
            self.home_ = kw["home"]
            self.home_players = {
                pid: {"name": data["name"], "no": data["no"], "score": GameSettings.DEFAULT_SCORE}
                for pid, data in self.home_.players.items()
            }
        if "away" in kw:
            self.away_ = kw["away"]
            self.away_players = {
                pid: {"name": data["name"], "no": data["no"], "score": GameSettings.DEFAULT_SCORE}
                for pid, data in self.away_.players.items()
            }
        
        self._notify()

    def delete(self) -> None:
        """Deletes the item by clearing its internal data."""
        self._observers.clear()
        self.timeline.clear()
        self.home_players.clear()
        self.away_players.clear()
        self.state = GameState.ENDED

    def getid(self) -> int:
        """Returns the unique identifier for the game."""
        return self.id_

    # For pickle
    def __getstate__(self):
        state = self.__dict__.copy()
        state["_observers"] = []
        return state

    def __setstate__(self, state):
        self.__dict__.update(state)
        if "_observers" not in self.__dict__:
            self._observers = []
