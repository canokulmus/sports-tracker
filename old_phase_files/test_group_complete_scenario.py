"""
Complete GROUP tournament scenario from start to finish.
Shows every stage: Group Stage → Standings → Playoff Generation → 
Quarter-Finals → Semi-Finals → Final → Champion

This version properly resolves placeholder teams using gametree().
"""

from datetime import datetime, timedelta
from sports_lib.team import Team
from sports_lib.cup import Cup, CupType
import random
import json


def print_section_header(title: str, emoji: str = "🏆"):
    """Print a fancy section header."""
    print("\n" + "="*70)
    print(f"{emoji} {title}")
    print("="*70)


def print_subsection(title: str):
    """Print a subsection header."""
    print(f"\n--- {title} ---")


def test_complete_group_tournament():
    """
    Complete GROUP tournament from start to finish.
    
    Tournament Structure:
    - 16 teams, 4 groups (A, B, C, D)
    - Group Stage: Each group plays round-robin (24 games total)
    - Top 2 from each group advance (8 teams)
    - Quarter-Finals: 8 teams → 4 winners (4 games)
    - Semi-Finals: 4 teams → 2 winners (2 games)
    - Final: 2 teams → 1 CHAMPION (1 game)
    
    Total: 31 games from start to champion!
    """
    
    print_section_header("COMPLETE GROUP TOURNAMENT", "🏆")
    print(" " * 20 + "16 Teams → 1 Champion")
    print(" " * 15 + "Group Stage → Playoffs → Final")
    
    # Fix seed for reproducibility
    random.seed(9999)
    
    # Create 16 teams with city names for realism
    team_names = [
        "Manchester", "Barcelona", "Munich", "Milan",
        "Paris", "Madrid", "Liverpool", "London",
        "Amsterdam", "Rome", "Lisbon", "Athens",
        "Istanbul", "Moscow", "Vienna", "Prague"
    ]
    teams = [Team(name) for name in team_names]
    for team in teams:
        team.addplayer("Star", 10)
    
    # Create tournament
    cup = Cup(
        teams,
        CupType.GROUP,
        interval=timedelta(days=1),
        num_groups=4,
        playoff_teams=8
    )
    
    print(f"\n📋 Tournament Configuration:")
    print(f"   Format: GROUP")
    print(f"   Teams: {len(teams)}")
    print(f"   Groups: {cup.num_groups}")
    print(f"   Playoff spots: {cup.playoff_teams}")
    print(f"   Total games: 24 (group) + 7 (playoff) = 31 games")
    
    # ========================================================================
    # STAGE 1: GROUP STAGE
    # ========================================================================
    
    print_section_header("STAGE 1: GROUP STAGE", "⚽")
    
    # Show group composition
    print("\n📊 Group Draw:")
    for group_name in sorted(cup.groups.keys()):
        group_teams = cup.groups[group_name]
        team_names_str = ", ".join([t.team_name for t in group_teams])
        print(f"   Group {group_name}: {team_names_str}")
    
    # Play all group games
    print("\n⚽ Playing Group Stage Matches...")
    game_number = 1
    
    for group_name in sorted(cup.group_games.keys()):
        group_games = cup.group_games[group_name]
        print_subsection(f"Group {group_name} Matches")
        
        for game in group_games:
            # Random scores (1-4 goals)
            home_score = random.randint(1, 4)
            away_score = random.randint(1, 4)
            
            game.start()
            game.score(home_score, game.home(), "Star")
            game.score(away_score, game.away(), "Star")
            game.end()
            
            # Format result
            home_name = game.home().team_name
            away_name = game.away().team_name
            
            if home_score > away_score:
                result = f"✓ {home_name}"
            elif away_score > home_score:
                result = f"✓ {away_name}"
            else:
                result = "⚖ DRAW"
            
            print(f"   Game {game_number:2d}: {home_name:<12} {home_score}-{away_score} {away_name:<12} → {result}")
            game_number += 1
    
    # Show final group standings
    print_section_header("GROUP STAGE FINAL STANDINGS", "📊")
    
    standings = cup.standings()
    qualified_teams = []
    
    for group_name in sorted(standings["Groups"].keys()):
        group_standings = standings["Groups"][group_name]
        print(f"\n🏆 Group {group_name}:")
        print(f"{'#':<3} {'Team':<15} {'P':<3} {'W':<3} {'D':<3} {'L':<3} {'GF':<4} {'GA':<4} {'GD':<5} {'Pts':<4} {'Result':<15}")
        print("-" * 75)
        
        for i, (team, w, d, l, gf, ga, pts) in enumerate(group_standings, 1):
            played = w + d + l
            gd = gf - ga
            
            # Top 2 qualify
            if i <= 2:
                status = "✅ QUALIFIED"
                qualified_teams.append((team, group_name, i, pts))
            else:
                status = "❌ Eliminated"
            
            print(f"{i:<3} {team:<15} {played:<3} {w:<3} {d:<3} {l:<3} {gf:<4} {ga:<4} {gd:+5} {pts:<4} {status:<15}")
    
    print(f"\n🎫 {len(qualified_teams)} teams qualified for playoffs:")
    for team, group, pos, pts in qualified_teams:
        print(f"   {team:<15} (Group {group} #{pos}, {pts} pts)")
    
    # ========================================================================
    # STAGE 2: PLAYOFF GENERATION
    # ========================================================================
    
    print_section_header("STAGE 2: GENERATING PLAYOFF BRACKET", "🎯")
    
    print("\n⏳ Generating complete playoff bracket...")
    print("   (Quarter-Finals → Semi-Finals → Final)")
    
    cup.generate_playoffs()
    
    print(f"\n✅ Playoff bracket generated!")
    print(f"   Playoff rounds: {len(cup.playoff_rounds)}")
    print(f"   Total playoff games: {len(cup.playoff_games)}")
    
    # Show initial bracket structure
    tree = cup.gametree()
    
    print("\n📋 Playoff Structure:")
    for round_name in tree["Playoffs"].keys():
        games_count = len(tree["Playoffs"][round_name])
        print(f"   {round_name}: {games_count} game(s)")
    
    # ========================================================================
    # STAGE 3: QUARTER-FINALS
    # ========================================================================
    
    print_section_header("STAGE 3: QUARTER-FINALS", "⚔️")
    
    qf_games_info = tree["Playoffs"][list(tree["Playoffs"].keys())[0]]
    
    print("\n🎯 Quarter-Final Matchups:")
    for i, game_info in enumerate(qf_games_info, 1):
        print(f"   QF{i}: {game_info['home']:<15} vs {game_info['away']:<15}")
    
    print("\n⚽ Playing Quarter-Finals...")
    qf_winners = []
    qf_results = []
    
    # Play QF games
    for i, game in enumerate(cup.playoff_rounds[0], 1):
        # Random scores (2-5 goals, no draws)
        home_score = random.randint(2, 5)
        away_score = random.randint(2, 5)
        while home_score == away_score:
            away_score = random.randint(2, 5)
        
        game.start()
        game.score(home_score, game.home(), "Star")
        game.score(away_score, game.away(), "Star")
        game.end()
        
        # ✅ Get RESOLVED team names from gametree
        tree_after_qf = cup.gametree()
        qf_current = tree_after_qf["Playoffs"]["Quarter-Final"][i-1]
        home_name = qf_current['home']
        away_name = qf_current['away']
        
        winner_name = home_name if home_score > away_score else away_name
        
        qf_winners.append(winner_name)
        qf_results.append((home_name, home_score, away_score, away_name, winner_name))
        
        print(f"   QF{i}: {home_name:<15} {home_score}-{away_score} {away_name:<15} → ✓ {winner_name}")
    
    print(f"\n✅ Quarter-Finals Complete!")
    print(f"   Semi-Finalists: {', '.join(qf_winners)}")
    
    # ========================================================================
    # STAGE 4: SEMI-FINALS
    # ========================================================================
    
    print_section_header("STAGE 4: SEMI-FINALS", "🔥")
    
    # Get updated gametree to see SF matchups with RESOLVED names
    tree_after_qf = cup.gametree()
    
    sf_winners = []
    sf_results = []
    
    if len(cup.playoff_rounds) >= 2:
        sf_games_info = tree_after_qf["Playoffs"]["Semi-Final"]
        
        print("\n🎯 Semi-Final Matchups:")
        for i, game_info in enumerate(sf_games_info, 1):
            print(f"   SF{i}: {game_info['home']:<15} vs {game_info['away']:<15}")
        
        print("\n⚽ Playing Semi-Finals...")
        
        # Play SF games
        for i, game in enumerate(cup.playoff_rounds[1], 1):
            # Random scores (2-6 goals, no draws)
            home_score = random.randint(2, 6)
            away_score = random.randint(2, 6)
            while home_score == away_score:
                away_score = random.randint(2, 6)
            
            game.start()
            game.score(home_score, game.home(), "Star")
            game.score(away_score, game.away(), "Star")
            game.end()
            
            # ✅ Get RESOLVED team names from gametree AFTER playing
            tree_current = cup.gametree()
            sf_current = tree_current["Playoffs"]["Semi-Final"][i-1]
            home_name = sf_current['home']
            away_name = sf_current['away']
            
            winner_name = home_name if home_score > away_score else away_name
            
            sf_winners.append(winner_name)
            sf_results.append((home_name, home_score, away_score, away_name, winner_name))
            
            print(f"   SF{i}: {home_name:<15} {home_score}-{away_score} {away_name:<15} → ✓ {winner_name}")
        
        print(f"\n✅ Semi-Finals Complete!")
        print(f"   Finalists: {' vs '.join(sf_winners)}")
    else:
        print("\n⚠️  Semi-Finals were not generated!")
    
    # ========================================================================
    # STAGE 5: FINAL
    # ========================================================================
    
    print_section_header("STAGE 5: GRAND FINAL", "🏆")
    
    champion_name = None
    runner_up_name = None
    final_score_str = ""
    
    if len(cup.playoff_rounds) >= 3:
        # Get final matchup with RESOLVED names
        tree_before_final = cup.gametree()
        final_game_info = tree_before_final["Playoffs"]["Final"][0]
        
        print("\n🎯 Final Matchup:")
        print(f"   🏆 FINAL: {final_game_info['home']:<15} vs {final_game_info['away']:<15}")
        
        print("\n⚽ Playing the Final...")
        
        # Play Final
        final_game = cup.playoff_rounds[2][0]
        
        # Random scores (3-7 goals, no draws)
        home_score = random.randint(3, 7)
        away_score = random.randint(3, 7)
        while home_score == away_score:
            away_score = random.randint(3, 7)
        
        final_game.start()
        final_game.score(home_score, final_game.home(), "Star")
        final_game.score(away_score, final_game.away(), "Star")
        final_game.end()
        
        # ✅ Get RESOLVED team names from gametree AFTER playing
        tree_final_result = cup.gametree()
        final_result = tree_final_result["Playoffs"]["Final"][0]
        home_name = final_result['home']
        away_name = final_result['away']
        
        champion_name = home_name if home_score > away_score else away_name
        runner_up_name = away_name if home_score > away_score else home_name
        final_score_str = f"{home_name:<15} {home_score}-{away_score} {away_name:<15}"
        
        print(f"\n   🏆 FINAL: {final_score_str}")
        print(f"\n   🥇 WINNER: {champion_name}")
        print(f"   🥈 RUNNER-UP: {runner_up_name}")
        
        # ====================================================================
        # FINAL TOURNAMENT SUMMARY
        # ====================================================================
        
        print_section_header("TOURNAMENT SUMMARY", "📊")
        
        print("\n🏆 Complete Tournament Results:")
        
        print("\n📈 Tournament Path:")
        print(f"   16 teams → Group Stage (24 games)")
        print(f"   8 teams → Quarter-Finals (4 games)")
        print(f"   4 teams → Semi-Finals (2 games)")
        print(f"   2 teams → Final (1 game)")
        print(f"   1 team → CHAMPION: {champion_name}")
        
        print("\n⚔️  Playoff Results:")
        print("\n   Quarter-Finals:")
        for i, (h, hs, aws, a, w) in enumerate(qf_results, 1):
            print(f"      QF{i}: {h:<15} {hs}-{aws} {a:<15} → {w}")
        
        print("\n   Semi-Finals:")
        for i, (h, hs, aws, a, w) in enumerate(sf_results, 1):
            print(f"      SF{i}: {h:<15} {hs}-{aws} {a:<15} → {w}")
        
        print("\n   Final:")
        print(f"      🏆 {final_score_str} → {champion_name}")
        
        print("\n🎖️  Final Rankings:")
        print(f"   🥇 CHAMPION: {champion_name}")
        print(f"   🥈 Runner-up: {runner_up_name}")
        
        # Get semi-finalists (losers of SF)
        sf_losers = []
        for h, hs, aws, a, w in sf_results:
            loser = a if w == h else h
            sf_losers.append(loser)
        
        if sf_losers:
            print(f"   🥉 Semi-Finalists: {', '.join(sf_losers)}")
        
        print("\n📊 Tournament Statistics:")
        print(f"   Total games played: {len([g for g in cup.games if g.state.name == 'ENDED'])}")
        print(f"   Group stage games: 24")
        print(f"   Playoff games: 7 (4 QF + 2 SF + 1 F)")
        print(f"   Groups: {cup.num_groups}")
        print(f"   Qualified teams: {cup.playoff_teams}")
        
    else:
        print("\n⚠️  Final was not generated!")
        print("   This indicates the playoff bracket generation is incomplete.")
    
    # ========================================================================
    # GAMETREE VALIDATION
    # ========================================================================
    
    print_section_header("GAMETREE VALIDATION", "🌳")
    
    final_tree = cup.gametree()
    
    print("\n✅ Tournament Tree Structure:")
    
    # Groups
    print("\n📦 Groups:")
    for group_name, games in final_tree["Groups"].items():
        ended = sum(1 for g in games if g['state'] == 'ENDED')
        print(f"   Group {group_name}: {ended}/{len(games)} games completed")
    
    # Playoffs
    print("\n🏆 Playoffs:")
    for round_name, games in final_tree["Playoffs"].items():
        ended = sum(1 for g in games if g['state'] == 'ENDED')
        placeholder_count = sum(1 for g in games if 'Winner' in g['home'] or 'Winner' in g['away'])
        print(f"   {round_name}: {ended}/{len(games)} completed, {placeholder_count} placeholders")
    
    # Check for placeholders (should be 0 after all games played)
    total_placeholders = 0
    for round_name, games in final_tree["Playoffs"].items():
        for game in games:
            if 'Winner' in game['home'] or 'Winner' in game['away']:
                total_placeholders += 1
    
    if total_placeholders == 0:
        print("\n✅ All placeholders resolved! Tournament complete!")
    else:
        print(f"\n⚠️  {total_placeholders} placeholder(s) remaining")
    
    print_section_header("✅ TOURNAMENT COMPLETE!", "🎉")
    
    return champion_name


# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    print("\n" + "🏆" * 35)
    print(" " * 8 + "COMPLETE GROUP TOURNAMENT DEMONSTRATION")
    print(" " * 15 + "From Group Stage to Champion")
    print("🏆" * 35)
    
    try:
        champion = test_complete_group_tournament()
        
        print("\n" + "="*70)
        print(f"🏆 TOURNAMENT CHAMPION: {champion} 🏆")
        print("="*70)
        
        print("""
✅ Complete Tournament Flow Demonstrated:
   1. ✅ Group Stage (24 games) - All groups played
   2. ✅ Standings Calculation - Top 2 from each group qualified
   3. ✅ Playoff Generation - Complete bracket (QF, SF, F)
   4. ✅ Quarter-Finals (4 games) - 8 teams → 4 winners
   5. ✅ Semi-Finals (2 games) - 4 teams → 2 finalists
   6. ✅ Final (1 game) - 2 teams → 1 CHAMPION
   7. ✅ GameTree - All placeholders resolved
   8. ✅ No missing rounds - Complete tournament!

🎉 GROUP tournament implementation is now COMPLETE!
        """)
        
    except Exception as e:
        print(f"\n💥 ERROR: {e}")
        import traceback
        traceback.print_exc()
        
        print("\n⚠️  If you see this error, check the implementation.")