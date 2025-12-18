"""
Test: GameTree dynamic update after each game.
Verifies that gametree() shows updated team names as games are played.
"""

from datetime import datetime, timedelta
from sports_lib.team import Team
from sports_lib.cup import Cup, CupType
import random


def test_gametree_dynamic_updates():
    """Test that gametree updates as games are played."""
    
    print("\n" + "="*70)
    print("TEST: GAMETREE DYNAMIC UPDATES")
    print("="*70)
    
    random.seed(5000)
    
    # Create 8 teams for quick test
    teams = [Team(f"Team {chr(65+i)}") for i in range(8)]
    for team in teams:
        team.addplayer("Star", 10)
    
    # Create elimination tournament
    cup = Cup(teams, CupType.ELIMINATION, interval=timedelta(days=1))
    
    print(f"\nTournament: {len(teams)} teams")
    print(f"Rounds: {len(cup.rounds)}")
    
    # ========================================================================
    # STEP 1: Before any games - Check initial gametree
    # ========================================================================
    
    print("\n--- STEP 1: Initial GameTree (Before Any Games) ---")
    tree_initial = cup.gametree()
    
    qf = tree_initial["Quarter-Final"]
    sf = tree_initial["Semi-Final"]
    final = tree_initial["Final"]
    
    print("\nQuarter-Finals:")
    for i, game in enumerate(qf, 1):
        print(f"  QF{i}: {game['home']:<12} vs {game['away']:<12} [{game['state']}]")
    
    print("\nSemi-Finals (Before QF):")
    for i, game in enumerate(sf, 1):
        has_placeholder = "Winner" in game['home'] or "Winner" in game['away']
        print(f"  SF{i}: {game['home']:<20} vs {game['away']:<20} [Placeholder: {has_placeholder}]")
    
    assert all("Winner" in g['home'] or "Winner" in g['away'] for g in sf), \
        "❌ SF should have placeholders before QF!"
    print("✅ SF has placeholders before QF is played")
    
    # ========================================================================
    # STEP 2: Play ONE QF game - Check if gametree updates
    # ========================================================================
    
    print("\n--- STEP 2: Play ONE Quarter-Final ---")
    
    first_qf = cup.rounds[0][0]
    first_qf.start()
    first_qf.score(3, first_qf.home(), "Star")
    first_qf.score(1, first_qf.away(), "Star")
    first_qf.end()
    
    winner_qf1 = first_qf.home().team_name
    print(f"  QF1 Result: {first_qf.home().team_name} 3-1 {first_qf.away().team_name} → {winner_qf1}")
    
    # Get gametree AFTER first QF
    tree_after_qf1 = cup.gametree()
    sf_after_qf1 = tree_after_qf1["Semi-Final"][0]
    
    print(f"\nSemi-Final 1 (After QF1 played):")
    print(f"  Home: {sf_after_qf1['home']:<20} [Should be: {winner_qf1}]")
    print(f"  Away: {sf_after_qf1['away']:<20} [Should be: Winner of Game 2]")
    
    # Check if SF1 home is now the real winner (not placeholder)
    assert sf_after_qf1['home'] == winner_qf1, \
        f"❌ SF1 home should be {winner_qf1}, got {sf_after_qf1['home']}"
    print(f"✅ SF1 home correctly updated to {winner_qf1}")
    
    assert "Winner" in sf_after_qf1['away'], \
        "❌ SF1 away should still be placeholder (QF2 not played)"
    print(f"✅ SF1 away still placeholder (QF2 not played yet)")
    
    # ========================================================================
    # STEP 3: Play ALL QF games - Check if ALL SF placeholders resolve
    # ========================================================================
    
    print("\n--- STEP 3: Play Remaining Quarter-Finals ---")
    
    qf_winners = [winner_qf1]  # Already have first winner
    
    for i, game in enumerate(cup.rounds[0][1:], 2):  # Start from QF2
        game.start()
        game.score(4, game.home(), "Star")
        game.score(2, game.away(), "Star")
        game.end()
        
        winner = game.home().team_name
        qf_winners.append(winner)
        print(f"  QF{i}: {game.home().team_name} 4-2 {game.away().team_name} → {winner}")
    
    # Get gametree AFTER all QF
    tree_after_all_qf = cup.gametree()
    sf_after_all = tree_after_all_qf["Semi-Final"]
    
    print("\nSemi-Finals (After ALL QF played):")
    for i, game in enumerate(sf_after_all, 1):
        print(f"  SF{i}: {game['home']:<12} vs {game['away']:<12}")
        
        # Should NOT have any placeholders now
        has_placeholder = "Winner" in game['home'] or "Winner" in game['away']
        assert not has_placeholder, \
            f"❌ SF{i} should not have placeholders after all QF played!"
    
    print("✅ All SF games now show real team names!")
    
    # ========================================================================
    # STEP 4: Play SF - Check if Final updates
    # ========================================================================
    
    print("\n--- STEP 4: Play Semi-Finals ---")
    
    sf_winners = []
    for i, game in enumerate(cup.rounds[1], 1):
        game.start()
        game.score(5, game.home(), "Star")
        game.score(3, game.away(), "Star")
        game.end()
        
        tree_current = cup.gametree()
        sf_game = tree_current["Semi-Final"][i-1]
        winner = sf_game['home']  # Home won (5-3)
        sf_winners.append(winner)
        
        print(f"  SF{i}: {sf_game['home']} 5-3 {sf_game['away']} → {winner}")
    
    # Get gametree AFTER all SF
    tree_after_sf = cup.gametree()
    final_after_sf = tree_after_sf["Final"][0]
    
    print("\nFinal (After SF played):")
    print(f"  {final_after_sf['home']} vs {final_after_sf['away']}")
    
    # Should NOT have placeholders
    has_placeholder = "Winner" in final_after_sf['home'] or "Winner" in final_after_sf['away']
    assert not has_placeholder, "❌ Final should not have placeholders after SF!"
    
    print("✅ Final now shows real team names!")
    
    # ========================================================================
    # STEP 5: Play Final - Verify complete tournament
    # ========================================================================
    
    print("\n--- STEP 5: Play Final ---")
    
    final_game = cup.rounds[2][0]
    final_game.start()
    final_game.score(7, final_game.home(), "Star")
    final_game.score(4, final_game.away(), "Star")
    final_game.end()
    
    tree_final = cup.gametree()
    final_result = tree_final["Final"][0]
    
    champion = final_result['home']
    runner_up = final_result['away']
    
    print(f"  {champion} 7-4 {runner_up}")
    print(f"\n🏆 CHAMPION: {champion}")
    
    # Final validation
    print("\n--- FINAL VALIDATION ---")
    
    total_placeholders = 0
    for round_name, games in tree_final.items():
        for game in games:
            if "Winner" in game['home'] or "Winner" in game['away']:
                total_placeholders += 1
    
    assert total_placeholders == 0, f"❌ Found {total_placeholders} placeholders!"
    print(f"✅ Zero placeholders in final gametree")
    
    print("\n" + "="*70)
    print("✅ TEST PASSED: GameTree updates dynamically after each game!")
    print("="*70)


if __name__ == "__main__":
    test_gametree_dynamic_updates()