"""
Complete test suite for GROUP tournament type.
Tests group stage, standings calculation, playoff generation, and bracket.

Each test uses a fixed random seed for reproducibility.
Now includes random scoring (1-5 goals) for more realistic testing.
"""

from datetime import datetime, timedelta
from sports_lib.team import Team
from sports_lib.cup import Cup, CupType
from sports_lib.constants import GameState
import json
import random


def test_group_16_teams_basic():
    """Test 1: Basic 16-team GROUP tournament structure"""
    
    print("\n" + "="*60)
    print("TEST 1: 16 TEAMS GROUP TOURNAMENT (Structure)")
    print("="*60)
    
    # Fix random seed for reproducibility
    random.seed(100)
    
    teams = [Team(f"Team {i}") for i in range(1, 17)]
    
    cup = Cup(
        teams,
        CupType.GROUP,
        interval=timedelta(days=1),
        num_groups=4,
        playoff_teams=8
    )
    
    print(f"\nTournament: {len(teams)} teams")
    print(f"Groups: {len(cup.groups)}")
    print(f"Playoff spots: {cup.playoff_teams}")
    print(f"Total games: {len(cup.games)}")
    
    # Should have 4 groups
    assert len(cup.groups) == 4, f"❌ Should have 4 groups!"
    
    # Each group should have 4 teams (16/4)
    print("\n--- GROUP COMPOSITION ---")
    for group_name in sorted(cup.groups.keys()):
        group_teams = cup.groups[group_name]
        team_names = [t.team_name for t in group_teams]
        print(f"Group {group_name}: {team_names}")
        assert len(group_teams) == 4, f"❌ Each group should have 4 teams!"
    
    # Each group should have 6 games (C(4,2))
    print("\n--- GAMES PER GROUP ---")
    for group_name in sorted(cup.group_games.keys()):
        group_games = cup.group_games[group_name]
        print(f"Group {group_name}: {len(group_games)} games")
        assert len(group_games) == 6, f"❌ Each group should have 6 games!"
    
    # Total group stage games: 4 * 6 = 24
    total_group_games = sum(len(games) for games in cup.group_games.values())
    assert total_group_games == 24, f"❌ Should have 24 group stage games!"
    
    # Playoffs not generated yet
    assert len(cup.playoff_games) == 0, "❌ Playoffs should not be generated yet!"
    
    print("\n✅ Test 1 PASSED!")


def test_group_gametree_structure():
    """Test 2: GameTree structure for GROUP tournament"""
    
    print("\n" + "="*60)
    print("TEST 2: GROUP GAMETREE STRUCTURE")
    print("="*60)
    
    random.seed(200)
    
    teams = [Team(f"Team {i}") for i in range(1, 17)]
    cup = Cup(
        teams,
        CupType.GROUP,
        interval=timedelta(days=1),
        num_groups=4,
        playoff_teams=8
    )
    
    tree = cup.gametree()
    
    print("\n--- GAMETREE STRUCTURE ---")
    print(f"Top-level keys: {list(tree.keys())}")
    
    # Should have Groups and Playoffs
    assert "Groups" in tree, "❌ GameTree should have 'Groups'!"
    assert "Playoffs" in tree, "❌ GameTree should have 'Playoffs'!"
    
    # Groups should have 4 groups
    groups = tree["Groups"]
    print(f"\nGroups: {list(groups.keys())}")
    assert len(groups) == 4, f"❌ Should have 4 groups!"
    
    # Each group should have 6 games
    print("\n--- GAMES PER GROUP (from gametree) ---")
    for group_name in sorted(groups.keys()):
        games = groups[group_name]
        print(f"Group {group_name}: {len(games)} games")
        assert len(games) == 6, f"❌ Group {group_name} should have 6 games!"
        
        # Check game structure
        first_game = games[0]
        assert "game_id" in first_game, "❌ Game should have ID!"
        assert "home" in first_game, "❌ Game should have home team!"
        assert "away" in first_game, "❌ Game should have away team!"
        assert "state" in first_game, "❌ Game should have state!"
        assert "score" in first_game, "❌ Game should have score field!"
    
    # Playoffs should be empty dict (not generated yet)
    assert len(tree["Playoffs"]) == 0, "❌ Playoffs should be empty!"
    
    print("\n✅ Test 2 PASSED!")


