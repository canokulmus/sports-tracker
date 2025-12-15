"""
Complete test suite for LEAGUE tournament type.
Tests round-robin scheduling, standings calculation, and game tracking.
"""

from datetime import datetime, timedelta
from sports_lib.team import Team
from sports_lib.cup import Cup, CupType
from sports_lib.constants import GameState
import json


def test_league_4_teams():
    """Test 1: Basic 4-team LEAGUE"""
    
    print("\n" + "="*60)
    print("TEST 1: 4 TEAMS LEAGUE (Single Round-Robin)")
    print("="*60)
    
    teams = [Team(f"Team {chr(65+i)}") for i in range(4)]  # Team A, B, C, D
    for team in teams:
        team.addplayer("Player1", 10)
    
    cup = Cup(teams, CupType.LEAGUE, interval=timedelta(days=1))
    
    print(f"\nTournament: {len(teams)} teams")
    print(f"Expected games: C(4,2) = 6 games")
    print(f"Actual games: {len(cup.games)}")
    
    # Should have 6 games (C(4,2))
    assert len(cup.games) == 6, f"❌ Should have 6 games, got {len(cup.games)}"
    
    # Each team should play 3 games
    print("\n--- SCHEDULE CHECK ---")
    for team in teams:
        team_games = cup.search(tname=team.team_name)
        print(f"{team.team_name}: {len(team_games)} games")
        assert len(team_games) == 3, f"❌ Each team should play 3 games!"
    
    # Check round-robin (no team plays back-to-back)
    print("\n--- ROUND-ROBIN VALIDATION ---")
    games_by_date = {}
    for game in cup.games:
        date_key = game.datetime.date()
        if date_key not in games_by_date:
            games_by_date[date_key] = []
        games_by_date[date_key].append(game)
    
    for date_key in sorted(games_by_date.keys()):
        games = games_by_date[date_key]
        print(f"\n{date_key}:")
        teams_playing = set()
        for game in games:
            print(f"  {game.home().team_name} vs {game.away().team_name}")
            
            # Check no duplicate teams in same round
            assert game.home().team_name not in teams_playing, \
                f"❌ {game.home().team_name} plays twice on {date_key}!"
            assert game.away().team_name not in teams_playing, \
                f"❌ {game.away().team_name} plays twice on {date_key}!"
            
            teams_playing.add(game.home().team_name)
            teams_playing.add(game.away().team_name)
    
    print("\n✅ Round-robin schedule is valid!")
    
    # Initial standings (no games played)
    print("\n--- INITIAL STANDINGS ---")
    standings = cup.standings()
    print(f"{'Pos':<5} {'Team':<12} {'W':<4} {'D':<4} {'L':<4} {'Pts':<5}")
    print("-" * 40)
    for i, (team, w, d, l, gf, ga, pts) in enumerate(standings, 1):
        print(f"{i:<5} {team:<12} {w:<4} {d:<4} {l:<4} {pts:<5}")
        assert pts == 0, "❌ All teams should have 0 points initially!"
    
    print("\n✅ Test 1 PASSED!")


def test_league_play_games():
    """Test 2: Play games and track standings"""
    
    print("\n" + "="*60)
    print("TEST 2: PLAY GAMES AND STANDINGS")
    print("="*60)
    
    teams = [Team(f"Team {chr(65+i)}") for i in range(4)]
    for team in teams:
        team.addplayer("Star", 10)
    
    cup = Cup(teams, CupType.LEAGUE, interval=timedelta(days=1))
    
    # Play all games with predetermined results
    print("\n--- PLAYING GAMES ---")
    results = [
        (3, 1),  # Game 1: Home wins
        (2, 2),  # Game 2: Draw
        (1, 3),  # Game 3: Away wins
        (4, 0),  # Game 4: Home wins big
        (1, 1),  # Game 5: Draw
        (2, 3),  # Game 6: Away wins
    ]
    
    for i, game in enumerate(cup.games):
        home_score, away_score = results[i]
        
        game.start()
        game.score(home_score, game.home(), "Star")
        game.score(away_score, game.away(), "Star")
        game.end()
        
        winner = "Draw" if home_score == away_score else \
                 game.home().team_name if home_score > away_score else \
                 game.away().team_name
        
        print(f"Game {i+1}: {game.home().team_name} {home_score}-{away_score} {game.away().team_name} → {winner}")
    
    # Final standings
    print("\n--- FINAL STANDINGS ---")
    standings = cup.standings()
    print(f"{'Pos':<5} {'Team':<12} {'P':<4} {'W':<4} {'D':<4} {'L':<4} {'GF':<5} {'GA':<5} {'GD':<5} {'Pts':<5}")
    print("-" * 70)
    
    for i, (team, w, d, l, gf, ga, pts) in enumerate(standings, 1):
        played = w + d + l
        gd = gf - ga
        print(f"{i:<5} {team:<12} {played:<4} {w:<4} {d:<4} {l:<4} {gf:<5} {ga:<5} {gd:<+5} {pts:<5}")
    
    # Validations
    print("\n--- VALIDATION ---")
    
    # All teams played 3 games
    for team, w, d, l, gf, ga, pts in standings:
        played = w + d + l
        assert played == 3, f"❌ {team} should have played 3 games!"
    
    # Points calculation correct (win=2, draw=1)
    for team, w, d, l, gf, ga, pts in standings:
        expected_pts = w * 2 + d * 1
        assert pts == expected_pts, f"❌ {team} points wrong! Expected {expected_pts}, got {pts}"
    
    # Check sorting (by points, then goal difference)
    prev_pts = float('inf')
    for team, w, d, l, gf, ga, pts in standings:
        assert pts <= prev_pts, "❌ Standings should be sorted by points!"
        prev_pts = pts
    
    print("✅ All validations passed!")
    print("\n✅ Test 2 PASSED!")


