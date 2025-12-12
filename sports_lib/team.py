from typing import Any, Dict, List


class Team:
    """Represents a sports team, its players, and custom attributes.

    Refactored for Phase 3:
    - Removed print statements (statelessness).
    - Added proper exception raising for error handling.
    """

    def __init__(self, name: str) -> None:
        """Initializes a new Team with a given name."""
        if not name:
            raise ValueError("Team name cannot be empty.")
        self.team_name = name
        self.players: Dict[str, Dict[str, int]] = {}
        self._generic_attrs: Dict[str, Any] = {}

    def __str__(self) -> str:
        """Returns the team's name for display purposes."""
        return self.team_name

    def __setitem__(self, key: str, value: Any) -> None:
        """Enables setting custom attributes using dictionary-like syntax.

        Example: team['city'] = 'Istanbul'
        """
        self._generic_attrs[key] = value

    def __getattr__(self, key: str) -> Any:
        """Enables accessing custom attributes using dot notation.

        Raises:
            AttributeError: If the attribute doesn't exist.
        """
        # Safety check for unpickling or initialization issues
        if key == "_generic_attrs":
            raise AttributeError()

        try:
            return self._generic_attrs[key]
        except KeyError:
            raise AttributeError(
                f"'{type(self).__name__}' object has no attribute '{key}'"
            )

    def __delattr__(self, key: str) -> None:
        """Enables deleting a custom attribute using `del`.

        Raises:
            AttributeError: If the attribute does not exist in _generic_attrs.
        """
        if key in self._generic_attrs:
            del self._generic_attrs[key]
        else:
            raise AttributeError(
                f"'{type(self).__name__}' object has no generic attribute '{key}' to delete."
            )

    def addplayer(self, name: str, no: int) -> None:
        """Adds or updates a player in the team's roster.

        Args:
            name: The name of the player.
            no: The jersey number.
        """
        # Pylance Note: We rely on the API View to ensure 'no' is an int
        # before calling this method, matching the type hint 'no: int'.
        self.players[name] = {"no": no}

    def delplayer(self, name: str) -> None:
        """Removes a player from the team's roster.

        Raises:
            ValueError: If the player is not found.
        """
        try:
            del self.players[name]
        except KeyError:
            raise ValueError(f"Player '{name}' not found in team '{self.team_name}'.")


class PlaceholderTeam(Team):
    """A placeholder for a team that will be determined by a future game.

    Used in tournament generation (Elimination brackets).
    """

    def __init__(self, description: str, source_games: List[int]) -> None:
        """Initializes the placeholder with a description and source game IDs."""
        # Initialize parent with the description as the team name
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
