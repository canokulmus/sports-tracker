# cup.py
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
from itertools import combinations
from .constants import GameState, CupType
from .game import Game
from .team import Team, PlaceholderTeam
import random
import string


class Cup:
    """A container for a collection of games (e.g., a tournament)."""

    def __init__(
        self,
        teams: List[Team],
        cup_type: str,
        interval: timedelta,
        num_groups: int = 4,
        playoff_teams: int = 8,
        repo: Optional[Any] = None,  # <--- Add this argument
        **kwargs: Any,
    ) -> None:
        """Initializes a tournament, generating all its games based on the format."""
        self.repo = repo  # <--- Store the repo reference
        self.id_ = kwargs.get("id_", -1)
        self.teams = teams
        self.cup_type = cup_type
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

    # CRUD Methods

    def getid(self) -> int:
        """Returns the unique identifier for the cup."""
        return self.id_

    def get(self) -> str:
        """Returns a textual representation of the cup."""
        return str(self)

    def update(self, *args: Any, **kw: Any) -> None:
        """Updates cup attributes."""
        if args and isinstance(args[0], Game):
            self._handle_game_notification(args[0])
            return

        if "interval" in kw:
            self.interval = kw["interval"]

    def delete(self) -> None:
        """Deletes the cup and cleans up resources."""
        self._observers.clear()
        # Cascade deletion to the repository for managed games
        if self.repo:
            for game in list(self.games):
                try:
                    self.repo.delete(game.id())
                except (ValueError, KeyError):
                    pass
        self.games.clear()
        self.rounds.clear()
        self.groups.clear()
        self.group_games.clear()

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

        # Since Game observers are wiped on load, the Cup (which watches games in Group tournaments to trigger playoffs) needs to re-subscribe itself when the server restarts.
        
        if self.cup_type in [CupType.GROUP, CupType.GROUP2]:
            for game in self.games:
                game.watch(self)

    def __str__(self) -> str:
        """Returns a human-readable summary of the cup."""
        return f"Cup Tournament: {self.cup_type} with {len(self.teams)} teams, {len(self.games)} games"

    def _generate_games(self) -> None:
        """Delegates game generation to the appropriate method based on cup type."""
        if self.cup_type == CupType.LEAGUE:
            self._generate_league(double=False)
        elif self.cup_type == CupType.LEAGUE2:
            self._generate_league(double=True)
        elif self.cup_type == CupType.ELIMINATION:
            self._generate_elimination(double=False)
        elif self.cup_type == CupType.ELIMINATION2:
            self._generate_elimination(double=True)
        elif self.cup_type == CupType.GROUP:
            self._generate_group(double=False)
        elif self.cup_type == CupType.GROUP2:
            self._generate_group(double=True)
        else:
            raise ValueError(f"Unknown cup type: {self.cup_type}")

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
            first_leg_games = list(self.games)
            for original_game in first_leg_games:
                game2 = self._create_game_instance(
                    home=original_game.away(),
                    away=original_game.home(),
                    datetime=current_date,
                )
                self.games.append(game2)
                current_date += self.interval

    def _create_game_instance(self, home, away, datetime, group=None) -> Game:
        """Helper to create a game via Repo if available, or standalone otherwise."""
        game = None
        if self.repo:
            # SERVER MODE: Register with Repo to get a Global ID
            game_id = self.repo.create(
                type="game", home=home, away=away, datetime=datetime, group=group
            )
            # Fetch the actual game object back from the repo
            game = self.repo._objects[game_id]["instance"]
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

        # Attach existing cup observers to the new game
        # This ensures that if games are generated dynamically (e.g. Playoffs),
        # existing observers start watching them immediately.
        for entry in self._observers:
            observer = entry["observer"]
            params = entry["params"]

            # Check if game matches params
            matches = True
            if params:
                tname = params.get("tname")
                group_param = params.get("group")
                between = params.get("between")

                if tname:
                    if not (game.home().team_name.lower() == tname.lower() or
                            game.away().team_name.lower() == tname.lower()):
                        matches = False

                if group_param and matches:
                    if game.group != group_param:
                        matches = False

                if between and matches:
                    s, e = between
                    if not (s <= game.datetime <= e):
                        matches = False

            if matches:
                game.watch(observer)

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
        if self.cup_type in [CupType.LEAGUE, CupType.LEAGUE2]:
            return self._calculate_league_standings()
        elif self.cup_type in [CupType.ELIMINATION, CupType.ELIMINATION2]:
            return self._compute_bracket_standings(self.rounds)
        elif self.cup_type in [CupType.GROUP, CupType.GROUP2]:
            return self._calculate_group_standings_full()
        else:
            raise ValueError(f"Unknown cup type: {self.cup_type}")

    def _calculate_group_standings_full(self) -> Dict[str, Any]:
        """Aggregates standings for all groups and the playoff stage."""
        result: Dict[str, Any] = {"Groups": {}, "Playoffs": {}}

        for group_name in sorted(self.groups.keys()):
            standings = self._calculate_group_standings(group_name)
            result["Groups"][group_name] = standings

        if len(self.playoff_games) > 0:
            result["Playoffs"] = self._compute_bracket_standings(self.playoff_rounds)

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
                game2 = self._create_game_instance(
                    home=away_team,
                    away=home_team,
                    datetime=current_date,
                )
                round_games.append(game2)
                current_date += self.interval

        return round_games

    def gametree(self) -> Dict[str, List[Dict[str, Any]]]:
        """Generates a structured view of the tournament bracket.

        This is only applicable for formats with distinct rounds or stages,
        like ELIMINATION and GROUP tournaments.
        """
        if self.cup_type not in [
            CupType.ELIMINATION,
            CupType.ELIMINATION2,
            CupType.GROUP,
            CupType.GROUP2,
        ]:
            raise ValueError(
                f"gametree() is only available for ELIMINATION and GROUP types, not {self.cup_type}"
            )

        if self.cup_type in [CupType.ELIMINATION, CupType.ELIMINATION2]:
            return self._gametree_elimination()
        else:  # GROUP or GROUP2
            return self._gametree_group()

    def _gametree_elimination(self) -> Dict[str, List[Dict[str, Any]]]:
        """Builds the game tree specifically for an elimination bracket.

        Now resolves placeholders to actual winners when games are played.
        """
        tree: Dict[str, List[Dict[str, Any]]] = {}
        round_names = self._get_round_names(len(self.rounds))

        for round_num, round_games in enumerate(self.rounds):
            round_name = round_names[round_num]
            tree[round_name] = []

            for game in round_games:
                # Resolve placeholders to actual team names if possible
                home_name = self._resolve_placeholder(game.home())
                away_name = self._resolve_placeholder(game.away())

                game_info = {
                    "game_id": game.id(),
                    "home": home_name,
                    "away": away_name,
                    "datetime": game.datetime.strftime("%Y-%m-%d %H:%M"),
                    "state": game.state.name,
                    "score": {"home": game.home_score, "away": game.away_score}
                    if game.state == GameState.ENDED
                    else None,
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

    def _compute_bracket_standings(
        self, rounds: List[List[Game]]
    ) -> Dict[str, Dict[str, Any]]:
        """Summarizes team progress through a bracket (Elimination or Playoffs)."""
        standings: Dict[str, Dict[str, Any]] = {}

        # Check each round and update standings
        for round_num, round_games in enumerate(rounds, 1):
            for game in round_games:
                # Resolve placeholders to actual names if possible
                home_name = self._resolve_placeholder(game.home())
                away_name = self._resolve_placeholder(game.away())

                # Determine if teams are known (not "Winner of...")
                is_h_known = not home_name.startswith("Winner of")
                is_a_known = not away_name.startswith("Winner of")

                if is_h_known:
                    if home_name not in standings:
                        standings[home_name] = {"Round": 0, "Won": [], "Lost": None}
                    standings[home_name]["Round"] = round_num

                if is_a_known:
                    if away_name not in standings:
                        standings[away_name] = {"Round": 0, "Won": [], "Lost": None}
                    standings[away_name]["Round"] = round_num

                if game.state == GameState.ENDED and is_h_known and is_a_known:
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

        After group stage, generates COMPLETE playoff bracket (all rounds).
        """
        shuffled_teams = self.teams.copy()
        random.shuffle(shuffled_teams)

        group_names = list(string.ascii_uppercase[: self.num_groups])  # A, B, C, ...
        self.groups = {name: [] for name in group_names}

        # Distribute teams round-robin to handle non-divisible counts (e.g. 11 teams)
        for i, team in enumerate(shuffled_teams):
            self.groups[group_names[i % self.num_groups]].append(team)

        for group_name in group_names:
            group_games = self._create_group_league(self.groups[group_name], group_name, double)
            self.group_games[group_name] = group_games
            self.games.extend(group_games)

        # The cup watches its own games to trigger playoffs automatically
        for game in self.games:
            game.watch(self)

        # Playoff info (bracket will be generated after group stage)
        print(f"\n   Playoff: {self.playoff_teams} teams will advance.")
        print(
            "   Playoff matches will be determined after the group stage is completed."
        )
        # Initialize empty playoff structure
        self.playoff_games = []
        self.playoff_rounds: List[List[Game]] = []  # Add this attribute!

    def _create_group_league(
        self, group_teams: List[Team], group_name: str, double: bool
    ) -> List[Game]:
        """Helper to create round-robin matches for a single group.

        Uses proper round-robin algorithm to ensure balanced scheduling.
        """
        import copy

        teams = copy.copy(group_teams)
        n = len(teams)

        # If odd number, add bye
        if n % 2 == 1:
            teams.append(None)
            n += 1

        group_games: List[Game] = []
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

                game = self._create_game_instance(
                    home=home_team,
                    away=away_team,
                    datetime=current_date,
                    group=group_name,
                )
                group_games.append(game)
                current_date += self.interval

            # Rotate teams (keep first fixed, rotate others)
            teams = [teams[0]] + [teams[-1]] + teams[1:-1]

        # If double, create reverse fixtures
        if double:
            first_round_count = len(group_games)
            for i in range(first_round_count):
                original_game = group_games[i]
                game2 = self._create_game_instance(
                    home=original_game.away(),
                    away=original_game.home(),
                    datetime=current_date,
                    group=group_name,
                )
                group_games.append(game2)
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
        """Generates the COMPLETE playoff bracket after group stage.

        Creates all playoff rounds (QF → SF → F) similar to ELIMINATION.
        """
        if self.cup_type not in [CupType.GROUP, CupType.GROUP2]:
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

        double = self.cup_type == CupType.GROUP2

        # Add a break before the playoffs start.
        self._current_date += self.interval * 3

        random.shuffle(playoff_teams)

        # Generate COMPLETE playoff bracket (all rounds)

        self._generate_playoff_bracket(playoff_teams, double)

    def _generate_playoff_bracket(self, teams: List[Team], double: bool) -> None:
        """Generate complete playoff bracket (QF → SF → F).

        Similar to _generate_elimination() but for playoff teams only.

        Args:
            teams: Qualified teams from group stage
            double: Whether to play home/away (GROUP2)
        """
        import copy

        current_teams = copy.copy(teams)

        # Handle odd number (bye)
        bye_team: Optional[Team] = None
        if len(current_teams) % 2 == 1:
            bye_team = current_teams.pop()
            print(f"   {bye_team.team_name} has a bye (advances to next round).")

        # Generate first round
        first_round = self._create_elimination_round(
            current_teams, double, is_first_round=True
        )
        self.playoff_rounds.append(first_round)
        self.playoff_games.extend(first_round)
        self.games.extend(first_round)

        print(f"\n   Playoff Round 1: {len(first_round)} games created.")

        # Prepare next round teams (placeholders)
        next_round_teams: List[Team] = []

        if bye_team is not None:
            next_round_teams.append(bye_team)

        for i in range(0, len(first_round), 2 if double else 1):
            if double:
                game1_id = first_round[i].id()
                game2_id = first_round[i + 1].id()
                placeholder = PlaceholderTeam(
                    f"Winner of Games {game1_id} & {game2_id}", [game1_id, game2_id]
                )
            else:
                game_id = first_round[i].id()
                placeholder = PlaceholderTeam(f"Winner of Game {game_id}", [game_id])
            next_round_teams.append(placeholder)

        # Generate subsequent rounds until we have a champion
        while len(next_round_teams) > 1:
            round_bye: Optional[Team] = None
            if len(next_round_teams) % 2 == 1:
                round_bye = next_round_teams.pop()
                print(f"   {round_bye.team_name} has a bye in this round.")

            next_round = self._create_elimination_round(
                next_round_teams, double, is_first_round=False
            )
            self.playoff_rounds.append(next_round)
            self.playoff_games.extend(next_round)
            self.games.extend(next_round)

            round_num = len(self.playoff_rounds)
            print(f"\n   Playoff Round {round_num}: {len(next_round)} games created.")

            # Prepare next round
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

        print(f"\n   ✅ Complete playoff bracket generated!")
        print(f"   Total playoff rounds: {len(self.playoff_rounds)}")
        print(f"   Total playoff games: {len(self.playoff_games)}")

    def _gametree_group(self) -> Dict[str, Any]:
        """Builds the game tree for a group-based tournament.

        Now includes ALL playoff rounds (not just first round).
        """
        tree: Dict[str, Any] = {"Groups": {}, "Playoffs": {}}

        # Groups (unchanged)
        for group_name in sorted(self.groups.keys()):
            tree["Groups"][group_name] = []
            group_games = self.group_games[group_name]

            for game in group_games:
                game_info = {
                    "game_id": game.id(),
                    "home": self._resolve_placeholder(game.home()),
                    "away": self._resolve_placeholder(game.away()),
                    "datetime": game.datetime.strftime("%Y-%m-%d %H:%M"),
                    "state": game.state.name,
                    "score": {"home": game.home_score, "away": game.away_score}
                    if game.state == GameState.ENDED
                    else None,
                }
                tree["Groups"][group_name].append(game_info)

        # Playoffs (Show ALL rounds)
        if len(self.playoff_games) > 0:
            # Calculate number of playoff rounds
            num_playoff_teams = (
                len(self.playoff_rounds[0]) * 2 if self.playoff_rounds else 0
            )
            num_playoff_rounds = len(self.playoff_rounds)

            round_names = self._get_round_names(num_playoff_rounds)

            # Add each playoff round to tree
            for round_num, round_games in enumerate(self.playoff_rounds):
                round_name = round_names[round_num]
                tree["Playoffs"][round_name] = []

                for game in round_games:
                    game_info = {
                        "game_id": game.id(),
                        "home": self._resolve_placeholder(game.home()),
                        "away": self._resolve_placeholder(game.away()),
                        "datetime": game.datetime.strftime("%Y-%m-%d %H:%M"),
                        "state": game.state.name,
                        "score": {"home": game.home_score, "away": game.away_score}
                        if game.state == GameState.ENDED
                        else None,
                    }
                    tree["Playoffs"][round_name].append(game_info)

        return tree

    def _resolve_placeholder(self, team: Team) -> str:
        """Resolves a placeholder team to actual winner if game is played.

        Recursively resolves nested placeholders (e.g., Winner of Winner of Game X).

        Args:
            team: Team object (could be PlaceholderTeam or real Team)

        Returns:
            Team name (either real team name or placeholder description)
        """
        # If real team, return its name
        if not isinstance(team, PlaceholderTeam):
            return team.team_name

        # If placeholder, check its source games
        placeholder: PlaceholderTeam = team
        source_games = placeholder.source_games

        # If single game source
        if len(source_games) == 1:
            game_id = source_games[0]
            source_game = self._find_game_by_id(game_id)

            if source_game and source_game.state == GameState.ENDED:
                winner = self._get_game_winner(source_game)
                if winner:
                    return self._resolve_placeholder(winner)

            return f"Winner of Game {game_id}"

        else:
            game_ids_str = ", ".join(str(g) for g in source_games)

            # Check if all games ended and retrieve them
            games = []
            for game_id in source_games:
                game = self._find_game_by_id(game_id)
                if not game or game.state != GameState.ENDED:
                    return f"Winner of Games [{game_ids_str}]"
                games.append(game)

            if len(games) == 2:
                g1 = games[0]
                g2 = games[1]

                # Robust aggregate score calculation
                team_a = g1.home()
                team_b = g1.away()

                score_a = g1.home_score
                score_b = g1.away_score

                # Add scores from g2 based on team identity
                if g2.home() == team_a:
                    score_a += g2.home_score
                elif g2.away() == team_a:
                    score_a += g2.away_score

                if g2.home() == team_b:
                    score_b += g2.home_score
                elif g2.away() == team_b:
                    score_b += g2.away_score

                if score_a > score_b:
                    return self._resolve_placeholder(team_a)
                elif score_b > score_a:
                    return self._resolve_placeholder(team_b)

            return f"Winner of Games [{game_ids_str}]"

    def _handle_game_notification(self, game: Game) -> None:
        """Internal observer handler to trigger playoffs when group stage ends."""
        if game.state == GameState.ENDED:
            if self.cup_type in [CupType.GROUP, CupType.GROUP2] and not self.playoff_games:
                # Check if all group games are finished
                if all(g.state == GameState.ENDED for g in self.games if g.group):
                    self.generate_playoffs()

    def _find_game_by_id(self, game_id: int) -> Optional[Game]:
        """Finds a game by its ID in the cup's games list."""
        for game in self.games:
            if game.id() == game_id:
                return game
        return None

    def _get_game_winner(self, game: Game) -> Optional[Team]:
        """Returns the winner of a completed game.

        Returns None if game is draw or not ended.
        """
        if game.state != GameState.ENDED:
            return None

        if game.home_score > game.away_score:
            return game.home()
        elif game.away_score > game.home_score:
            return game.away()
        else:
            return None
