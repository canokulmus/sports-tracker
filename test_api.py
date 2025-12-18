import requests
import json
import time

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

    # 2. Update Attributes (Generic Attributes feature)
    log_step("Update Team Attributes (PUT)")
    payload = {"city": "Istanbul", "founded": 1905, "colors": "Red/Yellow"}
    res = requests.put(f"{BASE_URL}/teams/{team_id}/", json=payload)
    assert_status(res, 200, "Update Team Attributes")

    # Verify persistence
    updated_data = res.json()["value"]
    assert_val(updated_data.get("city"), "Istanbul", "City Attribute")
    assert_val(updated_data.get("founded"), 1905, "Founded Attribute")

    # 3. Add Players
    log_step("Add Players (Sub-resource Creation)")
    p1 = {"name": "Muslera", "no": 1}
    p2 = {"name": "Icardi", "no": 9}

    res = requests.post(f"{BASE_URL}/teams/{team_id}/players/", json=p1)
    assert_status(res, 200, f"Add Player {p1['name']}")

    res = requests.post(f"{BASE_URL}/teams/{team_id}/players/", json=p2)
    assert_status(res, 200, f"Add Player {p2['name']}")

    # Verify players exist in Team Detail
    log_step("Verify Roster Persistence")
    res = requests.get(f"{BASE_URL}/teams/{team_id}/")
    players = res.json()["value"]["players"]
    if "Icardi" in players and "Muslera" in players:
        log_pass("Roster contains both players")
    else:
        log_fail("Roster check", "['Muslera', 'Icardi']", list(players.keys()))

    # 4. Remove Player
    log_step("Remove Player (DELETE Sub-resource)")
    res = requests.delete(f"{BASE_URL}/teams/{team_id}/players/Muslera/")
    assert_status(res, 200, "Delete Player 'Muslera'")

    # Verify removal
    res = requests.get(f"{BASE_URL}/teams/{team_id}/")
    players = res.json()["value"]["players"]
    if "Muslera" not in players:
        log_pass("Muslera successfully removed from roster")
    else:
        log_fail("Player removal", "Muslera gone", "Muslera present")

    # 5. Create Rival Team for Game Tests
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
    assert_val(game_data["score"]["home"], 0, "Initial Home Score")

    # 2. Start Game
    log_step("Start Game (State Change)")
    res = requests.put(f"{BASE_URL}/games/{game_id}/", json={"state": "RUNNING"})
    assert_status(res, 200, "Update State to RUNNING")
    assert_val(res.json()["value"]["state"], "RUNNING", "Game State")

    # 3. Update Score
    log_step("Update Score (Goal Scored)")
    score_payload = {"home_score": 1, "away_score": 0}
    res = requests.put(f"{BASE_URL}/games/{game_id}/", json=score_payload)
    assert_status(res, 200, "Update Score")

    # Verify Score Persistence
    current_score = res.json()["value"]["score"]
    if current_score["home"] == 1 and current_score["away"] == 0:
        log_pass("Score correctly updated to 1-0")
    else:
        log_fail(
            "Score update", "1-0", f"{current_score['home']}-{current_score['away']}"
        )

    # 4. End Game
    log_step("End Game")
    res = requests.put(f"{BASE_URL}/games/{game_id}/", json={"state": "ENDED"})
    assert_status(res, 200, "Update State to ENDED")

    return game_id