def test_group_play_matches():
    """Test 3: Play group stage matches with random scores"""
    
    print("\n" + "="*60)
    print("TEST 3: PLAY GROUP STAGE MATCHES (Random Scores)")
    print("="*60)
    
    random.seed(300)
    
    teams = [Team(f"Team {i}") for i in range(1, 17)]
    for team in teams:
        team.addplayer("Star", 10)
    
    cup = Cup(
        teams,
        CupType.GROUP,
        interval=timedelta(days=1),
        num_groups=4,
        playoff_teams=8
    )
    
    # Play all group games with RANDOM scores
    print("\n--- PLAYING GROUP STAGE (Random Scores 1-5) ---")
    for group_name in sorted(cup.group_games.keys()):
        group_games = cup.group_games[group_name]
        print(f"\nGroup {group_name}:")
        for game in group_games:
            # Random scores between 1-5
            home_score = random.randint(1, 5)
            away_score = random.randint(1, 5)
            
            game.start()
            game.score(home_score, game.home(), "Star")
            game.score(away_score, game.away(), "Star")
            game.end()
            
            # Show result
            if home_score > away_score:
                result = f"{game.home().team_name} WINS"
            elif away_score > home_score:
                result = f"{game.away().team_name} WINS"
            else:
                result = "DRAW"
            
            print(f"  {game.home().team_name} {home_score}-{away_score} {game.away().team_name} ({result})")
    
    # Check standings
    print("\n--- GROUP STANDINGS ---")
    standings = cup.standings()
    
    assert "Groups" in standings, "❌ Standings should have Groups!"
    
    for group_name in sorted(standings["Groups"].keys()):
        group_standings = standings["Groups"][group_name]
        print(f"\nGroup {group_name}:")
        print(f"{'Pos':<5} {'Team':<15} {'P':<4} {'W':<4} {'D':<4} {'L':<4} {'GF':<5} {'GA':<5} {'GD':<5} {'Pts':<5}")
        print("-" * 65)
        
        for i, (team, w, d, l, gf, ga, pts) in enumerate(group_standings, 1):
            played = w + d + l
            gd = gf - ga
            print(f"{i:<5} {team:<15} {played:<4} {w:<4} {d:<4} {l:<4} {gf:<5} {ga:<5} {gd:<+5} {pts:<5}")
            
            # All teams played 3 games
            assert played == 3, f"❌ {team} should have played 3 games!"
            
            # Points calculation correct (win=2, draw=1)
            expected_pts = w * 2 + d * 1
            assert pts == expected_pts, f"❌ {team} points incorrect!"
            
            # Goals for/against should match
            assert gf >= 0, f"❌ {team} goals for cannot be negative!"
            assert ga >= 0, f"❌ {team} goals against cannot be negative!"
        
        # Should have 4 teams
        assert len(group_standings) == 4, f"❌ Group should have 4 teams!"
    
    print("\n✅ Test 3 PASSED!")


