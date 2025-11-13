# test_cup.py
"""Unit tests for Cup class."""

import pytest
from datetime import timedelta
from typing import List
from team import Team
from cup import Cup, CupType


class TestCupLeague:
    """Test cases for LEAGUE type cups."""

    @pytest.fixture
    def teams(self) -> List[Team]:
        """Create teams for testing."""
        return [Team("Team A"), Team("Team B"), Team("Team C"), Team("Team D")]

    def test_league_creation(self, teams: List[Team]) -> None:
        """Test LEAGUE cup creation."""
        cup = Cup(teams, CupType.LEAGUE, interval=timedelta(days=1))

        assert cup.type == CupType.LEAGUE
        assert len(cup.teams) == 4
        # 4 teams: C(4,2) = 6 games
        assert len(cup.games) == 6

    def test_league2_creation(self, teams: List[Team]) -> None:
        """Test LEAGUE2 cup creation (double matches)."""
        cup = Cup(teams, CupType.LEAGUE2, interval=timedelta(days=1))

        # 4 teams: C(4,2) * 2 = 12 games
        assert len(cup.games) == 12

    def test_search_all_games(self, teams: List[Team]) -> None:
        """Test searching all games."""
        cup = Cup(teams, CupType.LEAGUE, interval=timedelta(days=1))
        all_games = cup.search()

        assert len(all_games) == len(cup.games)

    def test_search_by_team(self, teams: List[Team]) -> None:
        """Test searching games by team name."""
        cup = Cup(teams, CupType.LEAGUE, interval=timedelta(days=1))
        team_a_games = cup.search(tname="Team A")

        # Team A plays against 3 other teams
        assert len(team_a_games) == 3

        # Check Team A is in each game
        for game in team_a_games:
            assert (
                game.home().team_name == "Team A" or game.away().team_name == "Team A"
            )

    def test_getitem(self, teams: List[Team]) -> None:
        """Test accessing game by ID."""
        cup = Cup(teams, CupType.LEAGUE, interval=timedelta(days=1))

        game1 = cup[1]
        assert game1.id() == 1

        game2 = cup[2]
        assert game2.id() == 2

    def test_getitem_invalid_id(self, teams: List[Team]) -> None:
        """Test accessing non-existent game."""
        cup = Cup(teams, CupType.LEAGUE, interval=timedelta(days=1))

        with pytest.raises(KeyError):
            _ = cup[999]

    def test_league_standings_no_games(self, teams: List[Team]) -> None:
        """Test standings before any games played."""
        cup = Cup(teams, CupType.LEAGUE, interval=timedelta(days=1))
        standings = cup.standings()

        assert len(standings) == 4

        # All teams should have 0 points
        for _, won, draw, lost, gf, ga, pts in standings:  # type: ignore
            assert won == 0
            assert draw == 0
            assert lost == 0
            assert gf == 0
            assert ga == 0
            assert pts == 0

    def test_league_standings_after_games(self, teams: List[Team]) -> None:
        """Test standings after playing games."""
        for team in teams:
            team.addplayer("Player", 10)

        cup = Cup(teams, CupType.LEAGUE, interval=timedelta(days=1))

        # Play first game: Team A wins
        game1 = cup[1]
        game1.start()
        game1.score(3, game1.home(), "Player")
        game1.score(1, game1.away(), "Player")
        game1.end()

        standings = cup.standings()

        # Winner should have 2 points
        winner_name: str = game1.home().team_name
        winner_standing = next(s for s in standings if s[0] == winner_name)  # type: ignore
        _, won, draw, lost, gf, ga, pts = winner_standing  # type: ignore

        assert won == 1
        assert pts == 2
        assert gf == 3
        assert ga == 1

    def test_watch_observer(self, teams: List[Team]) -> None:
        """Test observer pattern on cup."""

        class TestObserver:
            def __init__(self):
                self.update_count = 0

            def update(self, game):
                self.update_count += 1

        cup = Cup(teams, CupType.LEAGUE, interval=timedelta(days=1))
        observer = TestObserver()

        cup.watch(observer)

        # Start and end a game
        game = cup[1]
        game.start()
        game.end()

        assert observer.update_count == 2


