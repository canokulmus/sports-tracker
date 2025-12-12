from typing import Any, Dict, List, Optional, Tuple

from .cup import Cup
from .game import Game
from .team import Team


class Repo:
    """A repository for creating and managing domain objects like Teams and Games.

    Updated for Phase 3 with robust error handling.
    """

    def __init__(self) -> None:
        """Initializes the repository with an empty object store."""
        self._objects: Dict[int, Dict[str, Any]] = {}
        self._last_id = 0

    def create(self, **kwargs: Any) -> int:
        """Creates and registers an object based on its 'type'.

        Raises:
            ValueError: If 'type' is missing, unknown, or if required arguments
                        for the object (like 'name' for Team) are missing.
        """
        obj_type: Optional[str] = kwargs.pop("type", None)
        if obj_type is None:
            raise ValueError("You must specify an object 'type' to create.")

        self._last_id += 1
        new_id = self._last_id

        try:
            if obj_type == "team":
                new_obj = Team(**kwargs)
            elif obj_type == "game":
                kwargs["id_"] = new_id
                new_obj = Game(**kwargs)
            elif obj_type == "cup":
                new_obj = Cup(**kwargs)
            else:
                raise ValueError(f"Unknown object type '{obj_type}'")

        except TypeError as e:
            # Revert the ID increment since creation failed
            self._last_id -= 1
            raise ValueError(f"Failed to create '{obj_type}': {str(e)}")

        self._objects[new_id] = {"instance": new_obj}
        return new_id

    def list(self) -> List[Tuple[int, str]]:
        """Returns a list of (ID, description) for all managed objects."""
        results: List[Tuple[int, str]] = []
        for id, data in self._objects.items():
            instance = data["instance"]
            description = str(instance)
            results.append((id, description))
        return results

    def get(self, id: int) -> Any:
        """Retrieve an object instance by ID.

        Raises:
            ValueError: If the ID does not exist.
        """
        if id not in self._objects:
            raise ValueError(f"Object with ID {id} not found.")

        return self._objects[id]["instance"]

    def delete(self, id: int) -> None:
        """Deletes an object by its ID.

        Raises:
            ValueError: If the ID does not exist.
        """
        if id in self._objects:
            del self._objects[id]
        else:
            raise ValueError(f"Cannot delete: Object with ID {id} not found.")