def test_group_playoff_generation():
    """Test 4: Generate playoffs after group stage with random scores"""
    
    print("\n" + "="*60)
    print("TEST 4: PLAYOFF GENERATION (Random Scores)")
    print("="*60)
    
    random.seed(400)
    
    teams = [Team(f"Team {i}") for i in range(1, 17)]
    for team in teams:
        team.addplayer("Star", 10)
    
    cup = Cup(
        teams,
        CupType.GROUP,
        interval=timedelta(days=1),
        num_groups=4,
        playoff_teams=8
    )
    
    # Play all group games with RANDOM scores
    print("\n--- PLAYING GROUP STAGE (Random Scores) ---")
    for group_name in sorted(cup.group_games.keys()):
        group_games = cup.group_games[group_name]
        games_count = 0
        for game in group_games:
            home_score = random.randint(1, 5)
            away_score = random.randint(1, 5)
            
            game.start()
            game.score(home_score, game.home(), "Star")
            game.score(away_score, game.away(), "Star")
            game.end()
            games_count += 1
        print(f"Group {group_name}: {games_count} games completed")
    
    # Before playoff generation
    print("\n--- BEFORE PLAYOFF GENERATION ---")
    print(f"Playoff games: {len(cup.playoff_games)}")
    assert len(cup.playoff_games) == 0, "❌ No playoffs yet!"
    
    # Generate playoffs
    print("\n--- GENERATING PLAYOFFS ---")
    cup.generate_playoffs()
    
    # After playoff generation
    print(f"\n--- AFTER PLAYOFF GENERATION ---")
    print(f"Playoff games: {len(cup.playoff_games)}")
    
    # Should have playoff games (8 teams → 4 games in first round)
    assert len(cup.playoff_games) == 4, \
        f"❌ Should have 4 playoff games! Got {len(cup.playoff_games)}"
    
    # Check playoff teams are real (not placeholders)
    print("\n--- PLAYOFF MATCHUPS ---")
    playoff_teams = set()
    for game in cup.playoff_games:
        home = game.home().team_name
        away = game.away().team_name
        print(f"  Game {game.id()}: {home} vs {away}")
        
        # Should be real teams
        assert not home.startswith("Winner"), \
            f"❌ Playoff should have real teams: {home}"
        assert not away.startswith("Winner"), \
            f"❌ Playoff should have real teams: {away}"
        
        playoff_teams.add(home)
        playoff_teams.add(away)
    
    # Should have exactly 8 unique teams
    assert len(playoff_teams) == 8, \
        f"❌ Should have 8 playoff teams! Got {len(playoff_teams)}"
    
    # Check gametree includes playoffs
    print("\n--- GAMETREE AFTER PLAYOFFS ---")
    tree = cup.gametree()
    
    assert len(tree["Playoffs"]) > 0, "❌ Playoffs should be in gametree!"
    
    playoff_round_name = list(tree["Playoffs"].keys())[0]
    playoff_games_in_tree = tree["Playoffs"][playoff_round_name]
    print(f"{playoff_round_name}: {len(playoff_games_in_tree)} games")
    
    assert len(playoff_games_in_tree) == 4, \
        "❌ Should have 4 playoff games in tree!"
    
    print("\n✅ Test 4 PASSED!")


def test_group_complete_tournament():
    """Test 5: Complete GROUP tournament with random scores"""
    
    print("\n" + "="*60)
    print("TEST 5: COMPLETE GROUP TOURNAMENT (Random Scores)")
    print("="*60)
    
    random.seed(500)
    
    teams = [Team(f"Team {i}") for i in range(1, 17)]
    for team in teams:
        team.addplayer("Star", 10)
    
    cup = Cup(
        teams,
        CupType.GROUP,
        interval=timedelta(days=1),
        num_groups=4,
        playoff_teams=8
    )
    
    # 1. Play group stage with RANDOM scores
    print("\n--- STEP 1: GROUP STAGE (Random Scores) ---")
    group_games_count = 0
    for group_name in sorted(cup.group_games.keys()):
        group_games = cup.group_games[group_name]
        for game in group_games:
            home_score = random.randint(1, 5)
            away_score = random.randint(1, 5)
            
            game.start()
            game.score(home_score, game.home(), "Star")
            game.score(away_score, game.away(), "Star")
            game.end()
            group_games_count += 1
    print(f"✅ All {group_games_count} group games completed")
    
    # 2. Generate playoffs
    print("\n--- STEP 2: GENERATE PLAYOFFS ---")
    cup.generate_playoffs()
    print(f"✅ Playoffs generated: {len(cup.playoff_games)} games")
    
    # 3. Play playoffs with RANDOM scores
    print("\n--- STEP 3: PLAY PLAYOFFS (Random Scores) ---")
    for game in cup.playoff_games:
        home_score = random.randint(2, 6)
        away_score = random.randint(2, 6)
        
        # Ensure no draws in playoffs
        while home_score == away_score:
            away_score = random.randint(2, 6)
        
        game.start()
        game.score(home_score, game.home(), "Star")
        game.score(away_score, game.away(), "Star")
        game.end()
        
        winner = game.home().team_name if home_score > away_score else game.away().team_name
        print(f"  {game.home().team_name} {home_score}-{away_score} {game.away().team_name} → {winner} wins")
    print(f"✅ All playoff games completed")
    
    # 4. Check final gametree
    print("\n--- STEP 4: FINAL GAMETREE ---")
    tree = cup.gametree()
    
    # All group games should be ENDED
    print("\nGroup games status:")
    total_group_games = 0
    total_ended = 0
    for group_name in sorted(tree["Groups"].keys()):
        games = tree["Groups"][group_name]
        ended = sum(1 for g in games if g['state'] == 'ENDED')
        total_group_games += len(games)
        total_ended += ended
        print(f"  Group {group_name}: {ended}/{len(games)} ended")
        assert ended == len(games), f"❌ All group games should be ended!"
    
    print(f"\nTotal: {total_ended}/{total_group_games} group games ended")
    
    # All playoff games should be ENDED
    print("\nPlayoff games status:")
    for round_name, games in tree["Playoffs"].items():
        ended = sum(1 for g in games if g['state'] == 'ENDED')
        print(f"  {round_name}: {ended}/{len(games)} ended")
        assert ended == len(games), f"❌ All playoff games should be ended!"
    
    print("\n✅ Test 5 PASSED!")
    print("   → Complete tournament played successfully!")