class TestCupElimination:
    """Test cases for ELIMINATION type cups."""

    @pytest.fixture
    def teams(self) -> List[Team]:
        """Create teams for testing."""
        return [Team(f"Team {i}") for i in range(1, 9)]

    def test_elimination_creation(self, teams: List[Team]) -> None:
        """Test ELIMINATION cup creation."""
        cup = Cup(teams, CupType.ELIMINATION, interval=timedelta(days=1))

        assert cup.type == CupType.ELIMINATION
        # 8 teams: should create multiple rounds
        assert len(cup.rounds) > 1
        assert len(cup.games) > 0

    def test_elimination_rounds(self, teams: List[Team]) -> None:
        """Test ELIMINATION has correct number of rounds."""
        cup = Cup(teams, CupType.ELIMINATION, interval=timedelta(days=1))

        # 8 teams: 3 rounds (QF, SF, F)
        # Round 1: 4 games, Round 2: 2 games, Round 3: 1 game = 7 total
        assert len(cup.rounds) == 3
        assert len(cup.games) == 7

    def test_elimination2_double_games(self) -> None:
        """Test ELIMINATION2 creates double games."""
        teams = [Team(f"Team {i}") for i in range(1, 5)]
        cup = Cup(teams, CupType.ELIMINATION2, interval=timedelta(days=1))

        # 4 teams: 2 matchups * 2 games each = 4 games first round
        # Then 1 matchup * 2 games = 2 games
        # Total = 6 games
        assert len(cup.games) == 6

    def test_elimination_standings(self) -> None:
        """Test ELIMINATION standings."""
        teams = [Team(f"Team {i}") for i in range(1, 5)]
        for team in teams:
            team.addplayer("Player", 10)

        cup = Cup(teams, CupType.ELIMINATION, interval=timedelta(days=1))

        # Play first round
        for game in cup.rounds[0]:
            game.start()
            game.score(10, game.home(), "Player")
            game.score(5, game.away(), "Player")
            game.end()

        standings = cup.standings()

        # Check format
        assert isinstance(standings, dict)  # type: ignore

        # Winners should have 1 win
        for team_name, info in standings.items():  # type: ignore
            if len(info["Won"]) == 1:
                assert info["Round"] == 1
                assert info["Lost"] is None

    def test_gametree_elimination(self, teams: List[Team]) -> None:
        """Test gametree for ELIMINATION."""
        cup = Cup(teams, CupType.ELIMINATION, interval=timedelta(days=1))
        tree = cup.gametree()

        # Should have round names
        assert "Quarter-Final" in tree
        assert "Semi-Final" in tree
        assert "Final" in tree

        # Check structure
        assert len(tree["Quarter-Final"]) == 4
        assert len(tree["Semi-Final"]) == 2
        assert len(tree["Final"]) == 1


class TestCupGroup:
    """Test cases for GROUP type cups."""

    @pytest.fixture
    def teams(self) -> List[Team]:
        """Create 16 teams for GROUP tournament."""
        return [Team(f"Team {i}") for i in range(1, 17)]

    def test_group_creation(self, teams: List[Team]) -> None:
        """Test GROUP cup creation."""
        cup = Cup(
            teams,
            CupType.GROUP,
            interval=timedelta(days=1),
            num_groups=4,
            playoff_teams=8,
        )

        assert cup.type == CupType.GROUP
        assert len(cup.groups) == 4

        # Each group should have 4 teams
        for group_teams in cup.groups.values():
            assert len(group_teams) == 4

    def test_group_games(self, teams: List[Team]) -> None:
        """Test GROUP creates correct number of games."""
        cup = Cup(
            teams,
            CupType.GROUP,
            interval=timedelta(days=1),
            num_groups=4,
            playoff_teams=8,
        )

        # 4 groups * C(4,2) = 4 * 6 = 24 games
        assert len(cup.games) == 24

        # Each group should have 6 games
        for group_games in cup.group_games.values():
            assert len(group_games) == 6

    def test_group_standings(self, teams: List[Team]) -> None:
        """Test GROUP standings structure."""
        for team in teams:
            team.addplayer("Player", 10)

        cup = Cup(
            teams,
            CupType.GROUP,
            interval=timedelta(days=1),
            num_groups=4,
            playoff_teams=8,
        )

        standings = cup.standings()

        # Should have Groups and Playoffs
        assert "Groups" in standings  # type: ignore
        assert "Playoffs" in standings  # type: ignore

        # Should have 4 groups
        assert len(standings["Groups"]) == 4  # type: ignore

    def test_group_gametree(self, teams: List[Team]) -> None:
        """Test GROUP gametree structure."""
        cup = Cup(
            teams,
            CupType.GROUP,
            interval=timedelta(days=1),
            num_groups=4,
            playoff_teams=8,
        )

        tree = cup.gametree()

        # Should have Groups and Playoffs
        assert "Groups" in tree  # type: ignore
        assert "Playoffs" in tree  # type: ignore

        # Should have 4 groups
        assert len(tree["Groups"]) == 4  # type: ignore


class TestCupErrors:
    """Test error handling in Cup class."""

    def test_gametree_wrong_type(self) -> None:
        """Test gametree raises error for LEAGUE."""
        teams = [Team(f"Team {i}") for i in range(1, 5)]
        cup = Cup(teams, CupType.LEAGUE, interval=timedelta(days=1))

        with pytest.raises(ValueError):
            cup.gametree()
