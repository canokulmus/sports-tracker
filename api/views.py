import json
from datetime import timedelta

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.dateparse import parse_datetime

from sports_lib.repo import Repo
from sports_lib.team import Team
from sports_lib.game import Game
from sports_lib.constants import GameState
from sports_lib.cup import Cup, CupType

# Global Repository Instance (In-memory storage for the running process)
REPO = Repo()

# --- Helper Functions ---


def send_success(value=None, message=None):
    """Returns a standard JSON success response."""
    response = {"result": "success"}
    if value is not None:
        response["value"] = value
    if message is not None:
        response["message"] = message
    return JsonResponse(response, status=200)


def send_error(reason, status=400):
    """Returns a standard JSON error response."""
    return JsonResponse({"result": "error", "reason": reason}, status=status)


def get_team_or_404(team_id):
    """Retrieves a Team from REPO or returns an error tuple."""
    try:
        instance = REPO.get(team_id)
        if not isinstance(instance, Team):
            return None, "Object found but it is not a Team."
        return instance, None
    except ValueError:
        return None, f"Team with ID {team_id} does not exist."


def serialize_team(team_id, team):
    """Serializes a Team object to a dictionary."""
    data = {
        "id": team_id,
        "name": team.team_name,
        "players": team.players,
    }
    # Include generic attributes if any exist
    if hasattr(team, "_generic_attrs"):
        data.update(team._generic_attrs)
    return data


def get_game_or_404(game_id):
    """Retrieves a Game from REPO or returns an error tuple."""
    try:
        instance = REPO.get(game_id)
        if not isinstance(instance, Game):
            return None, "Object found but it is not a Game."
        return instance, None
    except ValueError:
        return None, f"Game with ID {game_id} does not exist."


def serialize_game(game_id, game):
    """Serializes a Game object to a dictionary."""
    return {
        "id": game_id,
        "home": game.home().team_name,
        "away": game.away().team_name,
        "home_id": [
            k for k, v in REPO._objects.items() if v["instance"] == game.home()
        ][0]
        if game.home()
        else None,
        "away_id": [
            k for k, v in REPO._objects.items() if v["instance"] == game.away()
        ][0]
        if game.away()
        else None,
        "datetime": str(game.datetime),
        "state": game.state.name,
        "score": {"home": game.home_score, "away": game.away_score},
        "group": game.group,
    }


def get_cup_or_404(cup_id):
    """Retrieves a Cup from REPO or returns an error tuple."""
    try:
        instance = REPO.get(cup_id)
        if not isinstance(instance, Cup):
            return None, "Object found but it is not a Cup."
        return instance, None
    except ValueError:
        return None, f"Cup with ID {cup_id} does not exist."


def serialize_cup(cup_id, cup):
    """Serializes a Cup object to a dictionary."""
    return {
        "id": cup_id,
        "type": cup.cup_type,
        "teams": [t.team_name for t in cup.teams],
        "team_ids": [k for k, v in REPO._objects.items() if v["instance"] in cup.teams],
        "game_count": len(cup.games),
        "num_groups": cup.num_groups,
        "playoff_teams": cup.playoff_teams,
    }


# --- Views ---


@csrf_exempt
def team_collection(request):
    """
    API endpoint for Team collection.
    GET: List all teams. POST: Create a new team.
    """
    if request.method == "GET":
        teams_list = []
        all_objects = REPO.list()

        for obj_id, _ in all_objects:
            try:
                instance = REPO.get(obj_id)
                if isinstance(instance, Team):
                    teams_list.append(serialize_team(obj_id, instance))
            except ValueError:
                continue

        return send_success(teams_list)

    elif request.method == "POST":
        try:
            body = json.loads(request.body)
            name = body.get("name")

            new_id = REPO.create(type="team", name=name)

            # Retrieve the created object to return it
            new_team = REPO.get(new_id)
            return send_success(serialize_team(new_id, new_team))

        except json.JSONDecodeError:
            return send_error("Invalid JSON payload.")
        except ValueError as e:
            return send_error(str(e))

    else:
        return send_error("Method not allowed. Use GET or POST.", status=405)


@csrf_exempt
def team_detail(request, team_id):
    """
    API endpoint for a specific Team.
    GET: Retrieve details. PUT: Update attributes. DELETE: Remove team.
    """
    if request.method == "GET":
        team, error = get_team_or_404(team_id)
        if error:
            return send_error(error, status=404)
        return send_success(serialize_team(team_id, team))

    elif request.method == "PUT":
        team, error = get_team_or_404(team_id)
        if error:
            return send_error(error, status=404)

        try:
            body = json.loads(request.body)

            # Update explicit team_name if provided
            if "name" in body:
                team.team_name = body["name"]
                del body["name"]  # Prevent duplication in generic attrs

            # Update generic attributes
            for key, value in body.items():
                team[key] = value

            return send_success(serialize_team(team_id, team))

        except json.JSONDecodeError:
            return send_error("Invalid JSON payload.")
        except Exception as e:
            return send_error(str(e))

    elif request.method == "DELETE":
        try:
            # Ensure existence before deletion
            team, error = get_team_or_404(team_id)
            if error:
                return send_error(error, status=404)

            REPO.delete(team_id)
            return send_success(message=f"Team {team_id} deleted successfully.")
        except ValueError as e:
            return send_error(str(e), status=404)

    else:
        return send_error("Method not allowed. Use GET, PUT, or DELETE.", status=405)


