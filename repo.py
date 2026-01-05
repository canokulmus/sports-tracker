from typing import Any, Dict, List, Optional, Tuple, Set

from sports_lib.cup import Cup
from sports_lib.game import Game
from sports_lib.team import Team


class Repo:
    """A repository for creating and managing domain objects like Teams and Games.

    Updated for Phase 3 with robust error handling.
    """

    def __init__(self) -> None:
        """Initializes the repository with an empty object store."""
        self._objects: Dict[int, Dict[str, Any]] = {}
        self._attachments: Dict[int, Set[str]] = {}
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
        
        # Inject the ID into kwargs so constructors can use/store it
        kwargs["id_"] = new_id

        try:
            if obj_type == "team":
                new_obj = Team(**kwargs)
            elif obj_type == "game":
                new_obj = Game(**kwargs)
            elif obj_type == "cup":
                # Inject repo reference so the Cup can register its games globally
                if "repo" not in kwargs:
                    kwargs["repo"] = self
                new_obj = Cup(**kwargs)
            else:
                raise ValueError(f"Unknown object type '{obj_type}'")

        except (TypeError, ValueError) as e:
            raise ValueError(f"Failed to create '{obj_type}': {str(e)}")

        self._objects[new_id] = {"instance": new_obj}
        self._attachments[new_id] = set()
        return new_id

    def list(self) -> List[Tuple[int, str]]:
        """Returns a list of (ID, description) for all managed objects."""
        results: List[Tuple[int, str]] = []
        for id, data in self._objects.items():
            instance = data["instance"]
            description = str(instance)
            results.append((id, description))
        return results

    def listattached(self, user: str) -> List[Tuple[int, str]]:
        """Lists the objects that the specified user has attached."""
        results: List[Tuple[int, str]] = []
        for obj_id, users in self._attachments.items():
            if user in users:
                instance = self._objects[obj_id]["instance"]
                results.append((obj_id, str(instance)))
        return results

    def attach(self, id: int, user: str) -> Any:
        """Attaches a user to an object and returns the object instance.

        The object is marked as 'in use' as long as it is attached by any user.
        """
        if id not in self._objects:
            raise ValueError(f"Object with ID {id} not found.")

        self._attachments[id].add(user)
        return self._objects[id]["instance"]

    def detach(self, id: int, user: str) -> None:
        """Detaches a user from an object.

        When the last user detaches, the object is no longer 'in use'.
        """
        if id not in self._objects:
            raise ValueError(f"Object with ID {id} not found.")

        if user in self._attachments[id]:
            self._attachments[id].remove(user)

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

        All users must detach the object before it can be deleted.

        Raises:
            ValueError: If the ID does not exist or if users are still attached.
        """
        if id not in self._objects:
            raise ValueError(f"Cannot delete: Object with ID {id} not found.")

        if self._attachments.get(id):
            users = ", ".join(self._attachments[id])
            raise ValueError(f"Cannot delete: Object with ID {id} is still in use by: {users}")

        # Clean up the object itself if it has a delete method
        if hasattr(self._objects[id]["instance"], "delete"):
            self._objects[id]["instance"].delete()

        del self._objects[id]
        if id in self._attachments:
            del self._attachments[id]
