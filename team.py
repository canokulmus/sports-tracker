from typing import Any, Dict


class Team:
    """Represents a sports team and its players."""

    def __init__(self, name: str) -> None:
        self.team_name = name
        # Players are stored in a dict with their name as the key.
        self.players: Dict[str, Dict[str, int]] = {}  # E.g., {'Player One': {'no': 10}}

    def __setitem__(self, key: str, value: Any) -> None:
        # Allows dict-style assignment (team['coach'] = 'Ana') for logging/demonstration.
        print(f"Setting {key} to {value}")
        self.__setattr__(key, value)

    def __getattr__(self, key: str) -> Any:
        # Redundant: __getattr__ is a fallback for missing attributes.
        # Calling __getattribute__ here risks infinite recursion if the attribute is missing.
        return self.__getattribute__(key)

    def __delattr__(self, key: str) -> None:
        # Redundant: this just calls the default parent method.
        super().__delattr__(key)

    def addplayer(self, name: str, no: int) -> None:
        self.players[name] = {"no": no}

    def delplayer(self, name: str) -> None:
        try:
            del self.players[name]
        except KeyError:
            # Fail gracefully if the player doesn't exist.
            print(f"Warning: Player '{name}' not found.")
