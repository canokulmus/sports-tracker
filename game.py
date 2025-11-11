# game.py
from datetime import datetime
from time import monotonic
from typing import Any, Dict, List, Tuple

from team import Team
from constants import GameState, GameMessages, GameSettings
from helpers import TimeHelper, PlayerHelper, ScoreHelper


class Game:
    """Represents a single game between two teams."""

    def __init__(
        self,
        home: Team,
        away: Team,
        id_: int,
        datetime: datetime,
        state: GameState = GameState.READY,
    ) -> None:
        self.home_ = home
        self.away_ = away
        self.id_ = id_
        self.datetime = datetime
        self.state = state
        
        # Time tracking
        self.total_time = GameSettings.DEFAULT_TIME
        self.gametime = GameSettings.DEFAULT_TIME
        
        # Scores
        self.home_score = GameSettings.DEFAULT_SCORE
        self.away_score = GameSettings.DEFAULT_SCORE
        
        # Player scores
        self.home_players = {
            name: {"no": data["no"], "score": GameSettings.DEFAULT_SCORE}
            for name, data in home.players.items()
        }
        self.away_players = {
            name: {"no": data["no"], "score": GameSettings.DEFAULT_SCORE}
            for name, data in away.players.items()
        }
        
        # Observer pattern
        self._observers: List[Any] = []
        
        # Timeline tracking
        self.timeline: List[Tuple[str, str, str, int]] = []

    def __str__(self) -> str:
        """Returns the string representation of the Game."""
        return f"Game: {self.home().team_name} vs {self.away().team_name}"

    def _notify_observers(self) -> None:
        """Internal method to call .update() on all observers."""
        for obj in self._observers:
            obj.update(self)

    def id(self) -> int:
        """Returns the game's ID."""
        return self.id_

    def home(self) -> Team:
        """Returns the home team."""
        return self.home_

    def away(self) -> Team:
        """Returns the away team."""
        return self.away_

    def start(self) -> None:
        """Starts the game if it is in the READY state."""
        if self.state == GameState.READY:
            self.state = GameState.RUNNING
            self.gametime = monotonic()
            print(GameMessages.GAME_STARTED)
        elif self.state == GameState.RUNNING:
            print(GameMessages.GAME_ALREADY_RUNNING)
        elif self.state == GameState.PAUSED:
            print(GameMessages.GAME_PAUSED_USE_RESUME)
        else:
            print(GameMessages.GAME_ALREADY_ENDED)

    def pause(self) -> None:
        """Pauses the game if it is RUNNING."""
        if self.state == GameState.RUNNING:
            self.total_time += monotonic() - self.gametime
            self.state = GameState.PAUSED
            print(GameMessages.GAME_PAUSED)
        elif self.state == GameState.PAUSED:
            print(GameMessages.GAME_ALREADY_PAUSED)
        elif self.state == GameState.ENDED:
            print(GameMessages.GAME_ALREADY_ENDED)
        else:
            print(GameMessages.GAME_NOT_RUNNING)

    def resume(self) -> None:
        """Resumes the game if it is PAUSED."""
        if self.state == GameState.PAUSED:
            self.state = GameState.RUNNING
            self.gametime = monotonic()
            print(GameMessages.GAME_RESUMED)
        elif self.state == GameState.RUNNING:
            print(GameMessages.GAME_ALREADY_RUNNING)
        elif self.state == GameState.READY:
            print(GameMessages.GAME_NOT_STARTED)
        else:
            print(GameMessages.GAME_ALREADY_ENDED)

    def end(self) -> None:
        """Ends the game."""
        if self.state == GameState.ENDED:
            print(GameMessages.GAME_ALREADY_ENDED)
            return

        if self.state == GameState.RUNNING:
            self.total_time += monotonic() - self.gametime

        self.state = GameState.ENDED
        print(GameMessages.GAME_ENDED)

        self._notify_observers()

    def score(self, points: int, team: Team, player: str | None = None) -> None:
        """Adds points to a team's score if the game is running."""
        if self.state != GameState.RUNNING:
            print(GameMessages.CANNOT_SCORE_NOT_RUNNING)
            return

        # Calculate and format current time
        current_time = TimeHelper.calculate_current_time(
            self.state, self.total_time, self.gametime
        )
        time_str = TimeHelper.format_game_time(current_time)

        # Get player name
        player_name = PlayerHelper.get_player_name(player)

        # Update scores and timeline
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
        """
        Internal helper to handle scoring for a team.
        
        Args:
            team: Team object
            team_type: "Home" or "Away"
            points: Points scored
            time_str: Formatted time string
            player: Player name or None
            player_name: Resolved player name
            players_dict: Dictionary of team's players
        """
        print(GameMessages.team_scored(team.team_name, points))
        
        # Add to timeline
        timeline_entry = ScoreHelper.create_timeline_entry(
            time_str, team_type, player_name, points
        )
        self.timeline.append(timeline_entry)
        
        # Update player score
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
        """Return a dictionary of game statistics."""
        
        # Calculate current time using helper
        current_time = TimeHelper.calculate_current_time(
            self.state, self.total_time, self.gametime
        )

        # Get time display using helper
        time_display = TimeHelper.get_time_display(self.state, current_time)

        return {
            "Home": {
                "Name": self.home_.team_name,
                "Pts": self.home_score,
                "Players": {
                    name: data["score"]
                    for name, data in self.home_players.items()
                },
            },
            "Away": {
                "Name": self.away_.team_name,
                "Pts": self.away_score,
                "Players": {
                    name: data["score"]
                    for name, data in self.away_players.items()
                },
            },
            "Time": time_display,
            "Timeline": self.timeline,
        }