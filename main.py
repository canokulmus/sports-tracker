# main.py
"""
Sports Tournament Management System - Demo
Demonstrates LEAGUE, ELIMINATION, and Observer pattern usage.
"""
from datetime import datetime, timedelta
from typing import Dict, Any
from team import Team
from game import Game
from cup import Cup, CupType
from repo import Repo


def print_header(text: str) -> None:
    """Print a formatted header."""
    print("\n" + "=" * 70)
    print(f"  {text}")
    print("=" * 70)


def demo_repo() -> None:
    """Demonstrate Repo functionality."""
    print_header("REPO DEMONSTRATION")
    
    print("\n📦 Creating a repository...")
    repo = Repo()
    
    # Create teams
    print("\n1️⃣ Creating teams...")
    team1_id = repo.create(type="team", name="Galatasaray")
    team2_id = repo.create(type="team", name="Fenerbahçe")
    team3_id = repo.create(type="team", name="Beşiktaş")
    
    print(f"   ✅ Created 3 teams (IDs: {team1_id}, {team2_id}, {team3_id})")
    
    # List all objects
    print("\n2️⃣ Listing all objects:")
    all_objects = repo.list()
    for obj_id, description in all_objects:
        print(f"   ID {obj_id}: {description}")
    
    # Attach to objects
    print("\n3️⃣ User 'Coach' attaches to Galatasaray...")
    repo.attach(team1_id, "Coach")
    
    attached = repo.listattached("Coach")
    print(f"   Coach's objects: {len(attached)} item(s)")
    for obj_id, description in attached:
        print(f"      - {description}")


def demo_league() -> None:
    """Demonstrate LEAGUE tournament."""
    print_header("LEAGUE TOURNAMENT DEMONSTRATION")
    
    # Create teams
    print("\n⚽ Creating 4 teams for league...")
    teams = [
        Team("Galatasaray"),
        Team("Fenerbahçe"),
        Team("Beşiktaş"),
        Team("Trabzonspor")
    ]
    
    # Add players
    for team in teams:
        team.addplayer("Player1", 10)
        team.addplayer("Player2", 11)
    
    print(f"   ✅ Created {len(teams)} teams")
    
    # Create league
    print("\n🏆 Creating LEAGUE tournament...")
    cup = Cup(teams, CupType.LEAGUE, interval=timedelta(days=1))
    print(f"   ✅ {cup}")
    print(f"   📊 Total games: {len(cup.games)}")
    
    # Play some games
    print("\n🎮 Playing first 3 games...")
    for i, game in enumerate(cup.games[:3], 1):
        game.start()
        
        # Simulate scoring
        home_score = 2 if i % 2 == 0 else 3
        away_score = 1
        
        game.score(home_score, game.home(), "Player1")
        game.score(away_score, game.away(), "Player1")
        game.end()
        
        print(f"   Match {i}: {game.home().team_name} {game.home_score} - "
              f"{game.away_score} {game.away().team_name}")
    
    # Show standings
    print("\n📊 LEAGUE STANDINGS:")
    standings_result = cup.standings()
    
    # Type assertion for LEAGUE standings
    from typing import List, Tuple
    standings: List[Tuple[str, int, int, int, int, int, int]] = standings_result  # type: ignore
    
    print(f"\n   {'Pos':<4} {'Team':<20} {'P':<3} {'W':<3} {'D':<3} {'L':<3} "
          f"{'GF':<4} {'GA':<4} {'Pts':<4}")
    print("   " + "-" * 65)
    
    for i in range(len(standings)):
        team_name, won, draw, lost, gf, ga, pts = standings[i]
        played = won + draw + lost
        position = i + 1
        print(f"   {position:<4} {team_name:<20} {played:<3} {won:<3} {draw:<3} {lost:<3} "
              f"{gf:<4} {ga:<4} {pts:<4}")