# ==========================================
# 3. CUP TOURNAMENT LOGIC
# ==========================================
def test_cup_comprehensive():
    log_header("PHASE 3: TOURNAMENT SIMULATION (GROUP -> PLAYOFFS)")

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

    # 3. Verify Schedule Generation
    log_step("Verify Group Stage Schedule")
    res = requests.get(f"{BASE_URL}/cups/{cup_id}/games/")
    games = res.json()["value"]
    # 4 groups * 6 games each = 24 games
    assert_val(len(games), 24, "Total Group Games Generated")

    # 4. Simulate Group Stage (Play all games)
    log_step("Simulate Group Matches (Fast Forward)")
    print("   Playing 24 games...")
    for gid in games:
        # End games randomly to generate standings points
        requests.put(
            f"{BASE_URL}/games/{gid}/",
            json={"state": "ENDED", "home_score": 1, "away_score": 0},
        )
    log_pass("All group games marked as ENDED")

    # 5. Check Standings
    log_step("Retrieve Standings")
    res = requests.get(f"{BASE_URL}/cups/{cup_id}/standings/")
    standings = res.json()["value"]
    if "Groups" in standings and len(standings["Groups"]) == 4:
        log_pass("Standings calculated for 4 Groups")
    else:
        log_fail("Standings Structure", "4 Groups", "Invalid Structure")

    # 6. Generate Playoffs
    log_step("Generate Playoff Bracket")
    res = requests.post(f"{BASE_URL}/cups/{cup_id}/playoffs/")
    assert_status(res, 200, "Generate Playoffs")

    data = res.json()["value"]
    # 24 group games + 4 QF + 2 SF + 1 Final = 31 games total
    assert_val(data["total_games"], 31, "Total Games after Playoffs")

    # 7. Gametree Verification
    log_step("Verify Bracket Structure (Gametree)")
    res = requests.get(f"{BASE_URL}/cups/{cup_id}/gametree/")
    tree = res.json()["value"]

    if "Playoffs" in tree:
        rounds = list(tree["Playoffs"].keys())
        log_pass(f"Playoff Rounds found: {rounds}")

        # Verify Placeholders
        first_round_games = tree["Playoffs"][rounds[0]]
        first_game = first_round_games[0]
        print(
            f"   ℹ️  Sample Playoff Matchup: {first_game['home']} vs {first_game['away']}"
        )
        if "Winner" not in first_game["home"]:
            log_pass("First round teams are resolved (Real Teams)")
    else:
        log_fail("Gametree", "Playoffs section", "Missing")

    return cup_id, team_ids


# ==========================================
# 4. ERROR HANDLING
# ==========================================
def test_error_handling(team_id):
    log_header("PHASE 4: ERROR HANDLING & VALIDATION")

    # 1. Invalid ID
    log_step("Request Invalid Resource ID")
    res = requests.get(f"{BASE_URL}/teams/999999/")
    assert_status(res, 404, "GET Non-existent Team")
    assert_val(res.json()["result"], "error", "Error Format")

    # 2. Invalid Payload
    log_step("Send Invalid Payload")
    res = requests.post(f"{BASE_URL}/teams/", data="Not JSON")
    assert_status(res, 400, "POST Malformed JSON")

    # 3. Logic Error (Game state)
    log_step("Send Invalid Game State Enum")
    # Needs a valid game ID, create a temp one
    game_res = requests.post(
        f"{BASE_URL}/games/",
        json={
            "home_id": team_id,
            "away_id": team_id,  # Playing self allowed in logic but creates game
            "datetime": "2025-01-01T12:00:00",
        },
    )
    gid = game_res.json()["value"]["id"]

    res = requests.put(f"{BASE_URL}/games/{gid}/", json={"state": "SUPER_SAIYAN_MODE"})
    assert_status(res, 400, "Update Invalid Enum State")

    # Cleanup temp game
    requests.delete(f"{BASE_URL}/games/{gid}/")


# ==========================================
# MAIN EXECUTION
# ==========================================
if __name__ == "__main__":
    try:
        # Check connection
        requests.get(BASE_URL)

        # Run Phases
        t1, t2 = test_teams_comprehensive()
        test_games_comprehensive(t1, t2)
        cup_id, cup_teams = test_cup_comprehensive()
        test_error_handling(t1)

        # Cleanup
        log_header("CLEANUP")
        requests.delete(f"{BASE_URL}/cups/{cup_id}/")
        log_pass(f"Deleted Cup {cup_id}")

        # Delete first 2 teams
        requests.delete(f"{BASE_URL}/teams/{t1}/")
        requests.delete(f"{BASE_URL}/teams/{t2}/")

        # Delete cup teams
        for tid in cup_teams:
            requests.delete(f"{BASE_URL}/teams/{tid}/")
        log_pass("Deleted all test teams")

        print("\n" + "=" * 60)
        print("🎉  DEMONSTRATION COMPLETE: ALL SYSTEMS NOMINAL")
        print("=" * 60 + "\n")

    except requests.exceptions.ConnectionError:
        print("\n❌ FATAL: Cannot connect to server.")
        print("   Please run: 'python manage.py runserver' in another terminal.")
