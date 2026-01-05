from typing import Any, Dict, List


class Team:
    """Represents a sports team, its players, and custom attributes.

    Refactored for Phase 3:
    - Removed print statements (statelessness).
    - Added proper exception raising for error handling.
    """

    def __init__(self, name: str, **kwargs: Any) -> None:
        """Initializes a new Team with a given name."""
        if not name:
            raise ValueError("Team name cannot be empty.")
        self.team_name = name
        self.players: Dict[int, Dict[str, Any]] = {}
        self._player_id_counter = 0
        self._generic_attrs: Dict[str, Any] = {}
        for key, value in kwargs.items():
            self[key] = value

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

    def addplayer(self, name: str, no: int) -> int:
        """Adds or updates a player in the team's roster.

        Args:
            name: The name of the player.
            no: The jersey number.

        Returns:
            int: The unique ID assigned to the player.
        """
        self._player_id_counter += 1
        player_id = self._player_id_counter
        self.players[player_id] = {"name": name, "no": no}
        return player_id

    def delplayer(self, name: str) -> None:
        """Removes the first player found with the given name.

        Raises:
            ValueError: If the player is not found.
        """
        for pid, pdata in list(self.players.items()):
            if pdata["name"] == name:
                del self.players[pid]
                return
        raise ValueError(f"Player '{name}' not found in team '{self.team_name}'.")

    # CRUD Methods

    def get(self) -> str:
        """Returns a textual representation of the team (JSON-like)."""
        return str({
            "id": self.getid() if hasattr(self, "getid") else None,
            "name": self.team_name,
            "players": self.players,
            "attributes": self._generic_attrs
        })

    def update(self, **kw: Any) -> None:
        """Updates the team with new values.

        If 'name' is provided, it updates the team name. Other arguments
        are treated as generic attributes.
        """
        if "name" in kw:
            self.team_name = kw.pop("name")

        for key, value in kw.items():
            self[key] = value

    def delete(self) -> None:
        """Deletes the item by clearing its internal data."""
        self.players.clear()
        self._generic_attrs.clear()
        self.team_name = "DELETED"

    def getid(self) -> Any:
        """Returns the unique ID of the team if assigned by a Repo."""
        return getattr(self, "id_", None)


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
