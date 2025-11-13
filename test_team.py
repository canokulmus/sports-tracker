# test_team.py
"""Unit tests for Team class."""
import pytest
from team import Team, PlaceholderTeam


class TestTeam:
    """Test cases for Team class."""
    
    def test_team_creation(self):
        """Test team can be created with a name."""
        team = Team("Galatasaray")
        assert team.team_name == "Galatasaray"
        assert len(team.players) == 0
    
    def test_add_player(self):
        """Test adding a player to team."""
        team = Team("Fenerbahçe")
        team.addplayer("Arda Güler", 10)
        
        assert "Arda Güler" in team.players
        assert team.players["Arda Güler"]["no"] == 10
    
    def test_add_multiple_players(self):
        """Test adding multiple players."""
        team = Team("Beşiktaş")
        team.addplayer("Player1", 1)
        team.addplayer("Player2", 2)
        team.addplayer("Player3", 3)
        
        assert len(team.players) == 3
    
    def test_delete_player(self):
        """Test deleting a player from team."""
        team = Team("Trabzonspor")
        team.addplayer("Player", 5)
        team.delplayer("Player")
        
        assert "Player" not in team.players
        assert len(team.players) == 0
    
    def test_delete_nonexistent_player(self, capsys):
        """Test deleting a player that doesn't exist."""
        team = Team("Team")
        team.delplayer("NonExistent")
        
        captured = capsys.readouterr()
        assert "Warning: Player 'NonExistent' not found" in captured.out
    
    def test_generic_attributes(self):
        """Test setting and getting generic attributes."""
        team = Team("Team")
        team["city"] = "Istanbul"
        team["founded"] = 1905
        
        assert team.city == "Istanbul"
        assert team.founded == 1905
    
    def test_delete_generic_attribute(self):
        """Test deleting generic attributes."""
        team = Team("Team")
        team["country"] = "Turkey"
        
        del team.country
        
        with pytest.raises(AttributeError):
            _ = team.country
    
    def test_str_representation(self):
        """Test string representation of team."""
        team = Team("Galatasaray")
        assert str(team) == "Galatasaray"


class TestPlaceholderTeam:
    """Test cases for PlaceholderTeam class."""
    
    def test_placeholder_creation(self):
        """Test placeholder team creation."""
        placeholder = PlaceholderTeam("Winner of Game 1", [1])
        assert placeholder.team_name == "Winner of Game 1"
        assert placeholder.source_games == [1]
        assert placeholder.is_placeholder is True
    
    def test_placeholder_single_game(self):
        """Test placeholder for single game."""
        placeholder = PlaceholderTeam("Winner of Game 5", [5])
        assert str(placeholder) == "Winner of Game 5"
    
    def test_placeholder_multiple_games(self):
        """Test placeholder for multiple games."""
        placeholder = PlaceholderTeam("Winner", [1, 2])
        assert "Winner of Games [1, 2]" in str(placeholder)