from datetime import datetime
from enum import Enum, auto
from time import monotonic

from team import Team


class GameState(Enum):
    """Enum for game states to prevent bugs from using invalid state strings."""

    READY = auto()
    RUNNING = auto()
    PAUSED = auto()
    ENDED = auto()


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
        self.id_ = id_  # Trailing underscore to avoid shadowing the built-in id()
        self.datetime = datetime
        self.state = state
        # total_time accumulates paused game duration.
        self.total_time = 0
        # gametime marks the start of a running segment.
        self.gametime = 0
        self.home_score = 0
        self.away_score = 0
        self.home_players = {
            name: {"no": data["no"], "score": 0} for name, data in home.players.items()
        }
        self.away_players = {
            name: {"no": data["no"], "score": 0} for name, data in away.players.items()
        }

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
            print("Game started")
        elif self.state == GameState.RUNNING:
            print("Game is already running.")
        elif self.state == GameState.PAUSED:
            print("Game is paused. Use resume() to continue.")
        else:
            print("Game is already ended.")

    def pause(self) -> None:
        """Pauses the game if it is RUNNING."""
        if self.state == GameState.RUNNING:
            # Add the last running segment's duration to the total before pausing.
            self.total_time += monotonic() - self.gametime
            self.state = GameState.PAUSED
            print("Game paused")
        elif self.state == GameState.PAUSED:
            print("Game is already paused.")
        elif self.state == GameState.ENDED:
            print("Game is already ended.")
        else:
            print("Game is not running.")

    def resume(self) -> None:
        """Resumes the game if it is PAUSED."""
        if self.state == GameState.PAUSED:
            self.state = GameState.RUNNING
            self.gametime = monotonic()
            print("Game resumed")
        elif self.state == GameState.RUNNING:
            print("Game is already running.")
        elif self.state == GameState.READY:
            print("Game has not started yet. Use start().")
        else:  # ENDED
            print("Game is already ended.")

    def end(self) -> None:
        """Ends the game."""
        if self.state == GameState.ENDED:
            print("Game is already ended.")
            return

        if self.state == GameState.RUNNING:
            self.total_time += monotonic() - self.gametime

        self.state = GameState.ENDED
        print("Game has ended.")

    def score(self, points: int, team: Team, player: str | None = None) -> None:
        """Adds points to a team's score if the game is running."""
        if self.state != GameState.RUNNING:
            print("Cannot score, game is not running.")
            return

        if team == self.home_:
            self.home_score += points
            print(f"{team.team_name} scored {points} points.")
            if player is not None and player in self.home_players:
                self.home_players[player]["score"] += points
        elif team == self.away_:
            self.away_score += points
            print(f"{team.team_name} scored {points} points.")
            if player is not None and player in self.away_players:
                self.away_players[player]["score"] += points
