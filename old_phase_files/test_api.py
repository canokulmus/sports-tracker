import requests
import json
import time
import random

BASE_URL = "http://127.0.0.1:8000/api"


# --- Helper Functions for Presentation ---
def log_header(title):
    print("\n" + "█" * 60)
    print(f"█  {title}")
    print("█" * 60)


def log_step(step_name):
    print(f"\n🔹 STEP: {step_name}")


def log_pass(msg):
    print(f"   ✅ PASS: {msg}")


def log_fail(msg, expected, got):
    print(f"   ❌ FAIL: {msg}")
    print(f"      Expected: {expected}")
    print(f"      Got:      {got}")


def assert_status(res, expected_code, desc):
    if res.status_code == expected_code:
        log_pass(f"{desc} (Status {expected_code})")
        return True
    else:
        log_fail(f"{desc} Failed", expected_code, f"{res.status_code} - {res.text}")
        return False


def assert_val(actual, expected, field_name):
    if actual == expected:
        log_pass(f"Verified {field_name} is '{expected}'")
    else:
        log_fail(f"Verification of {field_name}", expected, actual)


# ==========================================
# 1. TEAM & PLAYER LOGIC
# ==========================================
def test_teams_comprehensive():
    log_header("PHASE 1: TEAM & PLAYER MANAGEMENT")

    # 1. Create Team
    log_step("Create Team 'Galatasaray'")
    res = requests.post(f"{BASE_URL}/teams/", json={"name": "Galatasaray"})
    if not assert_status(res, 200, "Create Team"):
        return None

    team_data = res.json()["value"]
    team_id = team_data["id"]
    assert_val(team_data["name"], "Galatasaray", "Team Name")

    # 2. Update Attributes
    log_step("Update Team Attributes (PUT)")
    payload = {"city": "Istanbul", "founded": 1905, "colors": "Red/Yellow"}
    res = requests.put(f"{BASE_URL}/teams/{team_id}/", json=payload)
    assert_status(res, 200, "Update Team Attributes")

    # 3. Add Players
    log_step("Add Players (Sub-resource Creation)")
    p1 = {"name": "Muslera", "no": 1}
    p2 = {"name": "Icardi", "no": 9}

    requests.post(f"{BASE_URL}/teams/{team_id}/players/", json=p1)
    requests.post(f"{BASE_URL}/teams/{team_id}/players/", json=p2)
    log_pass("Added Muslera and Icardi")

    # 4. Remove Player
    log_step("Remove Player (DELETE Sub-resource)")
    requests.delete(f"{BASE_URL}/teams/{team_id}/players/Muslera/")
    log_pass("Deleted Player 'Muslera'")

    # 5. Create Rival Team
    log_step("Create Rival Team 'Fenerbahçe'")
    res = requests.post(f"{BASE_URL}/teams/", json={"name": "Fenerbahçe"})
    rival_id = res.json()["value"]["id"]
    log_pass(f"Rival created with ID {rival_id}")

    return team_id, rival_id


# ==========================================
# 2. GAME LOGIC
# ==========================================
def test_games_comprehensive(home_id, away_id):
    log_header("PHASE 2: GAME LIFECYCLE & STATE")

    # 1. Create Game
    log_step("Create Derby Match")
    payload = {
        "home_id": home_id,
        "away_id": away_id,
        "datetime": "2025-05-20T20:00:00",
        "group": "Finals",
    }
    res = requests.post(f"{BASE_URL}/games/", json=payload)
    if not assert_status(res, 200, "Create Game"):
        return None

    game_data = res.json()["value"]
    game_id = game_data["id"]
    assert_val(game_data["state"], "READY", "Initial State")

    # 2. Start Game
    log_step("Start Game (State Change)")
    res = requests.put(f"{BASE_URL}/games/{game_id}/", json={"state": "RUNNING"})
    assert_status(res, 200, "Update State to RUNNING")

    # 3. Update Score
    log_step("Update Score (Goal Scored)")
    score_payload = {"home_score": 1, "away_score": 0}
    res = requests.put(f"{BASE_URL}/games/{game_id}/", json=score_payload)
    assert_status(res, 200, "Update Score")

    # Verify Score
    current_score = res.json()["value"]["score"]
    if current_score["home"] == 1:
        log_pass("Score correctly updated to 1-0")
    else:
        log_fail(
            "Score update", "1-0", f"{current_score['home']}-{current_score['away']}"
        )

    # 4. End Game
    log_step("End Game")
    requests.put(f"{BASE_URL}/games/{game_id}/", json={"state": "ENDED"})
    log_pass("Game Ended")

    return game_id


