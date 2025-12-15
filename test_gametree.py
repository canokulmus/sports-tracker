"""
Complete test suite for GameTree functionality.
Tests dynamic placeholder resolution and tournament bracket visualization.
"""

from datetime import datetime, timedelta
from sports_lib.team import Team
from sports_lib.cup import Cup, CupType
import json


def test_elimination_8_teams():
    """Test 1: 8 teams elimination bracket"""
    
    print("\n" + "="*60)
    print("TEST 1: 8 TEAMS ELIMINATION")
    print("="*60)
    
    # Create 8 teams
    teams = [Team(f"Team {i}") for i in range(1, 9)]
    
    # Create elimination cup
    cup = Cup(teams, CupType.ELIMINATION, interval=timedelta(days=1))
    
    # Get GameTree
    tree = cup.gametree()
    
    # Pretty print
    print("\nGameTree Structure:")
    print(json.dumps(tree, indent=2))
    
    # Validations
    print("\n--- VALIDATION ---")
    
    # Check round names
    print(f"Rounds: {list(tree.keys())}")
    assert "Quarter-Final" in tree, "❌ Quarter-Final missing!"
    assert "Semi-Final" in tree, "❌ Semi-Final missing!"
    assert "Final" in tree, "❌ Final missing!"
    
    # Check number of games per round
    print(f"Quarter-Final games: {len(tree['Quarter-Final'])}")
    print(f"Semi-Final games: {len(tree['Semi-Final'])}")
    print(f"Final games: {len(tree['Final'])}")
    
    assert len(tree['Quarter-Final']) == 4, "❌ Should have 4 QF games!"
    assert len(tree['Semi-Final']) == 2, "❌ Should have 2 SF games!"
    assert len(tree['Final']) == 1, "❌ Should have 1 Final game!"
    
    # Check placeholder teams
    print("\n--- PLACEHOLDER CHECK ---")
    for round_name, games in tree.items():
        print(f"\n{round_name}:")
        for game in games:
            home = game['home']
            away = game['away']
            state = game.get('state', 'UNKNOWN')
            print(f"  Game {game['game_id']}: {home} vs {away} [{state}]")
            
            # First round should have real teams
            if round_name == "Quarter-Final":
                assert not home.startswith("Winner"), f"❌ QF shouldn't have placeholder: {home}"
                assert not away.startswith("Winner"), f"❌ QF shouldn't have placeholder: {away}"
            else:
                # Other rounds should have placeholders (games not played yet)
                assert home.startswith("Winner") or away.startswith("Winner"), \
                    f"❌ {round_name} should have placeholders!"
    
    print("\n✅ Test 1 PASSED!")
    return tree


def test_elimination_4_teams():
    """Test 2: 4 teams elimination bracket"""
    
    print("\n" + "="*60)
    print("TEST 2: 4 TEAMS ELIMINATION")
    print("="*60)
    
    teams = [Team(f"Team {i}") for i in range(1, 5)]
    cup = Cup(teams, CupType.ELIMINATION, interval=timedelta(days=1))
    tree = cup.gametree()
    
    print("\nGameTree Structure:")
    print(json.dumps(tree, indent=2))
    
    print("\n--- VALIDATION ---")
    print(f"Rounds: {list(tree.keys())}")
    
    # 4 teams: Semi-Final + Final
    assert "Semi-Final" in tree, "❌ Semi-Final missing!"
    assert "Final" in tree, "❌ Final missing!"
    assert "Quarter-Final" not in tree, "❌ QF shouldn't exist (only 4 teams)!"
    
    assert len(tree['Semi-Final']) == 2, "❌ Should have 2 SF games!"
    assert len(tree['Final']) == 1, "❌ Should have 1 Final game!"
    
    print("\n✅ Test 2 PASSED!")
    return tree


def test_elimination_with_bye():
    """Test 3: Odd number of teams (5 teams) - BYE test"""
    
    print("\n" + "="*60)
    print("TEST 3: 5 TEAMS ELIMINATION (with BYE)")
    print("="*60)
    
    teams = [Team(f"Team {i}") for i in range(1, 6)]
    cup = Cup(teams, CupType.ELIMINATION, interval=timedelta(days=1))
    tree = cup.gametree()
    
    print("\nGameTree Structure:")
    print(json.dumps(tree, indent=2))
    
    print("\n--- VALIDATION ---")
    
    # 5 teams: 2 games first round (1 team gets bye), then 3-team second round
    first_round_name = list(tree.keys())[0]
    first_round_games = len(tree[first_round_name])
    print(f"First round ({first_round_name}) games: {first_round_games}")
    
    # With BYE, first round should have 2 games (5 teams → 4 play, 1 waits)
    assert first_round_games == 2, f"❌ 5 teams should have 2 first round games, found: {first_round_games}"
    
    print("\n✅ Test 3 PASSED!")
    return tree