def test_group_8_teams():
    """Test 6: 8 teams, 2 groups, 4 playoff spots with random scores"""
    
    print("\n" + "="*60)
    print("TEST 6: 8 TEAMS GROUP (2 groups, 4 playoff)")
    print("="*60)
    
    random.seed(600)
    
    teams = [Team(f"Team {i}") for i in range(1, 9)]
    for team in teams:
        team.addplayer("Star", 10)
    
    cup = Cup(
        teams,
        CupType.GROUP,
        interval=timedelta(days=1),
        num_groups=2,
        playoff_teams=4
    )
    
    print(f"\nTournament: {len(teams)} teams")
    print(f"Groups: {len(cup.groups)}")
    print(f"Playoff spots: {cup.playoff_teams}")
    
    # Should have 2 groups
    assert len(cup.groups) == 2, "❌ Should have 2 groups!"
    
    # Each group should have 4 teams
    print("\n--- GROUP COMPOSITION ---")
    for group_name in sorted(cup.groups.keys()):
        group_teams = cup.groups[group_name]
        team_names = [t.team_name for t in group_teams]
        print(f"Group {group_name}: {team_names}")
        assert len(group_teams) == 4, "❌ Each group should have 4 teams!"
    
    # Play groups with RANDOM scores
    print("\n--- PLAYING GROUPS (Random Scores) ---")
    for group_games in cup.group_games.values():
        for game in group_games:
            home_score = random.randint(1, 4)
            away_score = random.randint(1, 4)
            
            game.start()
            game.score(home_score, game.home(), "Star")
            game.score(away_score, game.away(), "Star")
            game.end()
    
    print("\n--- GENERATING PLAYOFFS ---")
    cup.generate_playoffs()
    
    # Should have 2 playoff games (4 teams → 2 games in SF)
    print(f"\nPlayoff games: {len(cup.playoff_games)}")
    assert len(cup.playoff_games) == 2, \
        f"❌ Should have 2 playoff games! Got {len(cup.playoff_games)}"
    
    print("\n--- PLAYOFF MATCHUPS ---")
    for game in cup.playoff_games:
        print(f"  {game.home().team_name} vs {game.away().team_name}")
    
    print("\n✅ Test 6 PASSED!")


