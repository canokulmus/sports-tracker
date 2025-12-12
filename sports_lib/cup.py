# cup.py
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
from itertools import combinations
from constants import GameState, CupType
from game import Game
from team import Team, PlaceholderTeam
import random
import string


class Cup:
    """A container for a collection of games (e.g., a tournament)."""

    def __init__(
        self,
        teams: List[Team],
        type: str,
        interval: timedelta,
        num_groups: int = 4,
        playoff_teams: int = 8,
        repo: Optional[Any] = None,  # <--- Add this argument
    ) -> None:
        """Initializes a tournament, generating all its games based on the format."""
        self.repo = repo  # <--- Store the repo reference
        self.teams = teams
        self.type = type
        self.interval = interval
        self.games: List[Game] = []
        self._observers: List[Any] = []
        self._game_id_counter = 1
        self._current_date = datetime.now()

        # Elimination-specific structure to hold rounds of games.
        self.rounds: List[List[Game]] = []

        # Group-specific attributes.
        self.num_groups = num_groups
        self.playoff_teams = playoff_teams
        self.groups: Dict[str, List[Team]] = {}
        self.group_games: Dict[str, List[Game]] = {}
        self.playoff_games: List[Game] = []

        self._generate_games()

    def __getitem__(self, gameid: int) -> Game:
        """Provides dictionary-style access to games by their ID."""
        for game in self.games:
            if game.id() == gameid:
                return game

        raise KeyError(f"Game with ID {gameid} not found in this cup")

    # Add this method
    def __getstate__(self):
        state = self.__dict__.copy()
        state["_observers"] = []
        return state

    # Add this method
    def __setstate__(self, state):
        self.__dict__.update(state)
        if "_observers" not in self.__dict__:
            self._observers = []

    def __str__(self) -> str:
        """Returns a human-readable summary of the cup."""
        return f"Cup Tournament: {self.type} with {len(self.teams)} teams, {len(self.games)} games"

    def _generate_games(self) -> None:
        """Delegates game generation to the appropriate method based on cup type."""
        if self.type == CupType.LEAGUE:
            self._generate_league(double=False)
        elif self.type == CupType.LEAGUE2:
            self._generate_league(double=True)
        elif self.type == CupType.ELIMINATION:
            self._generate_elimination(double=False)
        elif self.type == CupType.ELIMINATION2:
            self._generate_elimination(double=True)
        elif self.type == CupType.GROUP:
            self._generate_group(double=False)
        elif self.type == CupType.GROUP2:
            self._generate_group(double=True)
        else:
            raise ValueError(f"Unknown cup type: {self.type}")

    def _generate_league(self, double: bool = False) -> None:
        """Generates round-robin league matches with proper scheduling.

        Uses the Round-Robin algorithm to ensure each team plays one game per round,
        avoiding back-to-back matches for any team.
        """
        import copy

        teams = copy.copy(self.teams)
        n = len(teams)

        # If odd number of teams, add a "bye" (dummy team)
        if n % 2 == 1:
            teams.append(None)  # None = bye
            n += 1

        current_date = self._current_date

        # Round-Robin algorithm: n-1 rounds for n teams
        for round_num in range(n - 1):
            # Create matches for this round
            for i in range(n // 2):
                home_idx = i
                away_idx = n - 1 - i

                home_team = teams[home_idx]
                away_team = teams[away_idx]

                # Skip if either team is None (bye)
                if home_team is None or away_team is None:
                    continue

                # Create game
                game = self._create_game_instance(
                    home=home_team, away=away_team, datetime=current_date
                )
                self.games.append(game)

            # Move to next round date
            current_date += self.interval

            # Rotate teams (keep first team fixed, rotate others)
            teams = [teams[0]] + [teams[-1]] + teams[1:-1]

        # If double league, create reverse fixtures
        if double:
            first_round_count = len(self.games)
            for i in range(first_round_count):
                original_game = self.games[i]
                # Create reverse fixture (swap home/away)
                game2 = Game(
                    home=original_game.away(),
                    away=original_game.home(),
                    id_=self._game_id_counter,
                    datetime=current_date,
                )
                self.games.append(game2)
                self._game_id_counter += 1
                current_date += self.interval

    def _create_game_instance(self, home, away, datetime, group=None) -> Game:
        """Helper to create a game via Repo if available, or standalone otherwise."""
        if self.repo:
            # SERVER MODE: Register with Repo to get a Global ID
            game_id = self.repo.create(
                type="game", home=home, away=away, datetime=datetime, group=group
            )
            # Fetch the actual game object back from the repo
            return self.repo._objects[game_id]["instance"]
        else:
            # STANDALONE MODE: Use internal counter (for unit tests)
            game = Game(
                home=home,
                away=away,
                id_=self._game_id_counter,
                datetime=datetime,
                group=group,
            )
            self._game_id_counter += 1
            return game

    def search(
        self,
        tname: Optional[str] = None,
        group: Optional[str] = None,
        between: Optional[Tuple[datetime, datetime]] = None,
    ) -> List[Game]:
        """Filters and returns games based on specified criteria."""
        results: List[Game] = []

        for game in self.games:
            matches = True

            if tname is not None:
                home_match = game.home().team_name.lower() == tname.lower()
                away_match = game.away().team_name.lower() == tname.lower()
                if not (home_match or away_match):
                    matches = False

            if between is not None and matches:
                start_date, end_date = between
                if not (start_date <= game.datetime <= end_date):
                    matches = False

            if group is not None and matches:
                if game.group != group:
                    matches = False

            if matches:
                results.append(game)

        return results

    def standings(
        self,
    ) -> Dict[str, Any] | List[Tuple[str, int, int, int, int, int, int]]:
        """Calculates and returns the standings for the tournament.

        The structure of the returned data depends on the tournament type,
        providing a league table, an elimination bracket summary, or a
        group stage breakdown.
        """
        if self.type in [CupType.LEAGUE, CupType.LEAGUE2]:
            return self._calculate_league_standings()
        elif self.type in [CupType.ELIMINATION, CupType.ELIMINATION2]:
            return self._calculate_elimination_standings()
        elif self.type in [CupType.GROUP, CupType.GROUP2]:
            return self._calculate_group_standings_full()
        else:
            raise ValueError(f"Unknown cup type: {self.type}")

    def _calculate_group_standings_full(self) -> Dict[str, Any]:
        """Aggregates standings for all groups and the playoff stage."""
        result: Dict[str, Any] = {"Groups": {}, "Playoffs": {}}

        for group_name in sorted(self.groups.keys()):
            standings = self._calculate_group_standings(group_name)
            result["Groups"][group_name] = standings

        if len(self.playoff_games) > 0:
            # Placeholder for playoff standings logic.
            result["Playoffs"] = "Not yet implemented"

        return result

    def _calculate_league_standings(
        self,
    ) -> List[Tuple[str, int, int, int, int, int, int]]:
        """Calculates a sorted league table based on game results."""
        stats: Dict[str, Dict[str, int]] = {}

        for team in self.teams:
            stats[team.team_name] = {
                "won": 0,
                "draw": 0,
                "lost": 0,
                "goals_for": 0,
                "goals_against": 0,
                "points": 0,
            }

        for game in self.games:
            # Standings should only reflect completed games.
            if game.state != GameState.ENDED:
                continue

            home_team = game.home().team_name
            away_team = game.away().team_name
            home_score = game.home_score
            away_score = game.away_score

            stats[home_team]["goals_for"] += home_score
            stats[home_team]["goals_against"] += away_score
            stats[away_team]["goals_for"] += away_score
            stats[away_team]["goals_against"] += home_score

            if home_score > away_score:
                stats[home_team]["won"] += 1
                stats[home_team]["points"] += 2
                stats[away_team]["lost"] += 1
            elif home_score < away_score:
                stats[away_team]["won"] += 1
                stats[away_team]["points"] += 2
                stats[home_team]["lost"] += 1
            else:
                # draw
                stats[home_team]["draw"] += 1
                stats[home_team]["points"] += 1  # draw = 1 point
                stats[away_team]["draw"] += 1
                stats[away_team]["points"] += 1

        standings_list: List[Tuple[str, int, int, int, int, int, int]] = []
        for team_name, team_stats in stats.items():
            standings_list.append(
                (
                    team_name,
                    team_stats["won"],
                    team_stats["draw"],
                    team_stats["lost"],
                    team_stats["goals_for"],
                    team_stats["goals_against"],
                    team_stats["points"],
                )
            )

        # Sort by points, then by goal difference as a tie-breaker.
        standings_list.sort(key=lambda x: (x[6], x[4] - x[5]), reverse=True)

        return standings_list

    def watch(self, obj: Any, **searchparams: Any) -> None:
        """Adds an observer to games matching the given search parameters."""
        observer_entry = {"observer": obj, "params": searchparams}
        if observer_entry not in self._observers:
            self._observers.append(observer_entry)

        # Attach the observer to all existing and future games that match.
        matching_games = self.search(**searchparams)
        for game in matching_games:
            game.watch(obj)

    def unwatch(self, obj: Any) -> None:
        """Removes an observer from all games in the cup."""
        self._observers = [
            entry for entry in self._observers if entry["observer"] != obj
        ]

        # Remove the observer from all games
        for game in self.games:
            game.unwatch(obj)

    def _generate_elimination(self, double: bool = False) -> None:
        """Generates a multi-round elimination (knockout) bracket.

        This method builds the tournament round by round, using PlaceholderTeam
        objects to represent the winners of future games. It handles byes for
        tournaments with an odd number of teams.
        """
        shuffled_teams: List[Team] = self.teams.copy()
        random.shuffle(shuffled_teams)

        bye_team: Optional[Team] = None
        if len(shuffled_teams) % 2 == 1:
            bye_team = shuffled_teams.pop()
            print(f"   {bye_team.team_name} has a bye (advances without playing).")

        current_round = self._create_elimination_round(
            shuffled_teams, double, is_first_round=True
        )
        self.rounds.append(current_round)
        self.games.extend(current_round)

        next_round_teams: List[Team] = []

        if bye_team is not None:
            next_round_teams.append(bye_team)

        for i in range(0, len(current_round), 2 if double else 1):
            if double:
                game1_id = current_round[i].id()
                game2_id = current_round[i + 1].id()
                placeholder = PlaceholderTeam(
                    f"Winner of Games {game1_id} & {game2_id}", [game1_id, game2_id]
                )
            else:
                game_id = current_round[i].id()
                placeholder = PlaceholderTeam(f"Winner of Game {game_id}", [game_id])
            next_round_teams.append(placeholder)

        while len(next_round_teams) > 1:
            round_bye: Optional[Team] = None
            if len(next_round_teams) % 2 == 1:
                round_bye = next_round_teams.pop()
                print(f"   {round_bye.team_name} has a bye in this round.")

            next_round = self._create_elimination_round(
                next_round_teams, double, is_first_round=False
            )
            self.rounds.append(next_round)
            self.games.extend(next_round)

            next_round_teams = []

            if round_bye is not None:
                next_round_teams.append(round_bye)

            for i in range(0, len(next_round), 2 if double else 1):
                if double:
                    game1_id = next_round[i].id()
                    game2_id = next_round[i + 1].id()
                    placeholder = PlaceholderTeam(
                        f"Winner of Games {game1_id} & {game2_id}", [game1_id, game2_id]
                    )
                else:
                    game_id = next_round[i].id()
                    placeholder = PlaceholderTeam(
                        f"Winner of Game {game_id}", [game_id]
                    )
                next_round_teams.append(placeholder)

    def _create_elimination_round(
        self, teams: List[Team], double: bool, is_first_round: bool
    ) -> List[Game]:
        """Helper to create the games for a single elimination round."""
        round_games: List[Game] = []

        # Add a longer delay between rounds for realism.
        if not is_first_round:
            self._current_date += self.interval * 2

        current_date = self._current_date

        for i in range(0, len(teams), 2):
            home_team = teams[i]
            away_team = teams[i + 1]

            # First leg
            game = self._create_game_instance(
                home=home_team, away=away_team, datetime=current_date
            )
            round_games.append(game)
            current_date += self.interval

            if double:
                game2 = Game(
                    home=away_team,
                    away=home_team,
                    id_=self._game_id_counter,
                    datetime=current_date,
                )
                round_games.append(game2)
                self._game_id_counter += 1
                current_date += self.interval

        return round_games

    def gametree(self) -> Dict[str, List[Dict[str, Any]]]:
        """Generates a structured view of the tournament bracket.

        This is only applicable for formats with distinct rounds or stages,
        like ELIMINATION and GROUP tournaments.
        """
        if self.type not in [
            CupType.ELIMINATION,
            CupType.ELIMINATION2,
            CupType.GROUP,
            CupType.GROUP2,
        ]:
            raise ValueError(
                f"gametree() is only available for ELIMINATION and GROUP types, not {self.type}"
            )

        if self.type in [CupType.ELIMINATION, CupType.ELIMINATION2]:
            return self._gametree_elimination()
        else:  # GROUP or GROUP2
            return self._gametree_group()

    def _gametree_elimination(self) -> Dict[str, List[Dict[str, Any]]]:
        """Builds the game tree specifically for an elimination bracket."""
        tree: Dict[str, List[Dict[str, Any]]] = {}

        round_names = self._get_round_names(len(self.rounds))

        for round_num, round_games in enumerate(self.rounds):
            round_name = round_names[round_num]
            tree[round_name] = []

            for game in round_games:
                game_info = {
                    "game_id": game.id(),
                    "home": game.home().team_name,
                    "away": game.away().team_name,
                    "datetime": game.datetime.strftime("%Y-%m-%d %H:%M"),
                }
                tree[round_name].append(game_info)

        return tree

    def _get_round_names(self, total_rounds: int) -> List[str]:
        """Provides conventional names for tournament rounds (e.g., Final)."""
        if total_rounds == 1:
            return ["Final"]
        elif total_rounds == 2:
            return ["Semi-Final", "Final"]
        elif total_rounds == 3:
            return ["Quarter-Final", "Semi-Final", "Final"]
        elif total_rounds == 4:
            return ["Round of 16", "Quarter-Final", "Semi-Final", "Final"]
        elif total_rounds == 5:
            return [
                "Round of 32",
                "Round of 16",
                "Quarter-Final",
                "Semi-Final",
                "Final",
            ]
        else:
            # Fallback for very large tournaments.
            names: List[str] = []
            for i in range(total_rounds - 3):
                names.append(f"Round {i + 1}")
            names.extend(["Quarter-Final", "Semi-Final", "Final"])
            return names

    def _calculate_elimination_standings(self) -> Dict[str, Dict[str, Any]]:
        """Summarizes each team's progress through the elimination bracket."""
        standings: Dict[str, Dict[str, Any]] = {}

        for team in self.teams:
            # Initialize stats for real teams only.
            standings[team.team_name] = {"Round": 0, "Won": [], "Lost": None}

        # Check each round and update standings
        for round_num, round_games in enumerate(self.rounds, 1):
            for game in round_games:
                # Skip games involving placeholders as they haven't been played.
                if isinstance(game.home_, PlaceholderTeam) or isinstance(
                    game.away_, PlaceholderTeam
                ):
                    continue

                home_name = game.home().team_name
                away_name = game.away().team_name

                if home_name in standings:
                    standings[home_name]["Round"] = round_num
                if away_name in standings:
                    standings[away_name]["Round"] = round_num

                if game.state == GameState.ENDED:
                    home_score = game.home_score
                    away_score = game.away_score

                    if home_score > away_score:
                        if home_name in standings:
                            standings[home_name]["Won"].append(
                                (away_name, home_score, away_score)
                            )
                        if away_name in standings:
                            standings[away_name]["Lost"] = (
                                home_name,
                                away_score,
                                home_score,
                            )
                    elif away_score > home_score:
                        if away_name in standings:
                            standings[away_name]["Won"].append(
                                (home_name, away_score, home_score)
                            )
                        if home_name in standings:
                            standings[home_name]["Lost"] = (
                                away_name,
                                home_score,
                                away_score,
                            )

        return standings

    def _generate_group(self, double: bool = False) -> None:
        """Generates the group stage of a tournament.

        This method shuffles teams, divides them into a specified number of
        groups, and then creates a round-robin league within each group.
        """
        shuffled_teams = self.teams.copy()
        random.shuffle(shuffled_teams)

        # Split teams into groups
        teams_per_group = len(shuffled_teams) // self.num_groups

        group_names = list(string.ascii_uppercase[: self.num_groups])  # A, B, C, ...

        print(
            f"\nGROUP TOURNAMENT: {self.num_groups} groups, {teams_per_group} teams per group."
        )

        for i, group_name in enumerate(group_names):
            start_idx = i * teams_per_group
            end_idx = start_idx + teams_per_group
            group_teams = shuffled_teams[start_idx:end_idx]

            self.groups[group_name] = group_teams

            team_names = ", ".join([t.team_name for t in group_teams])
            print(f"\n   Group {group_name}: {team_names}")

            group_games = self._create_group_league(group_teams, group_name, double)
            self.group_games[group_name] = group_games
            self.games.extend(group_games)

        # The playoff bracket is generated later, after group games are played.
        print(f"\n   Playoff: {self.playoff_teams} teams will advance.")
        print(
            "   Playoff matches will be determined after the group stage is completed."
        )

    def _create_group_league(
        self, group_teams: List[Team], group_name: str, double: bool
    ) -> List[Game]:
        """Helper to create round-robin matches for a single group."""
        group_games: List[Game] = []
        current_date = self._current_date

        pairs = list(combinations(group_teams, 2))

        for home_team, away_team in pairs:
            game = self._create_game_instance(
                home=home_team, away=away_team, datetime=current_date, group=group_name
            )
            group_games.append(game)
            current_date += self.interval

            # If double, create the reverse fixture.
            if double:
                game2 = Game(
                    home=away_team,
                    away=home_team,
                    id_=self._game_id_counter,
                    datetime=current_date,
                    group=group_name,
                )
                group_games.append(game2)
                self._game_id_counter += 1
                current_date += self.interval

        return group_games

    def _calculate_group_standings(
        self, group_name: str
    ) -> List[Tuple[str, int, int, int, int, int, int]]:
        """Calculates the league table for a single group."""
        group_teams = self.groups[group_name]

        stats: Dict[str, Dict[str, int]] = {}
        for team in group_teams:
            stats[team.team_name] = {
                "won": 0,
                "draw": 0,
                "lost": 0,
                "goals_for": 0,
                "goals_against": 0,
                "points": 0,
            }

        group_games = self.group_games[group_name]

        for game in group_games:
            if game.state != GameState.ENDED:
                continue

            home_team = game.home().team_name
            away_team = game.away().team_name
            home_score = game.home_score
            away_score = game.away_score

            stats[home_team]["goals_for"] += home_score
            stats[home_team]["goals_against"] += away_score
            stats[away_team]["goals_for"] += away_score
            stats[away_team]["goals_against"] += home_score

            if home_score > away_score:
                stats[home_team]["won"] += 1
                stats[home_team]["points"] += 2
                stats[away_team]["lost"] += 1
            elif home_score < away_score:
                stats[away_team]["won"] += 1
                stats[away_team]["points"] += 2
                stats[home_team]["lost"] += 1
            else:
                stats[home_team]["draw"] += 1
                stats[home_team]["points"] += 1
                stats[away_team]["draw"] += 1
                stats[away_team]["points"] += 1

        standings_list: List[Tuple[str, int, int, int, int, int, int]] = []
        for team_name, team_stats in stats.items():
            standings_list.append(
                (
                    team_name,
                    team_stats["won"],
                    team_stats["draw"],
                    team_stats["lost"],
                    team_stats["goals_for"],
                    team_stats["goals_against"],
                    team_stats["points"],
                )
            )

        standings_list.sort(key=lambda x: (x[6], x[4] - x[5]), reverse=True)

        return standings_list

    def generate_playoffs(self) -> None:
        """Generates the playoff bracket after the group stage is complete.

        This method determines which teams qualify based on group rankings and
        wild card rules, then creates an elimination-style bracket for them.
        """
        if self.type not in [CupType.GROUP, CupType.GROUP2]:
            raise ValueError("generate_playoffs() only works for GROUP tournaments")

        k = self.playoff_teams // self.num_groups
        wild_card_count = self.playoff_teams - (k * self.num_groups)

        print("\nPLAYOFF GENERATION")
        print(f"   Each group sends top {k} team(s).")
        print(f"   Plus {wild_card_count} wild card team(s).")

        playoff_teams: List[Team] = []
        all_qualified: List[Tuple[Team, int, str]] = []  # (team, points, group)

        for group_name in sorted(self.groups.keys()):
            standings = self._calculate_group_standings(group_name)

            print(f"\n   Group {group_name} Standings:")
            for i, (team_name, _, _, _, _, _, pts) in enumerate(standings, 1):
                print(f"      {i}. {team_name}: {pts} pts")

                if i <= k:
                    # Automatically qualify the top k teams from each group.
                    team_obj = next(
                        t for t in self.groups[group_name] if t.team_name == team_name
                    )
                    playoff_teams.append(team_obj)
                    print(f"          Qualified (top {k}).")
                else:
                    # Remaining teams are candidates for wild card spots.
                    team_obj = next(
                        t for t in self.groups[group_name] if t.team_name == team_name
                    )
                    all_qualified.append((team_obj, pts, group_name))

        if wild_card_count > 0:
            # Sort remaining teams by points to find the best runners-up.
            all_qualified.sort(key=lambda x: x[1], reverse=True)

            print("\n   Wild Card Candidates:")
            for team, pts, grp in all_qualified[:wild_card_count]:
                print(
                    f"      {team.team_name} (from Group {grp}): {pts} pts - Qualified."
                )
                playoff_teams.append(team)

        print(f"\n   Total playoff teams: {len(playoff_teams)}.")

        double = self.type == CupType.GROUP2

        # Add a break before the playoffs start.
        self._current_date += self.interval * 3

        random.shuffle(playoff_teams)

        playoff_round = self._create_elimination_round(
            playoff_teams, double, is_first_round=True
        )
        self.playoff_games = playoff_round
        self.games.extend(playoff_round)

        print(f"\n   Playoff Round 1: {len(playoff_round)} games created.")

    def _gametree_group(self) -> Dict[str, Any]:
        """Builds the game tree for a group-based tournament."""
        tree: Dict[str, Any] = {"Groups": {}, "Playoffs": {}}

        for group_name in sorted(self.groups.keys()):
            tree["Groups"][group_name] = []

            group_games = self.group_games[group_name]
            for game in group_games:
                game_info = {
                    "game_id": game.id(),
                    "home": game.home().team_name,
                    "away": game.away().team_name,
                    "datetime": game.datetime.strftime("%Y-%m-%d %H:%M"),
                }
                tree["Groups"][group_name].append(game_info)

        if len(self.playoff_games) > 0:
            # This logic assumes a simple single-round playoff for now, but
            # calculates the number of rounds for future expansion.
            num_playoff_teams = len(self.playoff_games) * 2
            num_playoff_rounds = 0
            temp = num_playoff_teams
            while temp > 1:
                temp //= 2
                num_playoff_rounds += 1

            round_names = self._get_round_names(num_playoff_rounds)

            # Currently, only the first playoff round is populated.
            tree["Playoffs"][round_names[0]] = []

            for game in self.playoff_games:
                game_info = {
                    "game_id": game.id(),
                    "home": game.home().team_name,
                    "away": game.away().team_name,
                    "datetime": game.datetime.strftime("%Y-%m-%d %H:%M"),
                }
                tree["Playoffs"][round_names[0]].append(game_info)

        return tree
