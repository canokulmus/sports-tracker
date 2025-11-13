from typing import Any, Dict
from constants import TeamMessages


class Team:
    """Represents a sports team, its players, and custom attributes."""

    def __init__(self, name: str) -> None:
        """Initializes a new Team with a given name."""
        self.team_name = name
        self.players: Dict[str, Dict[str, int]] = {}
        self._generic_attrs: Dict[str, Any] = {}

    def __str__(self) -> str:
        """Returns the team's name for display purposes."""
        return self.team_name

    def __setitem__(self, key: str, value: Any) -> None:
        """Enables setting custom attributes using dictionary-like syntax."""
        print(TeamMessages.setting_attribute(key, str(value)))
        self._generic_attrs[key] = value

    def __getattr__(self, key: str) -> Any:
        """Enables accessing custom attributes using dot notation.

        This is a fallback that allows attributes set via `__setitem__` (like
        `team['city'] = 'Istanbul'`) to be accessed as `team.city`.

        Raises:
            AttributeError: If the attribute doesn't exist as a standard or
                            custom attribute.
        """
        try:
            return self._generic_attrs[key]
        except KeyError:
            raise AttributeError(
                f"'{type(self).__name__}' object has no attribute '{key}'"
            )

    def __delattr__(self, key: str) -> None:
        """Enables deleting a custom attribute using `del`."""
        if key in self._generic_attrs:
            del self._generic_attrs[key]
        else:
            raise AttributeError(
                f"'{type(self).__name__}' object has no generic attribute '{key}' to delete."
            )

    def addplayer(self, name: str, no: int) -> None:
        """Adds a player to the team's roster."""
        self.players[name] = {"no": no}

    def delplayer(self, name: str) -> None:
        """Removes a player from the team's roster."""
        try:
            del self.players[name]
        except KeyError:
            print(TeamMessages.player_not_found(name))


class PlaceholderTeam(Team):
    """A placeholder for a team that will be determined by a future game.

    In elimination tournaments, this class is used to build future rounds
    before the winners of the current round are known.
    """

    def __init__(self, description: str, source_games: list[int]) -> None:
        """Initializes the placeholder with a description and source game IDs."""
        super().__init__(description)
        self.source_games = source_games
        self.is_placeholder = True

    def __str__(self) -> str:
        """Returns a descriptive name indicating which game's winner it represents."""
        if len(self.source_games) == 1:
            return f"Winner of Game {self.source_games[0]}"
        else:
            game_ids = ", ".join(str(g) for g in self.source_games)
            return f"Winner of Games [{game_ids}]"
