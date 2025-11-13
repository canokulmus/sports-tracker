from typing import Any, Dict
from constants import TeamMessages

class Team:
    """Represents a sports team and its players."""

    def __init__(self, name: str) -> None:
        self.team_name = name
        # Players are stored in a dict with their name as the key.
        self.players: Dict[str, Dict[str, int]] = {}
        # A separate dict for generic attributes
        self._generic_attrs: Dict[str, Any] = {}

    def __str__(self) -> str:
        """Returns the string representation of the team."""
        return self.team_name

    def __setitem__(self, key: str, value: Any) -> None:
        """Sets a generic team attribute."""
        print(TeamMessages.setting_attribute(key, str(value)))
        self._generic_attrs[key] = value

    def __getattr__(self, key: str) -> Any:
        """
        Returns the given attribute.
        This is a fallback: only called for attributes not found normally.
        """
        try:
            # Check the generic attributes dictionary first
            return self._generic_attrs[key]
        except KeyError:
            # If not found, raise the standard Python error
            raise AttributeError(
                f"'{type(self).__name__}' object has no attribute '{key}'"
            )

    def __delattr__(self, key: str) -> None:
        """Deletes the given attribute."""
        if key in self._generic_attrs:
            del self._generic_attrs[key]
        else:
            # Use super() to delete "normal" attributes (though you might not want to)
            # or just raise an error.
            try:
                super().__delattr__(key)
            except AttributeError:
                raise AttributeError(
                    f"'{type(self).__name__}' object has no attribute '{key}'"
                )

    def addplayer(self, name: str, no: int) -> None:
        self.players[name] = {"no": no}

    def delplayer(self, name: str) -> None:
        try:
            del self.players[name]
        except KeyError:
            print(TeamMessages.player_not_found(name))


class PlaceholderTeam(Team):
    """
    Placeholder team for elimination rounds.
    Represents the winner of a previous game that hasn't been played yet.
    """
    
    def __init__(self, description: str, source_games: list[int]) -> None:
        """
        Args:
            description: Description like "Winner of Game 1"
            source_games: List of game IDs whose winner will fill this slot
        """
        super().__init__(description)
        self.source_games = source_games
        self.is_placeholder = True
    
    def __str__(self) -> str:
        if len(self.source_games) == 1:
            return f"Winner of Game {self.source_games[0]}"
        else:
            game_ids = ", ".join(str(g) for g in self.source_games)
            return f"Winner of Games [{game_ids}]"