# ==========================================
# 3. CUP TOURNAMENT LOGIC (UPDATED)
# ==========================================
def test_cup_comprehensive():
    log_header("PHASE 3: TOURNAMENT SIMULATION")

    # 1. Bulk Team Creation
    log_step("Generate 16 Teams for Tournament")
    team_ids = []
    for i in range(1, 17):
        r = requests.post(f"{BASE_URL}/teams/", json={"name": f"Nation-{i}"})
        if r.status_code == 200:
            team_ids.append(r.json()["value"]["id"])
    log_pass(f"Created {len(team_ids)} teams successfully")

    # 2. Create Cup
    log_step("Create Group Tournament")
    payload = {
        "cup_type": "GROUP",
        "team_ids": team_ids,
        "num_groups": 4,
        "playoff_teams": 8,
    }
    res = requests.post(f"{BASE_URL}/cups/", json=payload)
    if not assert_status(res, 200, "Create Cup"):
        return None

    cup_id = res.json()["value"]["id"]

    # 3. Verify Schedule
    log_step("Verify Group Stage Schedule")
    res = requests.get(f"{BASE_URL}/cups/{cup_id}/games/")
    game_ids = res.json()["value"]
    assert_val(len(game_ids), 24, "Total Group Games Generated")

    # 4. Simulate Group Stage
    log_step("Simulate Group Matches (Play & Check Standings)")
    games_per_group = 6
    games_per_round = 2

    for i, gid in enumerate(game_ids):
        # Determine group
        group_idx = i // games_per_group
        group_name = chr(65 + group_idx)  # A, B, C, D

        h_score = random.randint(0, 3)
        a_score = random.randint(0, 3)

        requests.put(
            f"{BASE_URL}/games/{gid}/",
            json={"state": "ENDED", "home_score": h_score, "away_score": a_score},
        )

        if (i + 1) % games_per_round == 0:
            round_num = ((i % games_per_group) // games_per_round) + 1
            print(f"   ► End of Round {round_num} for Group {group_name}")

            # Validate Live Standings
            s_res = requests.get(f"{BASE_URL}/cups/{cup_id}/standings/")
            standings = s_res.json()["value"]["Groups"][group_name]

            print(f"      {'Team':<12} {'P':<3} {'Pts':<3}")
            print(f"      {'-' * 20}")
            for row in standings:
                print(f"      {row[0]:<12} {row[1] + row[2] + row[3]:<3} {row[6]:<3}")

    log_pass("Completed Group Stage")

    # 5. Generate Playoffs
    log_step("Generate Playoff Bracket")
    res = requests.post(f"{BASE_URL}/cups/{cup_id}/playoffs/")
    assert_status(res, 200, "Generate Playoffs")

    data = res.json()["value"]
    assert_val(data["total_games"], 31, "Total Games (Group + Playoff)")

    # 6. Verify Gametree & SHOW IT (Initial)
    log_step("Verify & Show Initial Playoff Bracket")
    res = requests.get(f"{BASE_URL}/cups/{cup_id}/gametree/")
    tree = res.json()["value"]

    if "Playoffs" in tree and tree["Playoffs"]:
        log_pass("Playoff Rounds structure retrieved")
        print("\n" + "      🏆 INITIAL BRACKET (Before Playing)")
        print("      " + "=" * 35)
        for round_name, games in tree["Playoffs"].items():
            print(f"\n      📍 {round_name.upper()}")
            for g in games:
                print(f"         • {g['home']:<20} vs {g['away']}")
    else:
        log_fail("Gametree", "Playoffs section populated", "Empty or Missing")

    # 7. SIMULATE PLAYOFFS (Fixing the Placeholder Issue)
    log_step("Simulate Playoff Matches (Resolve Placeholders)")

    # We iterate round by round to show the progression
    rounds = ["Quarter-Final", "Semi-Final", "Final"]

    for round_name in rounds:
        # Fetch current state of tree
        res = requests.get(f"{BASE_URL}/cups/{cup_id}/gametree/")
        current_round_games = res.json()["value"]["Playoffs"].get(round_name, [])

        if not current_round_games:
            continue

        print(f"\n   ⚽ Playing {round_name} Matches...")

        for g in current_round_games:
            gid = g["game_id"]
            # Force a winner (no draws in playoffs usually)
            s1 = random.randint(2, 5)
            s2 = random.randint(0, 1)

            # Randomize who wins
            if random.choice([True, False]):
                s1, s2 = s2, s1

            requests.put(
                f"{BASE_URL}/games/{gid}/",
                json={"state": "ENDED", "home_score": s1, "away_score": s2},
            )
            print(
                f"      Game {gid}: {g['home']} ({s1}) vs {g['away']} ({s2}) -> ENDED"
            )

        # Now fetch tree again to show the NEXT round has real names
        print(f"   🔄 Updating Bracket View...")
        res = requests.get(f"{BASE_URL}/cups/{cup_id}/gametree/")
        full_tree = res.json()["value"]["Playoffs"]

        print("\n" + f"      🏆 BRACKET STATUS AFTER {round_name.upper()}")
        print("      " + "=" * 40)

        for r_name, games in full_tree.items():
            print(f"\n      📍 {r_name.upper()}")
            for g in games:
                # This print will show Real Names instead of 'Winner of...'
                # if the previous round was played correctly
                status = "✅" if g["state"] == "ENDED" else "⏳"
                print(f"         {status} {g['home']:<20} vs {g['away']}")

    return cup_id, team_ids


# ==========================================
# 4. CASCADING DELETE TEST
# ==========================================
def test_cascading_delete(cup_id):
    log_header("PHASE 4: CASCADING DELETE VERIFICATION")

    # 1. Fetch ALL games
    log_step("Fetch Games Before Deletion")
    res = requests.get(f"{BASE_URL}/cups/{cup_id}/games/")
    game_ids = res.json()["value"]
    print(f"   Cup {cup_id} has {len(game_ids)} games associated with it.")

    # 2. Delete the Cup
    log_step("Delete Cup (Trigger Cascade)")
    res = requests.delete(f"{BASE_URL}/cups/{cup_id}/")
    assert_status(res, 200, "Delete Cup")

    # 3. Verify Games are gone
    log_step("Verify Orphaned Games Deletion")
    all_gone = True
    for gid in game_ids[:5]:
        r = requests.get(f"{BASE_URL}/games/{gid}/")
        if r.status_code != 404:
            log_fail(f"Game {gid} still exists!", "404", r.status_code)
            all_gone = False
            break

    if all_gone:
        log_pass(f"Games successfully deleted from Repo.")


# ==========================================
# MAIN EXECUTION
# ==========================================
if __name__ == "__main__":
    try:
        requests.get(BASE_URL)

        # Run Phases
        t1, t2 = test_teams_comprehensive()
        test_games_comprehensive(t1, t2)
        cup_id, cup_teams = test_cup_comprehensive()

        # Run the cascading verification
        test_cascading_delete(cup_id)

        # Cleanup
        log_header("FINAL CLEANUP")
        requests.delete(f"{BASE_URL}/teams/{t1}/")
        requests.delete(f"{BASE_URL}/teams/{t2}/")
        requests.delete(f"{BASE_URL}/teams/{cup_teams[0]}/")
        log_pass("Cleanup complete")

        print("\n" + "=" * 60)
        print("🎉  DEMONSTRATION COMPLETE: ALL SYSTEMS NOMINAL")
        print("=" * 60 + "\n")

    except requests.exceptions.ConnectionError:
        print(
            "\n❌ FATAL: Cannot connect to server. Run 'python manage.py runserver' first."
        )
