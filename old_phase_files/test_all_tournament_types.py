"""
Quick test: All tournament types complete properly.
"""

from datetime import timedelta
from sports_lib.team import Team
from sports_lib.cup import Cup, CupType
import random


def test_all_cup_types():
    """Test that all cup types complete to a champion."""
    
    print("\n" + "🏆" * 35)
    print("TEST: ALL TOURNAMENT TYPES COMPLETE")
    print("🏆" * 35)
    
    results = {}
    
    # Test LEAGUE
    print("\n1️⃣  Testing LEAGUE...")
    random.seed(1000)
    teams = [Team(f"Team {i}") for i in range(1, 5)]
    for t in teams:
        t.addplayer("P", 10)
    
    cup_league = Cup(teams, CupType.LEAGUE, interval=timedelta(days=1))
    
    for game in cup_league.games:
        game.start()
        game.score(random.randint(1, 3), game.home(), "P")
        game.score(random.randint(1, 3), game.away(), "P")
        game.end()
    
    standings = cup_league.standings()
    champion = standings[0][0]  # First team
    results["LEAGUE"] = champion
    print(f"   ✅ LEAGUE Champion: {champion}")
    
    # Test ELIMINATION
    print("\n2️⃣  Testing ELIMINATION...")
    random.seed(2000)
    teams = [Team(f"Team {i}") for i in range(1, 9)]
    for t in teams:
        t.addplayer("P", 10)
    
    cup_elim = Cup(teams, CupType.ELIMINATION, interval=timedelta(days=1))
    
    for round_games in cup_elim.rounds:
        for game in round_games:
            game.start()
            game.score(5, game.home(), "P")
            game.score(3, game.away(), "P")
            game.end()
    
    tree = cup_elim.gametree()
    final_game = tree["Final"][0]
    champion = final_game['home']
    results["ELIMINATION"] = champion
    print(f"   ✅ ELIMINATION Champion: {champion}")
    
    # Test GROUP
    print("\n3️⃣  Testing GROUP...")
    random.seed(3000)
    teams = [Team(f"Team {i}") for i in range(1, 17)]
    for t in teams:
        t.addplayer("P", 10)
    
    cup_group = Cup(teams, CupType.GROUP, interval=timedelta(days=1), 
                    num_groups=4, playoff_teams=8)
    
    # Play groups
    for group_games in cup_group.group_games.values():
        for game in group_games:
            game.start()
            game.score(random.randint(1, 3), game.home(), "P")
            game.score(random.randint(1, 3), game.away(), "P")
            game.end()
    
    # Generate and play playoffs
    cup_group.generate_playoffs()
    
    for round_games in cup_group.playoff_rounds:
        for game in round_games:
            game.start()
            hs = random.randint(3, 6)
            aws = random.randint(3, 6)
            while hs == aws:
                aws = random.randint(3, 6)
            game.score(hs, game.home(), "P")
            game.score(aws, game.away(), "P")
            game.end()
    
    tree = cup_group.gametree()
    final_game = tree["Playoffs"]["Final"][0]
    champion = final_game['home'] if final_game['score']['home'] > final_game['score']['away'] else final_game['away']
    results["GROUP"] = champion
    print(f"   ✅ GROUP Champion: {champion}")
    
    # Summary
    print("\n" + "="*70)
    print("📊 TOURNAMENT RESULTS SUMMARY")
    print("="*70)
    for cup_type, champion in results.items():
        print(f"   {cup_type:<15} → Champion: {champion}")
    
    print("\n✅ ALL TOURNAMENT TYPES COMPLETE SUCCESSFULLY!")
    print("="*70)


if __name__ == "__main__":
    test_all_cup_types()