@csrf_exempt
def player_collection(request, team_id):
    """
    API endpoint for Player collection within a Team.
    POST: Add a player.
    """
    if request.method == "POST":
        team, error = get_team_or_404(team_id)
        if error:
            return send_error(error, status=404)

        try:
            body = json.loads(request.body)
            player_name = body.get("name")
            player_no = body.get("no")

            if not player_name or player_no is None:
                return send_error("Fields 'name' and 'no' are required.")

            if not isinstance(player_no, int):
                return send_error("Field 'no' must be an integer.")

            team.addplayer(player_name, player_no)
            return send_success(team.players)

        except json.JSONDecodeError:
            return send_error("Invalid JSON payload.")
        except Exception as e:
            return send_error(str(e))

    else:
        return send_error("Method not allowed. Use POST to add a player.", status=405)


@csrf_exempt
def player_detail(request, team_id, player_name):
    """
    API endpoint for a specific Player.
    DELETE: Remove a player.
    """
    if request.method == "DELETE":
        team, error = get_team_or_404(team_id)
        if error:
            return send_error(error, status=404)

        try:
            team.delplayer(player_name)
            return send_success(team.players)
        except ValueError as e:
            # Team.delplayer raises ValueError if player not found
            return send_error(str(e), status=404)

    else:
        return send_error(
            "Method not allowed. Use DELETE to remove a player.", status=405
        )


# --- Game Views ---


@csrf_exempt
def game_collection(request):
    """
    API endpoint for Game collection.
    GET: List all games. POST: Create a new game.
    """
    if request.method == "GET":
        games_list = []
        all_objects = REPO.list()

        for obj_id, _ in all_objects:
            try:
                instance = REPO.get(obj_id)
                if isinstance(instance, Game):
                    games_list.append(serialize_game(obj_id, instance))
            except ValueError:
                continue

        return send_success(games_list)

    elif request.method == "POST":
        try:
            body = json.loads(request.body)
            home_id = body.get("home_id")
            away_id = body.get("away_id")
            dt_str = body.get("datetime")
            group = body.get("group")  # Optional

            if not home_id or not away_id or not dt_str:
                return send_error(
                    "Fields 'home_id', 'away_id', and 'datetime' are required."
                )

            dt_obj = parse_datetime(dt_str)
            if dt_obj is None:
                return send_error(
                    "Invalid datetime format. Use ISO 8601 (e.g., '2023-10-27T14:30:00')."
                )

            # Fetch related Team objects
            home_team, err1 = get_team_or_404(home_id)
            away_team, err2 = get_team_or_404(away_id)

            if err1:
                return send_error(f"Home Team Error: {err1}", status=404)
            if err2:
                return send_error(f"Away Team Error: {err2}", status=404)

            new_id = REPO.create(
                type="game",
                home=home_team,
                away=away_team,
                datetime=dt_obj,
                group=group,
            )

            new_game = REPO.get(new_id)
            return send_success(serialize_game(new_id, new_game))

        except json.JSONDecodeError:
            return send_error("Invalid JSON payload.")
        except ValueError as e:
            return send_error(str(e))

    else:
        return send_error("Method not allowed. Use GET or POST.", status=405)


@csrf_exempt
def game_detail(request, game_id):
    """
    API endpoint for a specific Game.
    GET: Retrieve details. PUT: Update state/score/datetime. DELETE: Remove game.
    """
    game, error = get_game_or_404(game_id)
    if error:
        return send_error(error, status=404)

    if request.method == "GET":
        return send_success(serialize_game(game_id, game))

    elif request.method == "PUT":
        try:
            body = json.loads(request.body)

            if "datetime" in body:
                dt_obj = parse_datetime(body["datetime"])
                if dt_obj:
                    game.datetime = dt_obj

            # Update State
            if "state" in body:
                try:
                    game.state = GameState[body["state"].upper()]
                except KeyError:
                    return send_error(
                        f"Invalid state. Valid options: {[s.name for s in GameState]}"
                    )

            # Update Scores (direct override for CRUD)
            if "home_score" in body:
                game.home_score = int(body["home_score"])
            if "away_score" in body:
                game.away_score = int(body["away_score"])

            return send_success(serialize_game(game_id, game))

        except json.JSONDecodeError:
            return send_error("Invalid JSON payload.")
        except Exception as e:
            return send_error(str(e))

    elif request.method == "DELETE":
        try:
            REPO.delete(game_id)
            return send_success(message=f"Game {game_id} deleted successfully.")
        except ValueError as e:
            return send_error(str(e), status=404)

    else:
        return send_error("Method not allowed. Use GET, PUT, or DELETE.", status=405)


# --- Cup Views ---