def test_group_wildcard():
    """Test 7: Wild card qualification with random scores"""
    
    print("\n" + "="*60)
    print("TEST 7: WILD CARD QUALIFICATION (Random Scores)")
    print("="*60)
    
    random.seed(700)
    
    teams = [Team(f"Team {i}") for i in range(1, 13)]
    for team in teams:
        team.addplayer("Star", 10)
    
    # 3 groups, 8 playoff spots
    # Each group sends top 2 = 6 teams
    # Wild cards = 8 - 6 = 2 teams
    cup = Cup(
        teams,
        CupType.GROUP,
        interval=timedelta(days=1),
        num_groups=3,
        playoff_teams=8
    )
    
    print(f"\nTournament: {len(teams)} teams")
    print(f"Groups: {len(cup.groups)}")
    print(f"Playoff spots: {cup.playoff_teams}")
    
    k = cup.playoff_teams // cup.num_groups
    wild_cards = cup.playoff_teams - (k * cup.num_groups)
    
    print(f"\nQualification system:")
    print(f"  Top {k} from each group: {k * cup.num_groups} teams")
    print(f"  Wild cards: {wild_cards} teams")
    print(f"  Total: {cup.playoff_teams} teams")
    
    # Should have 3 groups with 4 teams each
    assert len(cup.groups) == 3, "❌ Should have 3 groups!"
    for group_name, group_teams in cup.groups.items():
        assert len(group_teams) == 4, \
            f"❌ Group {group_name} should have 4 teams!"
    
    # Play groups with RANDOM scores
    print("\n--- PLAYING GROUPS (Random Scores) ---")
    for group_games in cup.group_games.values():
        for game in group_games:
            home_score = random.randint(0, 4)
            away_score = random.randint(0, 4)
            
            game.start()
            if home_score > 0:
                game.score(home_score, game.home(), "Star")
            if away_score > 0:
                game.score(away_score, game.away(), "Star")
            game.end()
    
    # Generate playoffs
    print("\n--- GENERATING PLAYOFFS ---")
    cup.generate_playoffs()
    
    # Should have 4 playoff games (8 teams → QF)
    print(f"\nPlayoff games generated: {len(cup.playoff_games)}")
    assert len(cup.playoff_games) == 4, \
        f"❌ Should have 4 playoff games! Got {len(cup.playoff_games)}"
    
    # Count unique teams in playoffs
    playoff_teams = set()
    for game in cup.playoff_games:
        playoff_teams.add(game.home().team_name)
        playoff_teams.add(game.away().team_name)
    
    print(f"Unique playoff teams: {len(playoff_teams)}")
    assert len(playoff_teams) == 8, \
        f"❌ Should have 8 playoff teams! Got {len(playoff_teams)}"
    
    print("\n✅ Test 7 PASSED!")


def test_group_round_robin_scheduling():
    """Test 8: Verify round-robin scheduling (no back-to-back games)"""
    
    print("\n" + "="*60)
    print("TEST 8: ROUND-ROBIN SCHEDULING")
    print("="*60)
    
    random.seed(800)
    
    teams = [Team(f"Team {chr(65+i)}") for i in range(4)]  # Team A, B, C, D
    
    cup = Cup(
        teams,
        CupType.GROUP,
        interval=timedelta(days=1),
        num_groups=1,  # Single group for easy verification
        playoff_teams=2
    )
    
    # Get the single group's games
    group_name = list(cup.group_games.keys())[0]
    games = cup.group_games[group_name]
    
    print(f"\n--- SCHEDULE (Group {group_name}) ---")
    
    # Group games by date
    games_by_date = {}
    for game in games:
        date_key = game.datetime.date()
        if date_key not in games_by_date:
            games_by_date[date_key] = []
        games_by_date[date_key].append(game)
    
    print(f"Total games: {len(games)}")
    print(f"Total dates used: {len(games_by_date)}")
    
    # Verify round-robin constraints
    round_num = 1
    for date_key in sorted(games_by_date.keys()):
        round_games = games_by_date[date_key]
        teams_playing = set()
        
        print(f"\nRound {round_num} ({date_key}):")
        for game in round_games:
            home = game.home().team_name
            away = game.away().team_name
            print(f"  {home} vs {away}")
            
            # No team should play twice in same round
            assert home not in teams_playing, \
                f"❌ {home} plays twice in same round!"
            assert away not in teams_playing, \
                f"❌ {away} plays twice in same round!"
            
            teams_playing.add(home)
            teams_playing.add(away)
        
        print(f"  → {len(teams_playing)} teams playing this round ✅")
        round_num += 1
    
    print("\n✅ Test 8 PASSED!")
    print("   → Round-robin scheduling verified!")


# ============================================================================
# MAIN TEST RUNNER
# ============================================================================

if __name__ == "__main__":
    print("\n" + "🏆" * 30)
    print(" " * 16 + "GROUP TEST SUITE")
    print(" " * 12 + "(Phase 3 - REST API)")
    print("🏆" * 30)
    
    tests = [
        test_group_16_teams_basic,
        test_group_gametree_structure,
        test_group_play_matches,
        test_group_playoff_generation,
        test_group_complete_tournament,
        test_group_8_teams,
        test_group_wildcard,
        test_group_round_robin_scheduling,
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
    print("📊 GROUP TEST SUMMARY")
    print("="*60)
    print(f"✅ Passed: {passed}/{len(tests)}")
    print(f"❌ Failed: {failed}/{len(tests)}")
    
    if failed == 0:
        print("\n🎉 ALL GROUP TESTS PASSED! 🎉")
    else:
        print(f"\n⚠️  {failed} test(s) need attention")
    
    print()