def test_group_gametree():
    """Test 4: 16 teams GROUP tournament"""
    
    print("\n" + "="*60)
    print("TEST 4: 16 TEAMS GROUP TOURNAMENT")
    print("="*60)
    
    teams = [Team(f"Team {i}") for i in range(1, 17)]
    cup = Cup(
        teams, 
        CupType.GROUP, 
        interval=timedelta(days=1),
        num_groups=4,
        playoff_teams=8
    )
    
    tree = cup.gametree()
    
    print("\nGameTree Structure (truncated):")
    tree_str = json.dumps(tree, indent=2, default=str)
    print(tree_str[:800] + "...\n")
    
    print("--- VALIDATION ---")
    
    # Should have Groups and Playoffs
    assert "Groups" in tree, "❌ Groups missing!"
    assert "Playoffs" in tree, "❌ Playoffs missing!"
    
    # Should have 4 groups
    groups = tree["Groups"]
    print(f"Number of groups: {len(groups)}")
    assert len(groups) == 4, f"❌ Should have 4 groups, found: {len(groups)}"
    
    # Each group should have 6 games (4 teams → C(4,2) = 6)
    for group_name, games in groups.items():
        print(f"Group {group_name}: {len(games)} games")
        assert len(games) == 6, f"❌ Each group should have 6 games!"
    
    print("\n✅ Test 4 PASSED!")
    return tree


def test_played_games_gametree():
    """Test 5: GameTree after playing games"""
    
    print("\n" + "="*60)
    print("TEST 5: GAMETREE AFTER PLAYING GAMES")
    print("="*60)
    
    teams = [Team(f"Team {i}") for i in range(1, 5)]
    for team in teams:
        team.addplayer("Player1", 10)
    
    cup = Cup(teams, CupType.ELIMINATION, interval=timedelta(days=1))
    
    # Play first round
    print("\nPlaying first round (Semi-Finals)...")
    for game in cup.rounds[0]:
        game.start()
        game.score(10, game.home(), "Player1")
        game.score(5, game.away(), "Player1")
        game.end()
        print(f"  Game {game.id()}: {game.home().team_name} {game.home_score} - {game.away_score} {game.away().team_name}")
    
    # Get GameTree
    tree = cup.gametree()
    
    print("\nGameTree After Games:")
    print(json.dumps(tree, indent=2))
    
    # Check that games show ENDED state
    print("\n--- VALIDATION ---")
    sf_games = tree['Semi-Final']
    for game in sf_games:
        print(f"Game {game['game_id']}: State={game['state']}, Score={game['score']}")
        assert game['state'] == 'ENDED', f"❌ Game should be ENDED!"
        assert game['score'] is not None, f"❌ Game should have score!"
    
    # Final should still have placeholder (not played yet)
    final_game = tree['Final'][0]
    print(f"\nFinal matchup: {final_game['home']} vs {final_game['away']}")
    
    # At least one should be placeholder
    has_placeholder = "Winner" in final_game['home'] or "Winner" in final_game['away']
    assert has_placeholder, "❌ Final should have placeholder (not played yet)!"
    
    print("\n✅ Test 5 PASSED!")
    return tree


