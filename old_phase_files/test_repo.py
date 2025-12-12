# test_repo.py
"""Unit tests for Repo class."""

import pytest
from datetime import datetime
from repo import Repo
from team import Team
from game import Game


class TestRepo:
    """Test cases for Repo class."""

    @pytest.fixture
    def repo(self) -> Repo:
        """Create a fresh repo for testing."""
        return Repo()

    def test_repo_creation(self, repo: Repo) -> None:
        """Test repo can be created."""
        assert repo is not None
        assert len(repo._objects) == 0

    def test_create_team(self, repo: Repo) -> None:
        """Test creating a team."""
        team_id = repo.create(type="team", name="Galatasaray")

        assert team_id == 1
        assert team_id in repo._objects

        obj_data = repo._objects[team_id]
        assert isinstance(obj_data["instance"], Team)
        assert obj_data["instance"].team_name == "Galatasaray"

    def test_create_game(self, repo: Repo) -> None:
        """Test creating a game."""
        # First create teams
        team1_id = repo.create(type="team", name="Home Team")
        team2_id = repo.create(type="team", name="Away Team")

        # Get team instances
        team1 = repo._objects[team1_id]["instance"]
        team2 = repo._objects[team2_id]["instance"]

        # Create game
        game_id = repo.create(
            type="game", home=team1, away=team2, datetime=datetime.now()
        )

        assert game_id == 3
        assert isinstance(repo._objects[game_id]["instance"], Game)

    def test_create_multiple_objects(self, repo: Repo) -> None:
        """Test creating multiple objects."""
        id1 = repo.create(type="team", name="Team 1")
        id2 = repo.create(type="team", name="Team 2")
        id3 = repo.create(type="team", name="Team 3")

        assert id1 == 1
        assert id2 == 2
        assert id3 == 3

    def test_create_invalid_type(self, repo: Repo) -> None:
        """Test creating object with invalid type."""
        with pytest.raises(ValueError):
            repo.create(type="invalid_type")

    def test_create_without_type(self, repo: Repo) -> None:
        """Test creating object without type."""
        with pytest.raises(ValueError):
            repo.create(name="Test")

    def test_list_empty(self, repo: Repo) -> None:
        """Test listing when repo is empty."""
        objects = repo.list()
        assert len(objects) == 0

    def test_list_objects(self, repo: Repo) -> None:
        """Test listing objects."""
        repo.create(type="team", name="Team A")
        repo.create(type="team", name="Team B")

        objects = repo.list()

        assert len(objects) == 2

        # Check format: list of (id, description) tuples
        obj_id, description = objects[0]
        assert isinstance(obj_id, int)
        assert isinstance(description, str)

    def test_attach(self, repo: Repo) -> None:
        """Test attaching to an object."""
        team_id = repo.create(type="team", name="Team")

        result = repo.attach(team_id, "User1")

        assert result["attachment_count"] == 1
        assert "User1" in result["users"]
        assert isinstance(result["instance"], Team)

    def test_attach_multiple_users(self, repo: Repo) -> None:
        """Test multiple users attaching to same object."""
        team_id = repo.create(type="team", name="Team")

        repo.attach(team_id, "User1")
        repo.attach(team_id, "User2")

        obj_data = repo._objects[team_id]
        assert obj_data["attachment_count"] == 2
        assert "User1" in obj_data["users"]
        assert "User2" in obj_data["users"]

    def test_attach_default_user(self, repo: Repo) -> None:
        """Test attaching with default user."""
        team_id = repo.create(type="team", name="Team")

        result = repo.attach(team_id)

        assert "Polat Alemdar" in result["users"]

    def test_detach(self, repo: Repo) -> None:
        """Test detaching from an object."""
        team_id = repo.create(type="team", name="Team")

        repo.attach(team_id, "User1")
        repo.detach(team_id, "User1")

        obj_data = repo._objects[team_id]
        assert obj_data["attachment_count"] == 0
        assert "User1" not in obj_data["users"]

    def test_detach_multiple_users(self, repo: Repo) -> None:
        """Test detaching when multiple users attached."""
        team_id = repo.create(type="team", name="Team")

        repo.attach(team_id, "User1")
        repo.attach(team_id, "User2")
        repo.detach(team_id, "User1")

        obj_data = repo._objects[team_id]
        assert obj_data["attachment_count"] == 1
        assert "User1" not in obj_data["users"]
        assert "User2" in obj_data["users"]

    def test_delete_unattached(self, repo: Repo) -> None:
        """Test deleting an unattached object."""
        team_id = repo.create(type="team", name="Team")

        repo.delete(team_id)

        assert team_id not in repo._objects

    def test_delete_attached_fails(self, repo: Repo) -> None:
        """Test deleting attached object fails."""
        team_id = repo.create(type="team", name="Team")
        repo.attach(team_id, "User1")

        with pytest.raises(ValueError):
            repo.delete(team_id)

    def test_delete_after_detach(self, repo: Repo) -> None:
        """Test deleting after all users detach."""
        team_id = repo.create(type="team", name="Team")

        repo.attach(team_id, "User1")
        repo.detach(team_id, "User1")
        repo.delete(team_id)

        assert team_id not in repo._objects

    def test_listattached_empty(self, repo: Repo) -> None:
        """Test listattached for user with no attachments."""
        repo.create(type="team", name="Team")

        attached = repo.listattached("User1")

        assert len(attached) == 0

    def test_listattached_single_user(self, repo: Repo) -> None:
        """Test listattached for single user."""
        team1_id = repo.create(type="team", name="Team 1")
        team2_id = repo.create(type="team", name="Team 2")

        repo.attach(team1_id, "User1")
        repo.attach(team2_id, "User1")

        attached = repo.listattached("User1")

        assert len(attached) == 2

        # Check format
        obj_id, description = attached[0]
        assert isinstance(obj_id, int)
        assert isinstance(description, str)

    def test_listattached_multiple_users(self, repo: Repo) -> None:
        """Test listattached with multiple users."""
        team1_id = repo.create(type="team", name="Team 1")
        team2_id = repo.create(type="team", name="Team 2")

        repo.attach(team1_id, "User1")
        repo.attach(team2_id, "User2")
        repo.attach(team1_id, "User2")

        user1_attached = repo.listattached("User1")
        user2_attached = repo.listattached("User2")

        assert len(user1_attached) == 1
        assert len(user2_attached) == 2

    def test_listattached_after_detach(self, repo: Repo) -> None:
        """Test listattached after detaching."""
        team_id = repo.create(type="team", name="Team")

        repo.attach(team_id, "User1")
        attached_before = repo.listattached("User1")
        assert len(attached_before) == 1

        repo.detach(team_id, "User1")
        attached_after = repo.listattached("User1")
        assert len(attached_after) == 0

    def test_workflow_scenario(self, repo: Repo) -> None:
        """Test realistic workflow scenario."""
        # User1 creates two teams
        team1_id = repo.create(type="team", name="Galatasaray")
        team2_id = repo.create(type="team", name="Fenerbahçe")

        # User1 attaches to both teams
        repo.attach(team1_id, "User1")
        repo.attach(team2_id, "User1")

        # User2 also attaches to team1
        repo.attach(team1_id, "User2")

        # Check attachments
        user1_objects = repo.listattached("User1")
        user2_objects = repo.listattached("User2")

        assert len(user1_objects) == 2
        assert len(user2_objects) == 1

        # User1 detaches from team1
        repo.detach(team1_id, "User1")

        # User2 still attached, so can't delete
        with pytest.raises(ValueError):
            repo.delete(team1_id)

        # User2 detaches
        repo.detach(team1_id, "User2")

        # Now can delete
        repo.delete(team1_id)

        # Check final state
        all_objects = repo.list()
        assert len(all_objects) == 1  # Only team2 left
