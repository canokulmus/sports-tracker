"""
Test script for Round-Robin League Generation
Tests the new _generate_league() algorithm before integrating into cup.py
"""

from datetime import datetime, timedelta
from itertools import combinations
import copy


class DummyTeam:
    """Simple team class for testing."""
    def __init__(self, name):
        self.team_name = name
    
    def __str__(self):
        return self.team_name


def generate_league_OLD(teams):
    """OLD METHOD: Using combinations (creates sequential matches)."""
    print("=" * 60)
    print("OLD METHOD: combinations(teams, 2)")
    print("=" * 60)
    
    pairs = list(combinations(teams, 2))
    
    print(f"\nTotal matches: {len(pairs)}\n")
    
    for i, (home, away) in enumerate(pairs, 1):
        print(f"Match {i}: {home.team_name:<15} vs {away.team_name:<15}")
    
    print("\n❌ PROBLEM: Arsenal plays 3 matches in a row!")
    print()


def generate_league_NEW(teams):
    """NEW METHOD: Round-Robin scheduling (balanced rounds)."""
    print("=" * 60)
    print("NEW METHOD: Round-Robin Algorithm")
    print("=" * 60)
    
    teams_copy = copy.copy(teams)
    n = len(teams_copy)
    
    # If odd number of teams, add a "bye"
    if n % 2 == 1:
        teams_copy.append(None)
        n += 1
        print(f"\n⚠️  Odd number of teams detected. Adding BYE.\n")
    
    matches = []
    
    # Round-Robin algorithm: n-1 rounds for n teams
    for round_num in range(n - 1):
        round_matches = []
        
        # Create matches for this round
        for i in range(n // 2):
            home_idx = i
            away_idx = n - 1 - i
            
            home_team = teams_copy[home_idx]
            away_team = teams_copy[away_idx]
            
            # Skip if either team is None (bye)
            if home_team is None or away_team is None:
                if home_team:
                    round_matches.append((home_team, "BYE"))
                elif away_team:
                    round_matches.append((away_team, "BYE"))
                continue
            
            round_matches.append((home_team, away_team))
        
        matches.append(round_matches)
        
        # Rotate teams (keep first team fixed, rotate others)
        teams_copy = [teams_copy[0]] + [teams_copy[-1]] + teams_copy[1:-1]
    
    # Print results
    print(f"Total matches: {sum(len(r) for r in matches)}")
    print(f"Total rounds: {len(matches)}\n")
    
    match_num = 1
    for round_num, round_matches in enumerate(matches, 1):
        print(f"--- ROUND {round_num} ---")
        for home, away in round_matches:
            if away == "BYE":
                print(f"  Match {match_num}: {home.team_name:<15} (BYE - resting)")
            else:
                print(f"  Match {match_num}: {home.team_name:<15} vs {away.team_name:<15}")
            match_num += 1
        print()
    
    print("✅ SOLUTION: Each team plays once per round!")
    print()
    
    return matches


def test_4_teams():
    """Test with 4 teams (even number)."""
    print("\n" + "🏆" * 30)
    print("TEST 1: 4 TEAMS (Arsenal, Chelsea, Liverpool, ManCity)")
    print("🏆" * 30 + "\n")
    
    teams = [
        DummyTeam("Arsenal"),
        DummyTeam("Chelsea"),
        DummyTeam("Liverpool"),
        DummyTeam("ManCity")
    ]
    
    generate_league_OLD(teams)
    generate_league_NEW(teams)


def test_3_teams():
    """Test with 3 teams (odd number - bye week)."""
    print("\n" + "🏆" * 30)
    print("TEST 2: 3 TEAMS (Team A, Team B, Team C)")
    print("🏆" * 30 + "\n")
    
    teams = [
        DummyTeam("Team A"),
        DummyTeam("Team B"),
        DummyTeam("Team C")
    ]
    
    print("=" * 60)
    print("OLD METHOD: combinations(teams, 2)")
    print("=" * 60)
    pairs = list(combinations(teams, 2))
    print(f"\nTotal matches: {len(pairs)}\n")
    for i, (home, away) in enumerate(pairs, 1):
        print(f"Match {i}: {home.team_name:<10} vs {away.team_name:<10}")
    print()
    
    generate_league_NEW(teams)


def test_6_teams():
    """Test with 6 teams (larger tournament)."""
    print("\n" + "🏆" * 30)
    print("TEST 3: 6 TEAMS (T1, T2, T3, T4, T5, T6)")
    print("🏆" * 30 + "\n")
    
    teams = [
        DummyTeam("Team1"),
        DummyTeam("Team2"),
        DummyTeam("Team3"),
        DummyTeam("Team4"),
        DummyTeam("Team5"),
        DummyTeam("Team6")
    ]
    
    matches = generate_league_NEW(teams)
    
    # Verify each team plays once per round
    print("=" * 60)
    print("VERIFICATION: Checking if each team plays once per round")
    print("=" * 60)
    
    all_valid = True
    for round_num, round_matches in enumerate(matches, 1):
        teams_in_round = []
        for home, away in round_matches:
            if away != "BYE":
                teams_in_round.append(home.team_name)
                teams_in_round.append(away.team_name)
            else:
                teams_in_round.append(home.team_name)
        
        # Check for duplicates
        if len(teams_in_round) != len(set(teams_in_round)):
            print(f"❌ Round {round_num}: DUPLICATE TEAMS FOUND!")
            print(f"   Teams: {teams_in_round}")
            all_valid = False
        else:
            print(f"✅ Round {round_num}: All teams play at most once")
    
    print()
    if all_valid:
        print("🎉 ALL ROUNDS VALID! Algorithm works correctly!\n")
    else:
        print("⚠️  VALIDATION FAILED!\n")


def verify_all_matchups(teams, matches):
    """Verify that all possible matchups occur exactly once."""
    print("=" * 60)
    print("VERIFICATION: Checking if all matchups occur")
    print("=" * 60)
    
    # Generate all expected pairs
    expected_pairs = set()
    for i in range(len(teams)):
        for j in range(i + 1, len(teams)):
            pair = tuple(sorted([teams[i].team_name, teams[j].team_name]))
            expected_pairs.add(pair)
    
    # Collect actual pairs from matches
    actual_pairs = set()
    for round_matches in matches:
        for home, away in round_matches:
            if away != "BYE":
                pair = tuple(sorted([home.team_name, away.team_name]))
                actual_pairs.add(pair)
    
    missing = expected_pairs - actual_pairs
    extra = actual_pairs - expected_pairs
    
    print(f"\nExpected matchups: {len(expected_pairs)}")
    print(f"Actual matchups: {len(actual_pairs)}")
    
    if missing:
        print(f"\n❌ Missing matchups: {missing}")
    if extra:
        print(f"\n❌ Extra matchups: {extra}")
    
    if not missing and not extra:
        print("\n✅ All matchups occur exactly once!\n")
        return True
    else:
        print("\n❌ Matchup verification failed!\n")
        return False


def main():
    """Run all tests."""
    print("\n" + "=" * 60)
    print(" " * 15 + "ROUND-ROBIN TEST SUITE")
    print("=" * 60)
    
    # Test 1: 4 teams
    test_4_teams()
    
    # Test 2: 3 teams (odd number)
    test_3_teams()
    
    # Test 3: 6 teams (larger)
    test_6_teams()
    
    # Final verification for 4 teams
    print("\n" + "=" * 60)
    print("FINAL VERIFICATION: 4 Teams")
    print("=" * 60 + "\n")
    
    teams = [
        DummyTeam("Arsenal"),
        DummyTeam("Chelsea"),
        DummyTeam("Liverpool"),
        DummyTeam("ManCity")
    ]
    
    matches = generate_league_NEW(teams)
    verify_all_matchups(teams, matches)
    
    print("=" * 60)
    print(" " * 20 + "TEST COMPLETE")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    main()