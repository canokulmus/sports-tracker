from typing import Any, Dict


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
        print(f"Setting generic attribute {key} to {value}")
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
            print(f"Warning: Player '{name}' not found.")
