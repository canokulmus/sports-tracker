import itertools
from enum import Enum, auto


class GameState(Enum):
    READY = auto()
    RUNNING = auto()
    PAUSED = auto()
    ENDED = auto()


class Team:
    def __init__(self, name):
        self.team_name = name
        self.players = {}  # K: player_name, V: {'no': no}

    def __setitem__(self, key, value):
        # Allows dict-style assignment like team['coach'] = 'Ana'
        # This is mostly for debugging/logging.
        print(f"Setting {key} to {value}")
        self.__setattr__(key, value)

    def __getattr__(self, key):
        return self.__getattribute__(key)

    def __delattr__(self, key):
        super().__delattr__(key)

    def addplayer(self, name, no):
        # Method is self-explanatory
        self.players[name] = {"no": no}

    def delplayer(self, name):
        try:
            del self.players[name]
        except KeyError:
            # Fail gracefully instead of crashing if player not found
            print(f"Warning: Player '{name}' not found.")


class Game:
    def __init__(self, home, away, id, gametime=0, state=GameState.READY):
        self.home = home
        self.away = away
        self.gametime = gametime
        self.id = id
        self.state = state

    def id(self):
        return self.id
    
    def home(self):
        return self.home
    
    def away(self):
        return self.away
    
    def start(self):


class Cup:
    def __init__(self):
        self.games = []


class Repo:
    def __init__(self):
        self._objects = {}
        # Use itertools for a simple, memory-efficient ID generator (1, 2, 3...)
        self._id_counter = itertools.count(start=1)

    def create(self, **kwargs):
        # We .pop() 'type' so it isn't passed into the object's constructor
        obj_type = kwargs.pop("type", None)

        if obj_type is None:
            raise ValueError("You must specify an object 'type' to create.")

        new_id = next(self._id_counter)  # Get the next sequential ID

        new_obj = None

        # --- Factory Pattern ---
        # Select the correct class to build based on 'type'
        if obj_type == "team":
            # Pass all remaining kwargs (e.g., 'name') to Team's __init__
            new_obj = Team(**kwargs)

        elif obj_type == "game":
            kwargs["id"] = new_id
            new_obj = Game(**kwargs)

        elif obj_type == "cup":
            new_obj = Cup(**kwargs)  # Assumes Cup class is defined

        else:
            raise ValueError(f"Unknown object type '{obj_type}'")

        self._objects[new_id] = {
            "instance": new_obj,
            "attachment_count": 0,
            "users": [],
        }

        return new_id

    def list(self):
        # Return a simple list of (id, object) tuples
        return [(id, self._objects[id]) for id in self._objects.keys()]

    def attach(self, id, user="Captain Barbossa"):
        # The 'user' param is accepted but not currently used in the logic
        self._objects[id]["attachment_count"] += 1

        return self._objects[id]

    def deattach(self, id):
        self._objects[id]["attachment_count"] -= 1

    def delete(self, id):
        if self._objects[id]["attachment_count"] > 0:
            raise ValueError("The object is still attached")
        else:
            del self._objects[id]
