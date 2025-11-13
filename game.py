from datetime import datetime
from time import monotonic
from typing import Any, Dict, List, Tuple

from team import Team
from constants import GameState, GameMessages, GameSettings
from helpers import TimeHelper, PlayerHelper, ScoreHelper


class Game:
    """Manages the state and logic of a single game between two teams.

    This class tracks game time, score, and state transitions (e.g., ready,
    running, paused, ended). It also implements the observer pattern, allowing
    other objects to be notified of significant game events.
    """

    def __init__(
        self,
        home: Team,
        away: Team,
        id_: int,
        datetime: datetime,
        state: GameState = GameState.READY,
        group: str | None = None,
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
        self._observers: List[Any] = []

        self.timeline: List[Tuple[str, str, str, int]] = []

    def __str__(self) -> str:
        """Returns the string representation of the Game."""
        return f"Game: {self.home().team_name} vs {self.away().team_name}"

    def _notify_observers(self) -> None:
        """Notifies all registered observers of a state change."""
        for obj in self._observers:
            obj.update(self)

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
        """Transitions the game from READY to RUNNING state."""
        if self.state == GameState.READY:
            self.state = GameState.RUNNING
            self.gametime = monotonic()
            print(GameMessages.GAME_STARTED)
            self._notify_observers()
        elif self.state == GameState.RUNNING:
            print(GameMessages.GAME_ALREADY_RUNNING)
        elif self.state == GameState.PAUSED:
            print(GameMessages.GAME_PAUSED_USE_RESUME)
        else:
            print(GameMessages.GAME_ALREADY_ENDED)

    def pause(self) -> None:
        """Transitions the game from RUNNING to PAUSED state."""
        if self.state == GameState.RUNNING:
            self.total_time += monotonic() - self.gametime
            self.state = GameState.PAUSED
            print(GameMessages.GAME_PAUSED)
            self._notify_observers()
        elif self.state == GameState.PAUSED:
            print(GameMessages.GAME_ALREADY_PAUSED)
        elif self.state == GameState.ENDED:
            print(GameMessages.GAME_ALREADY_ENDED)
        else:
            print(GameMessages.GAME_NOT_RUNNING)

    def resume(self) -> None:
        """Transitions the game from PAUSED back to RUNNING state."""
        if self.state == GameState.PAUSED:
            self.state = GameState.RUNNING
            self.gametime = monotonic()
            print(GameMessages.GAME_RESUMED)
            self._notify_observers()
        elif self.state == GameState.RUNNING:
            print(GameMessages.GAME_ALREADY_RUNNING)
        elif self.state == GameState.READY:
            print(GameMessages.GAME_NOT_STARTED)
        else:
            print(GameMessages.GAME_ALREADY_ENDED)

    def end(self) -> None:
        """Transitions the game to the ENDED state, finalizing the time."""
        if self.state == GameState.ENDED:
            print(GameMessages.GAME_ALREADY_ENDED)
            return

        if self.state == GameState.RUNNING:
            self.total_time += monotonic() - self.gametime

        self.state = GameState.ENDED
        print(GameMessages.GAME_ENDED)

        self._notify_observers()

    def score(self, points: int, team: Team, player: str | None = None) -> None:
        """Records a score for a team and optionally a player.

        This method only functions when the game is in the RUNNING state. It
        updates the team's score, the player's score, and adds an entry to
        the game's timeline.
        """
        if self.state != GameState.RUNNING:
            print(GameMessages.CANNOT_SCORE_NOT_RUNNING)
            return

        current_time = TimeHelper.calculate_current_time(
            self.state, self.total_time, self.gametime
        )
        time_str = TimeHelper.format_game_time(current_time)
        player_name = PlayerHelper.get_player_name(player)

        if team == self.home_:
            self._score_for_team(
                team=team,
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
                team=team,
                team_type="Away",
                points=points,
                time_str=time_str,
                player=player,
                player_name=player_name,
                players_dict=self.away_players,
            )
            self.away_score += points

        self._notify_observers()

    def _score_for_team(
        self,
        team: Team,
        team_type: str,
        points: int,
        time_str: str,
        player: str | None,
        player_name: str,
        players_dict: Dict[str, Dict[str, int]],
    ) -> None:
        """Internal helper to encapsulate the logic of recording a score."""
        print(GameMessages.team_scored(team.team_name, points))

        timeline_entry = ScoreHelper.create_timeline_entry(
            time_str, team_type, player_name, points
        )
        self.timeline.append(timeline_entry)
        PlayerHelper.update_player_score(players_dict, player, points)

    def watch(self, obj: Any) -> None:
        """Adds the obj as an observer for the game."""
        if obj not in self._observers:
            self._observers.append(obj)

    def unwatch(self, obj: Any) -> None:
        """Remove the obj from list of observers."""
        if obj in self._observers:
            self._observers.remove(obj)

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