def test_league_search():
    """Test 3: Search functionality"""
    
    print("\n" + "="*60)
    print("TEST 3: SEARCH FUNCTIONALITY")
    print("="*60)
    
    teams = [Team(f"Team {chr(65+i)}") for i in range(4)]
    cup = Cup(teams, CupType.LEAGUE, interval=timedelta(days=1))
    
    # Search all games
    print("\n--- SEARCH ALL ---")
    all_games = cup.search()
    print(f"Total games: {len(all_games)}")
    assert len(all_games) == 6, "❌ Should return all 6 games!"
    
    # Search by team
    print("\n--- SEARCH BY TEAM ---")
    team_a_games = cup.search(tname="Team A")
    print(f"Team A games: {len(team_a_games)}")
    assert len(team_a_games) == 3, "❌ Team A should have 3 games!"
    
    for game in team_a_games:
        print(f"  {game.home().team_name} vs {game.away().team_name}")
        assert game.home().team_name == "Team A" or game.away().team_name == "Team A", \
            "❌ All games should involve Team A!"
    
    # Search by date range
    print("\n--- SEARCH BY DATE RANGE ---")
    start_date = cup.games[0].datetime
    end_date = start_date + timedelta(days=2)
    
    date_games = cup.search(between=(start_date, end_date))
    print(f"Games in first 3 days: {len(date_games)}")
    
    for game in date_games:
        assert start_date <= game.datetime <= end_date, \
            "❌ Game outside date range!"
    
    # Search by ID
    print("\n--- SEARCH BY ID ---")
    game1 = cup[1]
    print(f"Game 1: {game1.home().team_name} vs {game1.away().team_name}")
    assert game1.id() == 1, "❌ Wrong game ID!"
    
    print("\n✅ Test 3 PASSED!")

def test_league_5_teams():
    """Test 5: Odd number of teams (BYE handling)"""
    
    print("\n" + "="*60)
    print("TEST 5: 5 TEAMS LEAGUE (Odd Number)")
    print("="*60)
    
    teams = [Team(f"Team {i}") for i in range(1, 6)]
    cup = Cup(teams, CupType.LEAGUE, interval=timedelta(days=1))
    
    print(f"\nTournament: {len(teams)} teams")
    print(f"Expected games: C(5,2) = 10 games")
    print(f"Actual games: {len(cup.games)}")
    
    assert len(cup.games) == 10, f"❌ Should have 10 games!"
    
    # Each team should play 4 games
    for team in teams:
        team_games = cup.search(tname=team.team_name)
        print(f"{team.team_name}: {len(team_games)} games")
        assert len(team_games) == 4, f"❌ Each team should play 4 games!"
    
    print("\n✅ Test 5 PASSED!")


# ============================================================================
# MAIN TEST RUNNER
# ============================================================================

if __name__ == "__main__":
    print("\n" + "🏆" * 30)
    print(" " * 15 + "LEAGUE TEST SUITE")
    print("🏆" * 30)
    
    tests = [
        test_league_4_teams,
        test_league_play_games,
        test_league_search,
        test_league_5_teams,
    ]
    
    passed = 0
    failed = 0
    
    for test_func in tests:
        try:
            test_func()
            passed += 1
        except AssertionError as e:
            failed += 1
            print(f"\n❌ TEST FAILED: {test_func.__name__}")
            print(f"   {e}")
        except Exception as e:
            failed += 1
            print(f"\n💥 ERROR: {test_func.__name__}")
            print(f"   {e}")
            import traceback
            traceback.print_exc()
    
    print("\n" + "="*60)
    print("📊 LEAGUE TEST SUMMARY")
    print("="*60)
    print(f"✅ Passed: {passed}/{len(tests)}")
    print(f"❌ Failed: {failed}/{len(tests)}")
    
    if failed == 0:
        print("\n🎉 ALL LEAGUE TESTS PASSED! 🎉")
    
    print()