def test_dynamic_placeholder_resolution():
    """Test 6: Dynamic placeholder resolution after games are played"""
    
    print("\n" + "="*60)
    print("TEST 6: DYNAMIC PLACEHOLDER RESOLUTION")
    print("="*60)
    
    teams = [Team(f"Team {i}") for i in range(1, 9)]
    for team in teams:
        team.addplayer("Star", 10)
    
    cup = Cup(teams, CupType.ELIMINATION, interval=timedelta(days=1))
    
    # BEFORE: GameTree before playing games
    print("\n--- BEFORE PLAYING GAMES ---")
    tree_before = cup.gametree()
    semi_before = tree_before['Semi-Final'][0]
    print(f"Semi-Final Game {semi_before['game_id']}: {semi_before['home']} vs {semi_before['away']}")
    assert "Winner" in semi_before['home'], "❌ Should have placeholder before games!"
    assert "Winner" in semi_before['away'], "❌ Should have placeholder before games!"
    
    # Play Quarter-Finals
    print("\n--- PLAYING QUARTER-FINALS ---")
    qf_winners = []
    for i, game in enumerate(cup.rounds[0], 1):
        game.start()
        # Home team always wins
        game.score(10, game.home(), "Star")
        game.score(5, game.away(), "Star")
        game.end()
        winner = game.home().team_name
        qf_winners.append(winner)
        print(f"  Game {game.id()}: {winner} WON ({game.home_score}-{game.away_score})")
    
    # AFTER: GameTree after playing games
    print("\n--- AFTER PLAYING QUARTER-FINALS ---")
    tree_after = cup.gametree()
    
    # Semi-Final should now show real team names
    print("\nSemi-Final matchups (should show real teams now):")
    for sf_game in tree_after['Semi-Final']:
        print(f"  Game {sf_game['game_id']}: {sf_game['home']} vs {sf_game['away']}")
        
        # Should NOT have "Winner" placeholder anymore
        has_placeholder = "Winner" in sf_game['home'] or "Winner" in sf_game['away']
        assert not has_placeholder, \
            f"❌ Semi-Final should show real teams, not placeholders! Got: {sf_game['home']} vs {sf_game['away']}"
        
        # Should be one of the QF winners
        assert sf_game['home'] in qf_winners, f"❌ {sf_game['home']} should be a QF winner!"
        assert sf_game['away'] in qf_winners, f"❌ {sf_game['away']} should be a QF winner!"
    
    # Final should still have placeholders (Semi-Finals not played)
    final_game = tree_after['Final'][0]
    print(f"\nFinal Game {final_game['game_id']}: {final_game['home']} vs {final_game['away']}")
    assert "Winner" in final_game['home'], "❌ Final should still have placeholder!"
    assert "Winner" in final_game['away'], "❌ Final should still have placeholder!"
    
    # Check score information
    print("\n--- CHECKING GAME DETAILS ---")
    for qf_game in tree_after['Quarter-Final']:
        print(f"Game {qf_game['game_id']}: {qf_game['home']} vs {qf_game['away']}")
        print(f"  State: {qf_game['state']}")
        print(f"  Score: {qf_game['score']}")
        
        assert qf_game['state'] == 'ENDED', "❌ QF games should be ENDED!"
        assert qf_game['score'] is not None, "❌ QF games should have scores!"
        assert qf_game['score']['home'] == 10, "❌ Home score should be 10!"
        assert qf_game['score']['away'] == 5, "❌ Away score should be 5!"
    
    print("\n✅ Test 6 PASSED! ✅")
    print("   → Placeholders correctly resolved to real team names")
    print("   → Game states tracked correctly")
    print("   → Scores displayed properly")
    return tree_after


def test_complete_tournament():
    """Test 7: Complete tournament from start to finish"""
    
    print("\n" + "="*60)
    print("TEST 7: COMPLETE TOURNAMENT SIMULATION")
    print("="*60)
    
    teams = [Team(f"Team {i}") for i in range(1, 5)]
    for team in teams:
        team.addplayer("Star", 10)
    
    cup = Cup(teams, CupType.ELIMINATION, interval=timedelta(days=1))
    
    print(f"\nTournament: {len(teams)} teams, {len(cup.rounds)} rounds")
    
    # Play all rounds
    for round_num, round_games in enumerate(cup.rounds, 1):
        round_name = list(cup.gametree().keys())[round_num - 1]
        print(f"\n--- ROUND {round_num}: {round_name} ---")
        
        for game in round_games:
            game.start()
            game.score(10, game.home(), "Star")
            game.score(5, game.away(), "Star")
            game.end()
            winner = game.home().team_name
            print(f"  Game {game.id()}: {winner} defeats {game.away().team_name} (10-5)")
    
    # Final GameTree
    print("\n--- FINAL GAMETREE ---")
    final_tree = cup.gametree()
    print(json.dumps(final_tree, indent=2))
    
    # All games should be ENDED
    print("\n--- VALIDATION ---")
    for round_name, games in final_tree.items():
        for game in games:
            assert game['state'] == 'ENDED', f"❌ All games should be ENDED!"
            assert game['score'] is not None, f"❌ All games should have scores!"
            # No placeholders should remain
            assert "Winner" not in game['home'], f"❌ No placeholders should remain: {game['home']}"
            assert "Winner" not in game['away'], f"❌ No placeholders should remain: {game['away']}"
            print(f"  {game['home']} vs {game['away']}: ✅")
    
    print("\n✅ Test 7 PASSED!")
    print("   → Complete tournament played successfully")
    print("   → All placeholders resolved")
    print("   → Champion determined!")
    return final_tree


