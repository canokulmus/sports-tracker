# cup.py
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
from itertools import combinations
from constants import GameState
from game import Game
from team import Team, PlaceholderTeam
import random
import string


class CupType:
    """Cup type constants."""
    LEAGUE = "LEAGUE"
    LEAGUE2 = "LEAGUE2"
    ELIMINATION = "ELIMINATION"
    ELIMINATION2 = "ELIMINATION2"
    GROUP = "GROUP"
    GROUP2 = "GROUP2"

class Cup:
    """A container for a collection of games (e.g., a tournament)."""

    def __init__(
        self, 
        teams: List[Team], 
        type: str, 
        interval: timedelta,
        num_groups: int = 4,      # ← YENİ: Kaç grup olacak
        playoff_teams: int = 8    # ← YENİ: Playoff'a kaç takım gidecek
    ) -> None:
        """
        Creates a cup/tournament with given teams.
        
        Args:
            teams: List of Team objects
            type: Cup type (LEAGUE, ELIMINATION, GROUP, etc.)
            interval: Time interval between games
            num_groups: Number of groups (for GROUP type only)
            playoff_teams: Number of teams in playoffs (for GROUP type only)
        """
        self.teams = teams
        self.type = type
        self.interval = interval
        self.games: List[Game] = []
        self._observers: List[Any] = []
        self._game_id_counter = 1
        self._current_date = datetime.now()
        
        # Elimination için round tracking
        self.rounds: List[List[Game]] = []
        
        # GROUP için ekstra parametreler
        self.num_groups = num_groups            # ← YENİ
        self.playoff_teams = playoff_teams      # ← YENİ
        self.groups: Dict[str, List[Team]] = {} # ← YENİ: {'A': [team1, team2, ...]}
        self.group_games: Dict[str, List[Game]] = {}  # ← YENİ: Her grubun maçları
        self.playoff_games: List[Game] = []     # ← YENİ: Playoff maçları
        
        # Turnuva tipine göre maçları oluştur
        self._generate_games()
    
    def __getitem__(self, gameid: int) -> Game:
        """
        Returns the game with the given ID.
        
        Args:
            gameid: Game ID to search for
            
        Returns:
            Game object with matching ID
            
        Raises:
            KeyError: If game with given ID is not found
        """
        for game in self.games:
            if game.id() == gameid:
                return game
        
        raise KeyError(f"Game with ID {gameid} not found in this cup")

    def __str__(self) -> str:
        """Returns the string representation of the Cup."""
        return f"Cup Tournament: {self.type} with {len(self.teams)} teams, {len(self.games)} games"

    def _generate_games(self) -> None:
        """Generate games based on cup type."""
        if self.type == CupType.LEAGUE:
            self._generate_league(double=False)
        elif self.type == CupType.LEAGUE2:
            self._generate_league(double=True)
        elif self.type == CupType.ELIMINATION:
            self._generate_elimination(double=False)
        elif self.type == CupType.ELIMINATION2:
            self._generate_elimination(double=True)
        elif self.type == CupType.GROUP:
            self._generate_group(double=False)  # ← YENİ
        elif self.type == CupType.GROUP2:
            self._generate_group(double=True)   # ← YENİ
        else:
            raise ValueError(f"Unknown cup type: {self.type}")

    def _generate_league(self, double: bool = False) -> None:
        """
        Generate league matches where every team plays against every other team.
        
        Args:
            double: If True, each pair plays twice (home/away swap)
        """
        # Tüm takım çiftlerini oluştur
        # combinations([A, B, C, D], 2) → (A,B), (A,C), (A,D), (B,C), (B,D), (C,D)
        pairs = list(combinations(self.teams, 2))
        
        current_date = self._current_date
        
        for home_team, away_team in pairs:
            # İlk maç: home vs away
            game = Game(
                home=home_team,
                away=away_team,
                id_=self._game_id_counter,
                datetime=current_date
            )
            self.games.append(game)
            self._game_id_counter += 1
            current_date += self.interval  # Bir sonraki maç tarihi
            
            # Eğer double ise, rövanş maçı da ekle
            if double:
                game2 = Game(
                    home=away_team,  # ← ev sahibi/deplasman yer değiştirdi
                    away=home_team,
                    id_=self._game_id_counter,
                    datetime=current_date
                )
                self.games.append(game2)
                self._game_id_counter += 1
                current_date += self.interval
    def search(
        self, 
        tname: Optional[str] = None, 
        group: Optional[str] = None, 
        between: Optional[Tuple[datetime, datetime]] = None
    ) -> List[Game]:
        """
        Search for games with the given criteria. All parameters are optional.
        
        Args:
            tname: Team name to search for
            group: Group name (for GROUP type tournaments)
            between: Tuple of (start_date, end_date) for date range filtering
            
        Returns:
            List of games matching the criteria
        """
        results: List[Game] = []
        
        for game in self.games:
            # Varsayılan: tüm maçlar geçer
            matches = True
            
            # Takım ismi filtresi
            if tname is not None:
                # Ev sahibi veya deplasman takımı eşleşmeli
                home_match = game.home().team_name.lower() == tname.lower()
                away_match = game.away().team_name.lower() == tname.lower()
                if not (home_match or away_match):
                    matches = False
            
            # Tarih aralığı filtresi
            if between is not None and matches:
                start_date, end_date = between
                if not (start_date <= game.datetime <= end_date):
                    matches = False
            
            # Grup filtresi (şimdilik GROUP tipi desteklenmediği için pass)
            if group is not None and matches:
                # TODO: GROUP tipi implement edilince eklenecek
                pass
            
            # Tüm filtreleri geçtiyse ekle
            if matches:
                results.append(game)
        
        return results

    def standings(self) -> Dict[str, Any] | List[Tuple[str, int, int, int, int, int, int]]:
        """
        Return tournament standings based on cup type.
        
        LEAGUE: List of (team, won, draw, lost, scorefor, scoreagainst, points)
        ELIMINATION: Dict with team rounds
        GROUP: Dict with Groups and Playoffs
        
        Returns:
            Standings in format appropriate for cup type
        """
        if self.type in [CupType.LEAGUE, CupType.LEAGUE2]:
            return self._calculate_league_standings()
        elif self.type in [CupType.ELIMINATION, CupType.ELIMINATION2]:
            return self._calculate_elimination_standings()
        elif self.type in [CupType.GROUP, CupType.GROUP2]:
            return self._calculate_group_standings_full()  # ← YENİ
        else:
            raise ValueError(f"Unknown cup type: {self.type}")

    def _calculate_group_standings_full(self) -> Dict[str, Any]:
        """
        Calculate full GROUP tournament standings.
        
        Returns:
            Dict with 'Groups' and 'Playoffs' keys
        """
        result: Dict[str, Any] = {
            "Groups": {},
            "Playoffs": {}
        }
        
        # Her grup için standings
        for group_name in sorted(self.groups.keys()):
            standings = self._calculate_group_standings(group_name)
            result["Groups"][group_name] = standings
        
        # Playoff standings (ELIMINATION formatında)
        if len(self.playoff_games) > 0:
            # Playoff'a katılan takımları bul ve elimination standings hesapla
            # Basitleştirilmiş: Şimdilik boş
            result["Playoffs"] = "Not yet implemented"
        
        return result

    def _calculate_league_standings(self) -> List[Tuple[str, int, int, int, int, int, int]]:
        """
        Calculate league standings.
        
        Returns:
            List of (team_name, won, draw, lost, goals_for, goals_against, points)
            Sorted by points (descending), then goal difference (descending)
        """
        # Her takım için istatistik tut
        stats: Dict[str, Dict[str, int]] = {}
        
        # Tüm takımları başlat
        for team in self.teams:
            stats[team.team_name] = {
                "won": 0,
                "draw": 0,
                "lost": 0,
                "goals_for": 0,
                "goals_against": 0,
                "points": 0
            }
        
        # Sadece bitmiş maçları say
        
        for game in self.games:
            # Maç bitmemişse atla
            if game.state != GameState.ENDED:
                continue
            
            home_team = game.home().team_name
            away_team = game.away().team_name
            home_score = game.home_score
            away_score = game.away_score
            
            # Gol istatistikleri
            stats[home_team]["goals_for"] += home_score
            stats[home_team]["goals_against"] += away_score
            stats[away_team]["goals_for"] += away_score
            stats[away_team]["goals_against"] += home_score
            
            # Kazanan/berabere/kaybeden hesapla
            if home_score > away_score:
                # Ev sahibi kazandı
                stats[home_team]["won"] += 1
                stats[home_team]["points"] += 2  # Galibiyet = 2 puan
                stats[away_team]["lost"] += 1
            elif home_score < away_score:
                # Deplasman kazandı
                stats[away_team]["won"] += 1
                stats[away_team]["points"] += 2
                stats[home_team]["lost"] += 1
            else:
                # Berabere
                stats[home_team]["draw"] += 1
                stats[home_team]["points"] += 1  # Beraberlik = 1 puan
                stats[away_team]["draw"] += 1
                stats[away_team]["points"] += 1
        
        # Tuple listesine çevir
        standings_list: List[Tuple[str, int, int, int, int, int, int]] = []
        for team_name, team_stats in stats.items():
            standings_list.append((
                team_name,
                team_stats["won"],
                team_stats["draw"],
                team_stats["lost"],
                team_stats["goals_for"],
                team_stats["goals_against"],
                team_stats["points"]
            ))
        
        # Sırala: önce puana göre, sonra gol averajına göre
        standings_list.sort(
            key=lambda x: (x[6], x[4] - x[5]),  # (points, goal_difference)
            reverse=True  # Büyükten küçüğe
        )
        
        return standings_list

    def watch(self, obj: Any, **searchparams: Any) -> None:
        """
        Adds obj as an observer of the tournament.
        When a game matching search parameters starts or ends, obj.update(game) is called.
        
        Args:
            obj: Observer object (must have update(game) method)
            **searchparams: Search parameters (tname, group, between)
        """
        # Observer'ı kaydet (searchparams ile birlikte)
        observer_entry = {
            "observer": obj,
            "params": searchparams
        }
        
        if observer_entry not in self._observers:
            self._observers.append(observer_entry)
        
        # Tüm maçlara observer'ı ekle (searchparams'a uygun olanlar için)
        matching_games = self.search(**searchparams)
        for game in matching_games:
            game.watch(obj)

    def unwatch(self, obj: Any) -> None:
        """
        Remove the obj from list of observers.
        
        Args:
            obj: Observer object to remove
        """
        # Cup'ın observer listesinden çıkar
        self._observers = [
            entry for entry in self._observers 
            if entry["observer"] != obj
        ]
        
        # Tüm maçlardan observer'ı çıkar
        for game in self.games:
            game.unwatch(obj)
            
    def _generate_elimination(self, double: bool = False) -> None:
        """
        Generate elimination tournament matches with multiple rounds.
        
        Args:
            double: If True, each matchup has 2 games (home/away)
        """

        # Takımları rastgele karıştır
        shuffled_teams: List[Team] = self.teams.copy()
        random.shuffle(shuffled_teams)
        
        # Tek sayıda takım varsa bye
        bye_team: Team | None = None
        if len(shuffled_teams) % 2 == 1:
            bye_team = shuffled_teams.pop()
            print(f"   🎫 {bye_team.team_name} has a bye (advances without playing)")
        
        # İlk round'u oluştur
        current_round = self._create_elimination_round(
            shuffled_teams, double, is_first_round=True
        )
        self.rounds.append(current_round)
        self.games.extend(current_round)
        
        # Sonraki round'ları oluştur
        next_round_teams: List[Team] = []
        
        # Bye takımı varsa sonraki tura ekle
        if bye_team is not None:
            next_round_teams.append(bye_team)
        
        # Her maç çiftinin kazananı
        for i in range(0, len(current_round), 2 if double else 1):
            if double:
                # İki maçın kazananı (toplam skor)
                game1_id = current_round[i].id()
                game2_id = current_round[i + 1].id()
                placeholder = PlaceholderTeam(
                    f"Winner of Games {game1_id} & {game2_id}",
                    [game1_id, game2_id]
                )
            else:
                # Tek maçın kazananı
                game_id = current_round[i].id()
                placeholder = PlaceholderTeam(
                    f"Winner of Game {game_id}",
                    [game_id]
                )
            next_round_teams.append(placeholder)
        
        # Sonraki round'ları oluştur
        while len(next_round_teams) > 1:
            # Tek sayıda takım varsa, birini bye yap
            round_bye: Team | None = None
            if len(next_round_teams) % 2 == 1:
                round_bye = next_round_teams.pop()
                print(f"   🎫 {round_bye.team_name} has a bye in this round")
            
            next_round = self._create_elimination_round(
                next_round_teams, double, is_first_round=False
            )
            self.rounds.append(next_round)
            self.games.extend(next_round)
            
            # Bir sonraki round için placeholder'lar
            next_round_teams = []
            
            # Bye takımı varsa sonraki round'a ekle
            if round_bye is not None:
                next_round_teams.append(round_bye)
            
            for i in range(0, len(next_round), 2 if double else 1):
                if double:
                    game1_id = next_round[i].id()
                    game2_id = next_round[i + 1].id()
                    placeholder = PlaceholderTeam(
                        f"Winner of Games {game1_id} & {game2_id}",
                        [game1_id, game2_id]
                    )
                else:
                    game_id = next_round[i].id()
                    placeholder = PlaceholderTeam(
                        f"Winner of Game {game_id}",
                        [game_id]
                    )
                next_round_teams.append(placeholder)
                
    def _create_elimination_round(
        self, 
        teams: List[Team], 
        double: bool,
        is_first_round: bool
    ) -> List[Game]:
        """
        Create a single elimination round.
        
        Args:
            teams: Teams for this round (must be even number)
            double: Whether to create double matches
            is_first_round: If True, use current date, else add extra interval
            
        Returns:
            List of games in this round
        """
        round_games: List[Game] = []
        
        # Round arası bekleme süresi
        if not is_first_round:
            self._current_date += self.interval * 2  # Round arası 2x interval
        
        current_date = self._current_date
        
        # Takımları ikişerli eşleştir
        for i in range(0, len(teams), 2):
            home_team = teams[i]
            away_team = teams[i + 1]
            
            # İlk maç
            game = Game(
                home=home_team,
                away=away_team,
                id_=self._game_id_counter,
                datetime=current_date
            )
            round_games.append(game)
            self._game_id_counter += 1
            current_date += self.interval
            
            # Double ise rövanş
            if double:
                game2 = Game(
                    home=away_team,
                    away=home_team,
                    id_=self._game_id_counter,
                    datetime=current_date
                )
                round_games.append(game2)
                self._game_id_counter += 1
                current_date += self.interval
        
        return round_games
    
    def gametree(self) -> Dict[str, List[Dict[str, Any]]]:
        """
        Return a tree of games for ELIMINATION and GROUP type tournaments.
        Shows which games are in which round and how winners advance.
        
        Returns:
            Dictionary with round names as keys and game info as values
        """
        if self.type not in [CupType.ELIMINATION, CupType.ELIMINATION2, CupType.GROUP, CupType.GROUP2]:
            raise ValueError(f"gametree() is only available for ELIMINATION and GROUP types, not {self.type}")
        
        if self.type in [CupType.ELIMINATION, CupType.ELIMINATION2]:
            return self._gametree_elimination()
        else:  # GROUP or GROUP2
            return self._gametree_group()

    def _gametree_elimination(self) -> Dict[str, List[Dict[str, Any]]]:
        """
        Generate game tree for elimination tournaments.
        
        Returns:
            Dict with round names and game information
        """
        tree: Dict[str, List[Dict[str, Any]]] = {}
        
        # Round isimleri
        round_names = self._get_round_names(len(self.rounds))
        
        for round_num, round_games in enumerate(self.rounds):
            round_name = round_names[round_num]
            tree[round_name] = []
            
            for game in round_games:
                game_info = {
                    "game_id": game.id(),
                    "home": game.home().team_name,
                    "away": game.away().team_name,
                    "datetime": game.datetime.strftime("%Y-%m-%d %H:%M")
                }
                tree[round_name].append(game_info)
        
        return tree

    def _get_round_names(self, total_rounds: int) -> List[str]:
        """
        Get appropriate round names based on total number of rounds.
        
        Args:
            total_rounds: Total number of rounds in tournament
            
        Returns:
            List of round names
        """
        if total_rounds == 1:
            return ["Final"]
        elif total_rounds == 2:
            return ["Semi-Final", "Final"]
        elif total_rounds == 3:
            return ["Quarter-Final", "Semi-Final", "Final"]
        elif total_rounds == 4:
            return ["Round of 16", "Quarter-Final", "Semi-Final", "Final"]
        elif total_rounds == 5:
            return ["Round of 32", "Round of 16", "Quarter-Final", "Semi-Final", "Final"]
        else:
            # General naming for larger tournaments
            names: List[str] = []
            for i in range(total_rounds - 3):
                names.append(f"Round {i + 1}")
            names.extend(["Quarter-Final", "Semi-Final", "Final"])
            return names
        
    def _calculate_elimination_standings(self) -> Dict[str, Dict[str, Any]]:
        """
        Calculate elimination tournament standings.
        
        Returns:
            Dict with team names as keys and their tournament info as values
            Format: {
                'TeamName': {
                    'Round': int,  # Last round played or currently playing
                    'Won': [(opponent, own_score, opp_score), ...],
                    'Lost': (opponent, own_score, opp_score) or None
                }
            }
        """

        standings: Dict[str, Dict[str, Any]] = {}
        
        # Tüm gerçek takımları başlat (placeholder'lar hariç)
        for team in self.teams:
            standings[team.team_name] = {
                'Round': 0,
                'Won': [],
                'Lost': None
            }
        
        # Her round'u kontrol et
        for round_num, round_games in enumerate(self.rounds, 1):
            for game in round_games:
                # Placeholder takımları atla
                if isinstance(game.home_, PlaceholderTeam) or isinstance(game.away_, PlaceholderTeam):
                    continue
                
                home_name = game.home().team_name
                away_name = game.away().team_name
                
                # Her iki takımı da bu round'da işaretle
                if home_name in standings:
                    standings[home_name]['Round'] = round_num
                if away_name in standings:
                    standings[away_name]['Round'] = round_num
                
                # Maç bittiyse kazanan/kaybeden belirle
                if game.state == GameState.ENDED:
                    home_score = game.home_score
                    away_score = game.away_score
                    
                    if home_score > away_score:
                        # Ev sahibi kazandı
                        if home_name in standings:
                            standings[home_name]['Won'].append((away_name, home_score, away_score))
                        if away_name in standings:
                            standings[away_name]['Lost'] = (home_name, away_score, home_score)
                    elif away_score > home_score:
                        # Deplasman kazandı
                        if away_name in standings:
                            standings[away_name]['Won'].append((home_name, away_score, home_score))
                        if home_name in standings:
                            standings[home_name]['Lost'] = (away_name, home_score, away_score)
                    # Beraberlik durumu ELIMINATION'da genelde olmaz
        
        return standings
    
    def _generate_group(self, double: bool = False) -> None:
        """
        Generate GROUP tournament matches.
        
        Args:
            double: If True, each matchup has 2 games (home/away)
        """
        
        # Takımları karıştır
        shuffled_teams = self.teams.copy()
        random.shuffle(shuffled_teams)
        
        # Gruplara böl
        teams_per_group = len(shuffled_teams) // self.num_groups
        
        group_names = list(string.ascii_uppercase[:self.num_groups])  # A, B, C, ...
        
        print(f"\n🏆 GROUP TOURNAMENT: {self.num_groups} groups, {teams_per_group} teams per group")
        
        # Her grubu oluştur
        for i, group_name in enumerate(group_names):
            start_idx = i * teams_per_group
            end_idx = start_idx + teams_per_group
            group_teams = shuffled_teams[start_idx:end_idx]
            
            self.groups[group_name] = group_teams
            
            print(f"\n   Group {group_name}: {', '.join([t.team_name for t in group_teams])}")
            
            # Bu grup için LEAGUE maçları oluştur
            group_games = self._create_group_league(group_teams, group_name, double)
            self.group_games[group_name] = group_games
            self.games.extend(group_games)
        
        # Playoff'a gidecek takımları belirle (şimdilik placeholder)
        # Gerçek uygulamada grup maçları bittikten sonra belirlenecek
        print(f"\n   📌 Playoff: {self.playoff_teams} teams will advance")
        print(f"   📌 Playoff maçları grup aşaması bittikten sonra belirlenecek")

    def _create_group_league(
        self, 
        group_teams: List[Team], 
        group_name: str,
        double: bool
    ) -> List[Game]:
        """
        Create league matches for a single group.
        
        Args:
            group_teams: Teams in this group
            group_name: Group name (A, B, C, ...)
            double: Whether to create double matches
            
        Returns:
            List of games in this group
        """


        group_games: List[Game] = []
        current_date = self._current_date
        
        # Tüm takım çiftlerini oluştur
        pairs = list(combinations(group_teams, 2))
        
        for home_team, away_team in pairs:
            # İlk maç
            game = Game(
                home=home_team,
                away=away_team,
                id_=self._game_id_counter,
                datetime=current_date,
                group=group_name  # ← BURADA PARAMETRE OLARAK VERİYORUZ
            )
            group_games.append(game)
            self._game_id_counter += 1
            current_date += self.interval
            
            # Double ise rövanş
            if double:
                game2 = Game(
                    home=away_team,
                    away=home_team,
                    id_=self._game_id_counter,
                    datetime=current_date,
                    group=group_name  # ← BURADA DA
                )
                group_games.append(game2)
                self._game_id_counter += 1
                current_date += self.interval
        
        return group_games

    def _calculate_group_standings(self, group_name: str) -> List[Tuple[str, int, int, int, int, int, int]]:
        """
        Calculate standings for a single group.
        
        Args:
            group_name: Group name (A, B, C, ...)
            
        Returns:
            List of (team_name, won, draw, lost, goals_for, goals_against, points)
            Sorted by points (descending), then goal difference (descending)
        """
        
        # Bu gruptaki takımlar
        group_teams = self.groups[group_name]
        
        # İstatistikleri başlat
        stats: Dict[str, Dict[str, int]] = {}
        for team in group_teams:
            stats[team.team_name] = {
                "won": 0,
                "draw": 0,
                "lost": 0,
                "goals_for": 0,
                "goals_against": 0,
                "points": 0
            }
        
        # Bu gruptaki maçları kontrol et
        group_games = self.group_games[group_name]
        
        for game in group_games:
            # Maç bitmemişse atla
            if game.state != GameState.ENDED:
                continue
            
            home_team = game.home().team_name
            away_team = game.away().team_name
            home_score = game.home_score
            away_score = game.away_score
            
            # Gol istatistikleri
            stats[home_team]["goals_for"] += home_score
            stats[home_team]["goals_against"] += away_score
            stats[away_team]["goals_for"] += away_score
            stats[away_team]["goals_against"] += home_score
            
            # Kazanan/berabere/kaybeden
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
        
        # Tuple listesine çevir
        standings_list: List[Tuple[str, int, int, int, int, int, int]] = []
        for team_name, team_stats in stats.items():
            standings_list.append((
                team_name,
                team_stats["won"],
                team_stats["draw"],
                team_stats["lost"],
                team_stats["goals_for"],
                team_stats["goals_against"],
                team_stats["points"]
            ))
        
        # Sırala: puan, sonra gol averajı
        standings_list.sort(
            key=lambda x: (x[6], x[4] - x[5]),
            reverse=True
        )
        
        return standings_list
    
    def generate_playoffs(self) -> None:
        """
        Generate playoff matches after group stage is complete.
        Should be called after all group games are finished.
        
        Only works for GROUP type tournaments.
        """
        if self.type not in [CupType.GROUP, CupType.GROUP2]:
            raise ValueError("generate_playoffs() only works for GROUP tournaments")
        
        # Her gruptan kaç takım playoff'a gidecek
        k = self.playoff_teams // self.num_groups
        wild_card_count = self.playoff_teams - (k * self.num_groups)
        
        print(f"\n🏆 PLAYOFF GENERATION")
        print(f"   Each group sends top {k} teams")
        print(f"   Plus {wild_card_count} wild card teams")
        
        playoff_teams: List[Team] = []
        all_qualified: List[Tuple[Team, int, str]] = []  # (team, points, group)
        
        # Her gruptan ilk k takımı al
        for group_name in sorted(self.groups.keys()):
            standings = self._calculate_group_standings(group_name)
            
            print(f"\n   Group {group_name} standings:")
            for i, (team_name, _, _, _, _, _, pts) in enumerate(standings, 1):
                # ↑ DEĞİŞTİ: gf, ga yerine goals_for, goals_against
                print(f"      {i}. {team_name}: {pts} pts")
                
                # İlk k takım direkt playoff'a
                if i <= k:
                    # Takım nesnesini bul
                    team_obj = next(t for t in self.groups[group_name] if t.team_name == team_name)
                    playoff_teams.append(team_obj)
                    print(f"         ✅ Qualified (Group winner)")
                else:
                    # Wild card adayı
                    team_obj = next(t for t in self.groups[group_name] if t.team_name == team_name)
                    all_qualified.append((team_obj, pts, group_name))
        
        # Wild card takımları ekle (puana göre en iyiler)
        if wild_card_count > 0:
            # Henüz playoff'a gitmeyenleri puana göre sırala
            all_qualified.sort(key=lambda x: x[1], reverse=True)
            
            print(f"\n   Wild card candidates:")
            for team, pts, grp in all_qualified[:wild_card_count]:
                print(f"      {team.team_name} (Group {grp}): {pts} pts ✅")
                playoff_teams.append(team)

        print(f"\n   📌 Total playoff teams: {len(playoff_teams)}")
        
        # Playoff maçlarını ELIMINATION formatında oluştur
        double = (self.type == CupType.GROUP2)
        
        # Playoff başlangıç tarihini ayarla (grup maçlarından sonra)
        self._current_date += self.interval * 3  # 3 gün ara
        
        # Playoff'u oluştur (ELIMINATION mantığıyla)
        random.shuffle(playoff_teams)
        
        # Playoff rounds
        playoff_round = self._create_elimination_round(
            playoff_teams, double, is_first_round=True
        )
        self.playoff_games = playoff_round
        self.games.extend(playoff_round)
        
        print(f"\n   🎮 Playoff Round 1: {len(playoff_round)} games created")

    def _gametree_group(self) -> Dict[str, Any]:
        """
        Generate game tree for GROUP tournaments.
        
        Returns:
            Dict with 'Groups' and 'Playoffs' sections
        """
        tree: Dict[str, Any] = {
            "Groups": {},
            "Playoffs": {}
        }
        
        # Grup maçları
        for group_name in sorted(self.groups.keys()):
            tree["Groups"][group_name] = []
            
            group_games = self.group_games[group_name]
            for game in group_games:
                game_info = {
                    "game_id": game.id(),
                    "home": game.home().team_name,
                    "away": game.away().team_name,
                    "datetime": game.datetime.strftime("%Y-%m-%d %H:%M")
                }
                tree["Groups"][group_name].append(game_info)
        
        # Playoff maçları
        if len(self.playoff_games) > 0:
            # Playoff'u rounds'a ayır
            # Şu an sadece ilk round var, ama gelecekte birden fazla olabilir
            
            # Kaç round olmalı?
            num_playoff_teams = len(self.playoff_games) * 2  # Her maç 2 takım
            num_playoff_rounds = 0
            temp = num_playoff_teams
            while temp > 1:
                temp //= 2
                num_playoff_rounds += 1
            
            # Round isimleri
            round_names = self._get_round_names(num_playoff_rounds)
            
            # Şimdilik sadece ilk round'u ekle
            tree["Playoffs"][round_names[0]] = []
            
            for game in self.playoff_games:
                game_info = {
                    "game_id": game.id(),
                    "home": game.home().team_name,
                    "away": game.away().team_name,
                    "datetime": game.datetime.strftime("%Y-%m-%d %H:%M")
                }
                tree["Playoffs"][round_names[0]].append(game_info)
        
        return tree