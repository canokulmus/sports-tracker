# api/views.py
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

# Import your Phase 1 library
from sports_lib.repo import Repo
from sports_lib.team import Team

# 1. Initialize a GLOBAL repository.
# Since we aren't using a database, this keeps data in memory while the server runs.
# If you restart the server, this data will be lost.
REPO = Repo()

# Optional: Pre-fill some dummy data so GET returns something immediately
try:
    t1 = REPO.create(type="team", name="Galatasaray")
    t2 = REPO.create(type="team", name="Fenerbahçe")
except:
    pass


# Helper to format success responses consistently
def send_success(data):
    return JsonResponse({"result": "success", "value": data}, status=200)


# Helper to format error responses consistently
def send_error(reason, status=400):
    return JsonResponse({"result": "error", "reason": reason}, status=status)


@csrf_exempt  # We disable CSRF protection to make testing easier with tools like Postman
def team_collection(request):
    """
    Handles requests to /api/teams/
    GET  -> Returns a list of all teams.
    POST -> Creates a new team.
    """

    # --- IMPLEMENTING GET (Retrieve) ---
    if request.method == "GET":
        teams_list = []

        # 1. Get all objects from your library
        all_objects = REPO.list()  # returns list of (id, description)

        # 2. Iterate and filter only for 'Team' objects
        for obj_id, _ in all_objects:
            try:
                obj_instance = REPO.get(obj_id)
                # Check if this object is actually a Team
                if isinstance(obj_instance, Team):
                    teams_list.append(
                        {
                            "id": obj_id,
                            "name": obj_instance.team_name,
                            "players": obj_instance.players,
                        }
                    )
            except ValueError:
                continue

        # 3. Return the JSON response
        return send_success(teams_list)

    # --- IMPLEMENTING POST (Create) ---
    elif request.method == "POST":
        try:
            # 1. Parse JSON body
            body = json.loads(request.body)
            team_name = body.get("name")

            if not team_name:
                return send_error("Field 'name' is required.")

            # 2. Use your library to create the team
            new_id = REPO.create(type="team", name=team_name)

            # 3. Return the ID of the new team
            return send_success({
                "id": new_id, 
                "message": "Team created successfully",
                "name": team_name
            })

        except json.JSONDecodeError:
            return send_error("Invalid JSON payload.")
        except ValueError as e:
            return send_error(str(e))

    # --- HANDLE UNSUPPORTED METHODS ---
    else:
        return send_error("Method not allowed. Use GET or POST.", status=405)