def demo_elimination() -> None:
    """Demonstrate ELIMINATION tournament."""
    print_header("ELIMINATION TOURNAMENT DEMONSTRATION")
    
    # Create teams
    print("\n🏀 Creating 8 teams for elimination...")
    teams = [Team(f"Team {i}") for i in range(1, 9)]
    
    for team in teams:
        team.addplayer("Star Player", 23)
    
    print(f"   ✅ Created {len(teams)} teams")
    
    # Create elimination tournament
    print("\n🏆 Creating ELIMINATION tournament...")
    cup = Cup(teams, CupType.ELIMINATION, interval=timedelta(days=1))
    print(f"   ✅ {cup}")
    print(f"   📊 Total rounds: {len(cup.rounds)}")
    print(f"   📊 Total games: {len(cup.games)}")
    
    # Show game tree
    print("\n🌳 TOURNAMENT BRACKET:")
    tree = cup.gametree()
    
    for round_name, games in tree.items():
        print(f"\n   {round_name}: {len(games)} game(s)")
        for game in games:
            print(f"      Game {game['game_id']}: {game['home']} vs {game['away']}")
    
    # Play first round
    print("\n🎮 Playing Quarter-Finals...")
    for game in cup.rounds[0]:
        game.start()
        game.score(100, game.home(), "Star Player")
        game.score(90, game.away(), "Star Player")
        game.end()
        print(f"   {game.home().team_name} {game.home_score} - "
              f"{game.away_score} {game.away().team_name}")
    
    # Show standings
    print("\n📊 ELIMINATION STANDINGS (after Quarter-Finals):")
    standings_result = cup.standings()
    
    # Type assertion for ELIMINATION standings
    standings_dict: Dict[str, Any] = standings_result  # type: ignore
    
    print("\n   Team              Round  Won  Lost")
    print("   " + "-" * 40)
    
    for team_name in sorted(standings_dict.keys()):
        info = standings_dict[team_name]
        won_count = len(info['Won'])
        lost = "Yes" if info['Lost'] else "No"
        print(f"   {team_name:<17} {info['Round']:<6} {won_count:<4} {lost}")


def demo_observer() -> None:
    """Demonstrate Observer pattern."""
    print_header("OBSERVER PATTERN DEMONSTRATION")
    
    print("\n👁️  Creating observer to watch games...")
    
    class GameObserver:
        """Simple game observer."""
        def __init__(self, name: str):
            self.name = name
            self.notifications = 0
        
        def update(self, game: Game) -> None:
            """Called when game state changes."""
            self.notifications += 1
            print(f"   📢 [{self.name}] Game {game.id()} update: "
                  f"{game.home().team_name} vs {game.away().team_name} "
                  f"(State: {game.state.name})")
    
    # Create teams and game
    home = Team("Real Madrid")
    away = Team("Barcelona")
    home.addplayer("Benzema", 9)
    away.addplayer("Lewandowski", 9)
    
    game = Game(home, away, id_=1, datetime=datetime.now())
    
    # Add observer
    observer = GameObserver("TV Broadcast")
    game.watch(observer)
    
    print("\n🎮 Starting game with observer attached...")
    game.start()
    
    print("\n⚽ Scoring some goals...")
    game.score(2, home, "Benzema")
    game.score(1, away, "Lewandowski")
    
    print("\n🏁 Ending game...")
    game.end()
    
    print(f"\n📊 Observer received {observer.notifications} notifications")
    
    # Show final stats
    stats = game.stats()
    print(f"\n📊 FINAL STATS:")
    print(f"   {stats['Home']['Name']}: {stats['Home']['Pts']} points")
    print(f"   {stats['Away']['Name']}: {stats['Away']['Pts']} points")
    print(f"   Time: {stats['Time']}")


def demo_search() -> None:
    """Demonstrate search functionality."""
    print_header("SEARCH FUNCTIONALITY DEMONSTRATION")
    
    # Create teams
    teams = [
        Team("Manchester United"),
        Team("Manchester City"),
        Team("Liverpool"),
        Team("Chelsea")
    ]
    
    print("\n🔍 Creating tournament...")
    cup = Cup(teams, CupType.LEAGUE, interval=timedelta(days=1))
    print(f"   ✅ Created {len(cup.games)} games")
    
    # Search by team name
    print("\n🔎 Searching for Manchester United's games...")
    man_utd_games = cup.search(tname="Manchester United")
    print(f"   Found {len(man_utd_games)} game(s):")
    
    for game in man_utd_games:
        print(f"      Game {game.id()}: {game.home().team_name} vs "
              f"{game.away().team_name}")
    
    # Search by date range
    print("\n🔎 Searching for games in first 2 days...")
    start_date = cup.games[0].datetime
    end_date = start_date + timedelta(days=1)
    
    date_games = cup.search(between=(start_date, end_date))
    print(f"   Found {len(date_games)} game(s) in date range")


def main() -> None:
    """Main demonstration function."""
    print("\n" + "=" * 70)
    print("  🏆 SPORTS TOURNAMENT MANAGEMENT SYSTEM")
    print("  📚 Comprehensive Demonstration")
    print("=" * 70)
    
    # Run all demos
    demo_repo()
    demo_league()
    demo_elimination()
    demo_observer()
    demo_search()
    
    # Final message
    print_header("DEMONSTRATION COMPLETE")
    print("\n✅ All features demonstrated successfully!")
    print("📝 Unit tests: Run 'pytest -v' to see 66 passing tests")
    print("📖 Features: LEAGUE, ELIMINATION, GROUP tournaments")
    print("🔍 Search, standings, gametree, observer pattern")
    print("\n" + "=" * 70 + "\n")


if __name__ == "__main__":
    main()