@csrf_exempt
def cup_collection(request):
    """
    API endpoint for Cup collection.
    GET: List all cups. POST: Create a new cup.
    """
    if request.method == "GET":
        cups_list = []
        all_objects = REPO.list()

        for obj_id, _ in all_objects:
            try:
                instance = REPO.get(obj_id)
                if isinstance(instance, Cup):
                    cups_list.append(serialize_cup(obj_id, instance))
            except ValueError:
                continue

        return send_success(cups_list)

    elif request.method == "POST":
        try:
            body = json.loads(request.body)
            cup_type = body.get("cup_type")
            team_ids = body.get("team_ids")

            num_groups = body.get("num_groups", 4)
            playoff_teams = body.get("playoff_teams", 8)

            if not cup_type or not team_ids:
                return send_error(
                    "Fields 'cup_type' and 'team_ids' (list of ints) are required."
                )

            # Validate Team IDs
            teams_instances = []
            for tid in team_ids:
                team_obj, err = get_team_or_404(tid)
                if err:
                    return send_error(f"Invalid Team ID {tid}: {err}", status=404)
                teams_instances.append(team_obj)

            if not hasattr(CupType, cup_type):
                return send_error(
                    f"Invalid cup_type. Options: {[a for a in dir(CupType) if not a.startswith('__')]}"
                )

            # Create Cup (pass repo for internal game creation)
            new_id = REPO.create(
                type="cup",
                teams=teams_instances,
                cup_type=cup_type,
                interval=timedelta(days=1),  # Default interval
                num_groups=num_groups,
                playoff_teams=playoff_teams,
                repo=REPO,
            )

            new_cup = REPO.get(new_id)
            return send_success(serialize_cup(new_id, new_cup))

        except json.JSONDecodeError:
            return send_error("Invalid JSON payload.")
        except ValueError as e:
            return send_error(str(e))

    else:
        return send_error("Method not allowed. Use GET or POST.", status=405)


@csrf_exempt
def cup_detail(request, cup_id):
    """
    API endpoint for a specific Cup.
    GET: Retrieve details. DELETE: Remove cup and associated games.
    """
    cup, error = get_cup_or_404(cup_id)
    if error:
        return send_error(error, status=404)

    if request.method == "GET":
        return send_success(serialize_cup(cup_id, cup))

    elif request.method == "DELETE":
        try:
            # Cascading delete: Remove associated games first
            game_ids_to_delete = [g.id() for g in cup.games]
            deleted_games_count = 0

            for gid in game_ids_to_delete:
                try:
                    REPO.delete(gid)
                    deleted_games_count += 1
                except ValueError:
                    # Game might have been deleted manually
                    pass

            REPO.delete(cup_id)

            return send_success(
                message=f"Cup {cup_id} and {deleted_games_count} associated games deleted successfully."
            )

        except ValueError as e:
            return send_error(str(e), status=404)

    else:
        return send_error("Method not allowed. Use GET or DELETE.", status=405)


@csrf_exempt
def cup_standings(request, cup_id):
    """
    API endpoint for Cup standings (GET).
    """
    if request.method == "GET":
        cup, error = get_cup_or_404(cup_id)
        if error:
            return send_error(error, status=404)

        return send_success(cup.standings())
    else:
        return send_error("Method not allowed. Use GET.", status=405)


@csrf_exempt
def cup_gametree(request, cup_id):
    """
    API endpoint for Cup game tree/bracket (GET).
    """
    if request.method == "GET":
        cup, error = get_cup_or_404(cup_id)
        if error:
            return send_error(error, status=404)

        try:
            return send_success(cup.gametree())
        except ValueError as e:
            # LEAGUE cups raise ValueError for gametree()
            return send_error(str(e))
    else:
        return send_error("Method not allowed. Use GET.", status=405)


@csrf_exempt
def cup_games(request, cup_id):
    """
    API endpoint for retrieving Game IDs associated with a Cup (GET).
    """
    if request.method == "GET":
        cup, error = get_cup_or_404(cup_id)
        if error:
            return send_error(error, status=404)

        # Get IDs of all games generated by this cup
        game_ids = [g.id() for g in cup.games]
        return send_success(game_ids)
    else:
        return send_error("Method not allowed. Use GET.", status=405)


@csrf_exempt
def cup_playoffs(request, cup_id):
    """
    API endpoint to generate playoffs for a GROUP cup (POST).
    """
    if request.method == "POST":
        cup, error = get_cup_or_404(cup_id)
        if error:
            return send_error(error, status=404)

        try:
            cup.generate_playoffs()
            # Return new game count and updated structure
            return send_success(
                {
                    "message": "Playoffs generated successfully.",
                    "total_games": len(cup.games),
                    "playoff_rounds": len(cup.playoff_rounds)
                    if hasattr(cup, "playoff_rounds")
                    else 0,
                }
            )
        except ValueError as e:
            return send_error(str(e))
        except Exception as e:
            return send_error(f"Failed to generate playoffs: {str(e)}")

    else:
        return send_error("Method not allowed. Use POST.", status=405)
