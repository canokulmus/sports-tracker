"""
Complete test suite for ELIMINATION tournament type.
Tests bracket generation, placeholder resolution, and winner progression.
"""

from datetime import datetime, timedelta
from sports_lib.team import Team
from sports_lib.cup import Cup, CupType
from sports_lib.constants import GameState
import json


def test_elimination_4_teams():
    """Test 1: Basic 4-team elimination (Semi + Final)"""
    
    print("\n" + "="*60)
    print("TEST 1: 4 TEAMS ELIMINATION")
    print("="*60)
    
    teams = [Team(f"Team {i}") for i in range(1, 5)]
    for team in teams:
        team.addplayer("Star", 10)
    
    cup = Cup(teams, CupType.ELIMINATION, interval=timedelta(days=1))
    
    print(f"\nTournament: {len(teams)} teams")
    print(f"Rounds: {len(cup.rounds)}")
    print(f"Total games: {len(cup.games)}")
    
    # Should have 2 rounds (Semi + Final)
    assert len(cup.rounds) == 2, f"❌ Should have 2 rounds!"
    assert len(cup.games) == 3, f"❌ Should have 3 games total (2 SF + 1 F)!"
    
    # Get gametree
    tree = cup.gametree()
    print("\n--- INITIAL BRACKET ---")
    print(json.dumps(tree, indent=2))
    
    # Validate structure
    assert "Semi-Final" in tree, "❌ Missing Semi-Final!"
    assert "Final" in tree, "❌ Missing Final!"
    assert len(tree["Semi-Final"]) == 2, "❌ Should have 2 SF games!"
    assert len(tree["Final"]) == 1, "❌ Should have 1 Final game!"
    
    # Semi-Finals should have real teams
    for game in tree["Semi-Final"]:
        assert not game["home"].startswith("Winner"), "❌ SF should have real teams!"
        assert not game["away"].startswith("Winner"), "❌ SF should have real teams!"
    
    # Final should have placeholders
    final = tree["Final"][0]
    assert "Winner" in final["home"], "❌ Final should have placeholders!"
    assert "Winner" in final["away"], "❌ Final should have placeholders!"
    
    print("\n✅ Test 1 PASSED!")


def test_elimination_play_semifinals():
    """Test 2: Play semi-finals and check placeholder resolution"""
    
    print("\n" + "="*60)
    print("TEST 2: PLAY SEMI-FINALS (Placeholder Resolution)")
    print("="*60)
    
    teams = [Team(f"Team {i}") for i in range(1, 5)]
    for team in teams:
        team.addplayer("Star", 10)
    
    cup = Cup(teams, CupType.ELIMINATION, interval=timedelta(days=1))
    
    print("\n--- BEFORE PLAYING ---")
    tree_before = cup.gametree()
    final_before = tree_before["Final"][0]
    print(f"Final: {final_before['home']} vs {final_before['away']}")
    
    # Play semi-finals
    print("\n--- PLAYING SEMI-FINALS ---")
    sf_winners = []
    for game in cup.rounds[0]:
        game.start()
        game.score(10, game.home(), "Star")
        game.score(5, game.away(), "Star")
        game.end()
        
        winner = game.home().team_name
        sf_winners.append(winner)
        print(f"  Game {game.id()}: {winner} defeats {game.away().team_name}")
    
    # Check gametree after semi-finals
    print("\n--- AFTER SEMI-FINALS ---")
    tree_after = cup.gametree()
    final_after = tree_after["Final"][0]
    print(f"Final: {final_after['home']} vs {final_after['away']}")
    
    # Final should now show real teams
    assert final_after['home'] in sf_winners, \
        f"❌ Final should show SF winner! Got: {final_after['home']}"
    assert final_after['away'] in sf_winners, \
        f"❌ Final should show SF winner! Got: {final_after['away']}"
    
    # No placeholders should remain
    assert "Winner" not in final_after['home'], "❌ Placeholder should be resolved!"
    assert "Winner" not in final_after['away'], "❌ Placeholder should be resolved!"
    
    print("\n✅ Test 2 PASSED!")


def test_elimination_complete_tournament():
    """Test 3: Complete tournament from start to finish"""
    
    print("\n" + "="*60)
    print("TEST 3: COMPLETE TOURNAMENT")
    print("="*60)
    
    teams = [Team(f"Team {i}") for i in range(1, 5)]
    for team in teams:
        team.addplayer("Star", 10)
    
    cup = Cup(teams, CupType.ELIMINATION, interval=timedelta(days=1))
    
    # Play all rounds
    print("\n--- PLAYING ALL ROUNDS ---")
    for round_num, round_games in enumerate(cup.rounds, 1):
        round_name = list(cup.gametree().keys())[round_num - 1]
        print(f"\n{round_name}:")
        
        for game in round_games:
            game.start()
            game.score(10, game.home(), "Star")
            game.score(5, game.away(), "Star")
            game.end()
            
            winner = game.home().team_name
            loser = game.away().team_name
            print(f"  {winner} defeats {loser} (10-5)")
    
    # Final gametree
    print("\n--- FINAL GAMETREE ---")
    final_tree = cup.gametree()
    
    # All games should be ENDED
    all_ended = True
    for round_name, games in final_tree.items():
        for game in games:
            if game['state'] != 'ENDED':
                all_ended = False
            print(f"{round_name} Game {game['game_id']}: {game['home']} vs {game['away']} [{game['state']}]")
    
    assert all_ended, "❌ All games should be ENDED!"
    
    # No placeholders should remain
    for round_name, games in final_tree.items():
        for game in games:
            assert "Winner" not in game['home'], f"❌ No placeholders should remain!"
            assert "Winner" not in game['away'], f"❌ No placeholders should remain!"
    
    # Check standings
    print("\n--- STANDINGS ---")
    standings = cup.standings()
    print(json.dumps(standings, indent=2))
    
    print("\n✅ Test 3 PASSED!")
    print("   → Champion determined!")


