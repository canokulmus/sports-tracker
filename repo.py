import itertools
from enum import Enum, auto

# monotonic is for measuring time intervals; it's not affected by system time changes.
from time import monotonic
from datetime import datetime


# Using an Enum for game states prevents bugs from using invalid state strings.
class GameState(Enum):
    READY = auto()
    RUNNING = auto()
    PAUSED = auto()
    ENDED = auto()


# Represents a sports team and its players.
class Team:
    def __init__(self, name):
        self.team_name = name
        # Players are stored in a dict with their name as the key.
        self.players = {}  # E.g., {'Player One': {'no': 10}}

    def __setitem__(self, key, value):
        # Allows dict-style assignment (team['coach'] = 'Ana') for logging/demonstration.
        print(f"Setting {key} to {value}")
        self.__setattr__(key, value)

    def __getattr__(self, key):
        # Redundant: __getattr__ is a fallback for missing attributes.
        # Calling __getattribute__ here risks infinite recursion if the attribute is missing.
        return self.__getattribute__(key)

    def __delattr__(self, key):
        # Redundant: this just calls the default parent method.
        super().__delattr__(key)

    def addplayer(self, name, no):
        self.players[name] = {"no": no}

    def delplayer(self, name):
        try:
            del self.players[name]
        except KeyError:
            # Fail gracefully if the player doesn't exist.
            print(f"Warning: Player '{name}' not found.")


class Game:
    def __init__(
        self,
        home: Team,
        away: Team,
        id_: int,
        datetime: datetime,
        state: GameState = GameState.READY,
    ):
        self.home_ = home
        self.away_ = away
        self.id_ = id_  # Trailing underscore to avoid shadowing the built-in id()
        self.datetime = datetime
        self.state = state
        # total_time accumulates paused game duration.
        self.total_time = 0
        # gametime marks the start of a running segment.
        self.gametime = 0

    # Simple "getters" provide a stable interface, though direct access (e.g., game.id_)
    # is also common in Python.
    def id(self):
        return self.id_

    def home(self):
        return self.home_

    def away(self):
        return self.away_

    def start(self):
        # A game must be in the READY state to start.
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

    def pause(self):
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

    def resume(self):
        # A game must be PAUSED to be resumed.
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


# A container for a collection of games (e.g., a tournament).
class Cup:
    def __init__(self):
        self.games = []


# The Repo class is a central registry for creating and managing all objects.
class Repo:
    def __init__(self):
        self._objects = {}
        # Use itertools.count for a memory-efficient ID generator (1, 2, 3...).
        self._id_counter = itertools.count(start=1)

    def create(self, **kwargs):
        # A factory method to create objects. The 'type' kwarg determines the class.
        obj_type = kwargs.pop("type", None)

        if obj_type is None:
            raise ValueError("You must specify an object 'type' to create.")

        new_id = next(self._id_counter)  # Get the next sequential ID

        new_obj = None

        if obj_type == "team":
            # Pass remaining kwargs (e.g., name='Warriors') to the Team constructor.
            new_obj = Team(**kwargs)

        elif obj_type == "game":
            # Add the new ID to kwargs before creating the Game.
            kwargs["id_"] = new_id
            new_obj = Game(**kwargs)

        elif obj_type == "cup":
            new_obj = Cup(**kwargs)  # Assumes Cup class is defined

        else:
            raise ValueError(f"Unknown object type '{obj_type}'")

        # Store the new object with metadata for reference counting.
        self._objects[new_id] = {
            "instance": new_obj,
            "attachment_count": 0,
            "users": [],
        }

        return new_id

    def list(self):
        # Returns a list of all managed objects and their IDs.
        return [(id, self._objects[id]) for id in self._objects.keys()]

    def attach(self, id, user="Captain Barbossa"):
        # Increments a reference counter to prevent deletion while an object is "in use".
        self._objects[id]["attachment_count"] += 1

        return self._objects[id]

    def deattach(self, id):
        # Decrements the object's reference counter.
        self._objects[id]["attachment_count"] -= 1

    def delete(self, id):
        # An object cannot be deleted if its reference count is > 0.
        if self._objects[id]["attachment_count"] > 0:
            raise ValueError("The object is still attached")
        else:
            del self._objects[id]
