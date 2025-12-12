# test_game.py
"""Unit tests for Game class."""

import pytest
from datetime import datetime
from typing import Any, Tuple
from team import Team
from game import Game
from constants import GameState


class TestGame:
    """Test cases for Game class."""

    @pytest.fixture
    def teams(self) -> Tuple[Team, Team]:
        """Create two teams for testing."""
        home = Team("Home Team")
        home.addplayer("Player1", 10)
        away = Team("Away Team")
        away.addplayer("Player2", 11)
        return home, away

    @pytest.fixture
    def game(self, teams: Tuple[Team, Team]) -> Game:
        """Create a game for testing."""
        home, away = teams
        return Game(home, away, id_=1, datetime=datetime.now())

    def test_game_creation(self, game: Game, teams: Tuple[Team, Team]) -> None:
        """Test game can be created."""
        home, away = teams
        assert game.home() == home
        assert game.away() == away
        assert game.id() == 1
        assert game.state == GameState.READY

    def test_game_start(self, game: Game, capsys: pytest.CaptureFixture[str]) -> None:
        """Test starting a game."""
        game.start()
        captured = capsys.readouterr()

        assert game.state == GameState.RUNNING
        assert "Game started" in captured.out

    def test_game_start_twice(
        self, game: Game, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """Test starting an already running game."""
        game.start()
        game.start()
        captured = capsys.readouterr()

        assert "Game is already running" in captured.out

    def test_game_pause(self, game: Game, capsys: pytest.CaptureFixture[str]) -> None:
        """Test pausing a game."""
        game.start()
        game.pause()
        captured = capsys.readouterr()

        assert game.state == GameState.PAUSED
        assert "Game paused" in captured.out

    def test_game_resume(self, game: Game, capsys: pytest.CaptureFixture[str]) -> None:
        """Test resuming a paused game."""
        game.start()
        game.pause()
        game.resume()
        captured = capsys.readouterr()

        assert game.state == GameState.RUNNING
        assert "Game resumed" in captured.out

    def test_game_end(self, game: Game, capsys: pytest.CaptureFixture[str]) -> None:
        """Test ending a game."""
        game.start()
        game.end()
        captured = capsys.readouterr()

        assert game.state == GameState.ENDED
        assert "Game has ended" in captured.out

    def test_score_when_running(
        self, game: Game, teams: Tuple[Team, Team], capsys: pytest.CaptureFixture[str]
    ) -> None:
        """Test scoring during running game."""
        home, _ = teams
        game.start()
        game.score(2, home, "Player1")
        captured = capsys.readouterr()

        assert game.home_score == 2
        assert "Home Team scored 2 points" in captured.out

    def test_score_when_not_running(
        self, game: Game, teams: Tuple[Team, Team], capsys: pytest.CaptureFixture[str]
    ) -> None:
        """Test scoring when game is not running."""
        home, _ = teams
        game.score(2, home, "Player1")
        captured = capsys.readouterr()

        assert game.home_score == 0
        assert "Cannot score, game is not running" in captured.out

    def test_score_both_teams(self, game: Game, teams: Tuple[Team, Team]) -> None:
        """Test both teams can score."""
        home, away = teams
        game.start()
        game.score(3, home, "Player1")
        game.score(2, away, "Player2")

        assert game.home_score == 3
        assert game.away_score == 2

    def test_player_score_tracking(self, game: Game, teams: Tuple[Team, Team]) -> None:
        """Test individual player scores are tracked."""
        home, _ = teams
        game.start()
        game.score(5, home, "Player1")

        assert game.home_players["Player1"]["score"] == 5

    def test_timeline_tracking(self, game: Game, teams: Tuple[Team, Team]) -> None:
        """Test timeline is recorded."""
        home, _ = teams
        game.start()
        game.score(2, home, "Player1")

        assert len(game.timeline) == 1
        _, team_type, player, points = game.timeline[0]
        assert team_type == "Home"
        assert player == "Player1"
        assert points == 2

    def test_stats_ready_state(self, game: Game) -> None:
        """Test stats when game is ready."""
        stats = game.stats()

        assert stats["Home"]["Pts"] == 0
        assert stats["Away"]["Pts"] == 0
        assert stats["Time"] == "00:00.00"

    def test_stats_after_end(self, game: Game, teams: Tuple[Team, Team]) -> None:
        """Test stats after game ends."""
        home, _ = teams
        game.start()
        game.score(10, home, "Player1")
        game.end()

        stats = game.stats()
        assert stats["Home"]["Pts"] == 10
        assert stats["Time"] == "Full Time"

    def test_observer_pattern(self, game: Game) -> None:
        """Test observer pattern works."""

        class TestObserver:
            def __init__(self):
                self.update_count = 0

            def update(self, game):
                self.update_count += 1

        observer = TestObserver()
        game.watch(observer)

        game.start()
        game.end()

        assert observer.update_count == 2

    def test_unwatch_observer(self, game: Game) -> None:
        """Test removing observer."""

        class TestObserver:
            def __init__(self):
                self.update_count = 0

            def update(self, game: Game) -> None:
                self.update_count += 1

        observer = TestObserver()
        game.watch(observer)
        game.unwatch(observer)

        game.start()

        assert observer.update_count == 0