def test_group_with_playoffs():
    """Test 8: GROUP tournament with playoff generation"""
    
    print("\n" + "="*60)
    print("TEST 8: GROUP TOURNAMENT WITH PLAYOFFS")
    print("="*60)
    
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
    
    # Play all group games
    print("\n--- PLAYING GROUP STAGE ---")
    for group_name, group_games in cup.group_games.items():
        print(f"\nGroup {group_name}:")
        for game in group_games:
            game.start()
            game.score(3, game.home(), "Star")
            game.score(1, game.away(), "Star")
            game.end()
        print(f"  {len(group_games)} games completed")
    
    # Generate playoffs
    print("\n--- GENERATING PLAYOFFS ---")
    cup.generate_playoffs()
    
    # Get GameTree with playoffs
    tree = cup.gametree()
    
    print("\n--- GAMETREE AFTER PLAYOFFS ---")
    print(f"Groups: {len(tree['Groups'])} groups")
    print(f"Playoffs: {tree['Playoffs']}")
    
    # Playoffs should have games
    assert len(tree['Playoffs']) > 0, "❌ Playoffs should have games!"
    
    # Get first playoff round
    first_playoff_round = list(tree['Playoffs'].values())[0]
    print(f"\nFirst playoff round: {len(first_playoff_round)} games")
    
    for game in first_playoff_round:
        print(f"  Game {game['game_id']}: {game['home']} vs {game['away']}")
        # Teams should be real (from group stage)
        assert not game['home'].startswith("Winner"), \
            f"❌ Playoff teams should be real: {game['home']}"
        assert not game['away'].startswith("Winner"), \
            f"❌ Playoff teams should be real: {game['away']}"
    
    print("\n✅ Test 8 PASSED!")
    return tree


# ============================================================================
# MAIN TEST RUNNER
# ============================================================================

if __name__ == "__main__":
    print("\n" + "🏆" * 30)
    print(" " * 20 + "GAMETREE TEST SUITE")
    print("🏆" * 30)
    
    passed = 0
    failed = 0
    errors = []
    
    tests = [
        ("8 Teams Elimination", test_elimination_8_teams),
        ("4 Teams Elimination", test_elimination_4_teams),
        ("5 Teams with BYE", test_elimination_with_bye),
        ("Group Tournament", test_group_gametree),
        ("Played Games", test_played_games_gametree),
        ("Dynamic Placeholders", test_dynamic_placeholder_resolution),
        ("Complete Tournament", test_complete_tournament),
        ("Group with Playoffs", test_group_with_playoffs),
    ]
    
    for test_name, test_func in tests:
        try:
            test_func()
            passed += 1
        except AssertionError as e:
            failed += 1
            errors.append((test_name, str(e)))
            print(f"\n❌ TEST FAILED: {test_name}")
            print(f"   Reason: {e}")
        except Exception as e:
            failed += 1
            errors.append((test_name, f"ERROR: {str(e)}"))
            print(f"\n💥 ERROR in {test_name}: {e}")
            import traceback
            traceback.print_exc()
    
    # Final Summary
    print("\n" + "="*60)
    print("📊 TEST SUMMARY")
    print("="*60)
    print(f"✅ Passed: {passed}/{len(tests)}")
    print(f"❌ Failed: {failed}/{len(tests)}")
    
    if errors:
        print("\n--- FAILED TESTS ---")
        for test_name, error in errors:
            print(f"  • {test_name}: {error}")
    
    if failed == 0:
        print("\n" + "🎉" * 30)
        print(" " * 15 + "ALL TESTS PASSED!")
        print("🎉" * 30)
    else:
        print("\n" + "⚠️ " * 30)
        print(" " * 10 + f"{failed} TEST(S) NEED ATTENTION")
        print("⚠️ " * 30)
    
    print()