def test_elimination_8_teams():
    """Test 4: 8-team elimination (QF + SF + F)"""
    
    print("\n" + "="*60)
    print("TEST 4: 8 TEAMS ELIMINATION")
    print("="*60)
    
    teams = [Team(f"Team {i}") for i in range(1, 9)]
    for team in teams:
        team.addplayer("Star", 10)
    
    cup = Cup(teams, CupType.ELIMINATION, interval=timedelta(days=1))
    
    print(f"\nTournament: {len(teams)} teams")
    print(f"Rounds: {len(cup.rounds)}")
    print(f"Total games: {len(cup.games)}")
    
    # 8 teams: QF (4) + SF (2) + F (1) = 7 games
    assert len(cup.rounds) == 3, "❌ Should have 3 rounds!"
    assert len(cup.games) == 7, "❌ Should have 7 games!"
    
    tree = cup.gametree()
    
    assert "Quarter-Final" in tree, "❌ Missing Quarter-Final!"
    assert "Semi-Final" in tree, "❌ Missing Semi-Final!"
    assert "Final" in tree, "❌ Missing Final!"
    
    assert len(tree["Quarter-Final"]) == 4, "❌ QF should have 4 games!"
    assert len(tree["Semi-Final"]) == 2, "❌ SF should have 2 games!"
    assert len(tree["Final"]) == 1, "❌ Final should have 1 game!"
    
    # Play Quarter-Finals
    print("\n--- PLAYING QUARTER-FINALS ---")
    qf_winners = []
    for game in cup.rounds[0]:
        game.start()
        game.score(10, game.home(), "Star")
        game.score(5, game.away(), "Star")
        game.end()
        qf_winners.append(game.home().team_name)
    
    # Check Semi-Finals after QF
    tree_after_qf = cup.gametree()
    print("\n--- SEMI-FINALS (after QF) ---")
    for sf_game in tree_after_qf["Semi-Final"]:
        print(f"  {sf_game['home']} vs {sf_game['away']}")
        
        # Should show real teams now
        assert sf_game['home'] in qf_winners, \
            f"❌ SF should show QF winner! Got: {sf_game['home']}"
        assert sf_game['away'] in qf_winners, \
            f"❌ SF should show QF winner! Got: {sf_game['away']}"
    
    print("\n✅ Test 4 PASSED!")


def test_elimination_5_teams_bye():
    """Test 5: 5 teams with BYE"""
    
    print("\n" + "="*60)
    print("TEST 5: 5 TEAMS WITH BYE")
    print("="*60)
    
    teams = [Team(f"Team {i}") for i in range(1, 6)]
    cup = Cup(teams, CupType.ELIMINATION, interval=timedelta(days=1))
    
    print(f"\nTournament: {len(teams)} teams")
    print(f"Rounds: {len(cup.rounds)}")
    print(f"Total games: {len(cup.games)}")
    
    tree = cup.gametree()
    
    # Check first round
    first_round_name = list(tree.keys())[0]
    first_round_games = tree[first_round_name]
    
    print(f"\nFirst round ({first_round_name}): {len(first_round_games)} games")
    
    # With 5 teams and BYE, first round should have 2 games (4 play, 1 waits)
    assert len(first_round_games) == 2, \
        f"❌ 5 teams should have 2 first-round games!"
    
    print("\n✅ Test 5 PASSED!")


# ============================================================================
# MAIN TEST RUNNER
# ============================================================================

if __name__ == "__main__":
    print("\n" + "🏆" * 30)
    print(" " * 12 + "ELIMINATION TEST SUITE")
    print(" " * 12 + "(Phase 3 - REST API)")
    print("🏆" * 30)
    
    tests = [
        test_elimination_4_teams,
        test_elimination_play_semifinals,
        test_elimination_complete_tournament,
        test_elimination_8_teams,
        test_elimination_5_teams_bye,
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
    print("📊 ELIMINATION TEST SUMMARY")
    print("="*60)
    print(f"✅ Passed: {passed}/{len(tests)}")
    print(f"❌ Failed: {failed}/{len(tests)}")
    
    if failed == 0:
        print("\n🎉 ALL ELIMINATION TESTS PASSED! 🎉")
    
    print()