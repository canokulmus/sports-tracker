import itertools
from typing import Any, Dict, List, Tuple

from cup import Cup
from game import Game
from team import Team


class Repo:
    """A central registry for creating and managing all objects."""

    def __init__(self) -> None:
        self._objects: Dict[int, Dict[str, Any]] = {}
        # Use itertools.count for a memory-efficient ID generator (1, 2, 3...).
        self._id_counter = itertools.count(start=1)

    def create(self, **kwargs: Any) -> int:
        # A factory method to create objects. The 'type' kwarg determines the class.
        obj_type: str = kwargs.pop("type", None)

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

    def list(self) -> List[Tuple[int, str]]:
        """
        Returns a list of (id, description) pairs for all managed objects.
        """
        results: List[Tuple[int, str]] = []
        for id, data in self._objects.items():
            instance = data["instance"]
            # Python automatically calls the correct __str__ method!
            description = str(instance)
            results.append((id, description))

        return results

    def attach(self, id: int, user: str = "Polat Alemdar") -> Dict[str, Any]:
        self._objects[id]["attachment_count"] += 1
        self._objects[id]["users"].append(user)
        return self._objects[id]

    def detach(self, id: int, user: str) -> None:
        obj_data = self._objects[id]
        if user in obj_data["users"]:
            obj_data["users"].remove(user)
            if obj_data["attachment_count"] > 0:
                obj_data["attachment_count"] -= 1

    def delete(self, id: int) -> None:
        """Deletes an object if it is no longer attached."""
        if self._objects[id]["attachment_count"] > 0:
            raise ValueError("The object is still attached")
        else:
            del self._objects[id]
