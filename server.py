import sys
import threading
import pickle
import os
import queue
import json
from datetime import datetime, timedelta
from typing import Any, List, Dict, Tuple
from websockets.sync.server import serve
from websockets.exceptions import ConnectionClosedError, ConnectionClosedOK

from sports_lib import Repo, Game, Team, Cup, GameState

# --- Configuration & Globals ---
HOST = '0.0.0.0'  # Listen on all available interfaces.
PORT = 8888
SAVE_FILE = 'server_state.pkl'  # File for object persistence.

# The global repository holds the application's state. It is shared across all threads.
# The `repo_lock` is crucial to prevent race conditions when multiple clients
# modify the repository concurrently.
repository = Repo()
repo_lock = threading.RLock()

# User management: Store registered users
registered_users = set()  # Set of usernames
user_watches = {}  # Username -> Set[int]
users_lock = threading.RLock()


class SocketObserver:
    """
    Implements the Observer pattern. When a watched object (e.g., a Game)
    is updated, its `update` method is called. This observer's role is to
    format the update as a JSON notification and put it into a session-specific queue.
    """

    def __init__(self, message_queue: queue.Queue):
        self.message_queue = message_queue

    def __getstate__(self):
        # Prevent pickling of the queue, which causes save_state to fail
        return {}

    def __setstate__(self, state):
        # Restore with dummy values; these observers are dead upon restore
        self.message_queue = None

    def update(self, game: Any) -> None:
        """Constructs a game update notification and adds it to the client's message queue."""
        if not getattr(self, 'message_queue', None):
            return

        try:
            payload = {
                "type": "NOTIFICATION",
                "game_id": game.id(),
                "home": game.home().team_name,
                "away": game.away().team_name,
                "state": game.state.name,
                "score": {
                    "home": game.home_score,
                    "away": game.away_score
                }
            }
            self.message_queue.put(json.dumps(payload))
        except Exception as e:
            error_payload = {"type": "ERROR", "message": f"Notification failed: {str(e)}"}
            self.message_queue.put(json.dumps(error_payload))


class Session:
    """
    Represents a single client session.
    In Phase 4, this class manages the state for a WebSocket connection.
    """
    def __init__(self, websocket):
        self.websocket = websocket
        self.client_address = websocket.remote_address
        self.user = "Anonymous"  # Default user, can be changed with the USER command.

        # This queue is the bridge between the game logic (which calls observer.update)
        # and the notification agent (which sends to the socket). This is a suggested
        # design in the project description to handle asynchronous notifications.
        self.output_queue: queue.Queue[str | None] = queue.Queue()
        self.observer = SocketObserver(self.output_queue)

        self.watched_ids: List[int] = []  # IDs of objects this session is watching.
        self.attached_ids: List[int] = [] # IDs of objects this session has interacted with.
        self.running = True

        # Start the background thread for sending notifications.
        self.agent_thread = threading.Thread(target=self.notification_agent, daemon=True)
        self.agent_thread.start()

    def find_game(self, game_id: int):
        """Find a game by ID in repository or cups.
        
        If the system is consistent, all games (standalone or cup-managed)
        should be registered in the central repository._objects.
        """
        obj = repository._objects.get(game_id, {}).get('instance')
        if isinstance(obj, Game):
            return obj
        
        # Game not found anywhere
        return None

    def notification_agent(self) -> None:
        """
        The "notification agent" required by the project description.
        It runs in a separate thread, blocking on the `output_queue`. When a message
        appears, it sends it to the client. This decouples sending from receiving.
        """
        while self.running:
            try:
                msg = self.output_queue.get()
                if msg is None:  # A `None` message is a sentinel to stop the thread.
                    break
                # TODO: Learn - WebSockets are message-based, so we don't need '\n' delimiters anymore.
                self.websocket.send(msg)
            except (ConnectionClosedError, ConnectionClosedOK):
                break # Stop if the socket is closed.
            except Exception as e:
                print(f"Notification error: {e}")
                break

    def process_command(self, req: Dict[str, Any]) -> Dict[str, Any]:
        """Parses the JSON request and executes the corresponding action."""
        cmd = req.get("command", "").upper()

        try:
            if cmd == "LOGIN":
                username = req.get("username", "").strip()
                if not username:
                    return {"status": "ERROR", "message": "Username is required for LOGIN command."}

                with users_lock:
                    # Add user to registered users if not already present
                    if username not in registered_users:
                        registered_users.add(username)
                        save_state()  # Persist user data

                    # Set the session user
                    self.user = username

                    # Restore watched games
                    watches = user_watches.get(self.user, set()).copy()
                    print(f"DEBUG: Restoring watches for user '{self.user}': {watches}")

                if watches:
                    with repo_lock:
                        for oid in watches:
                            if oid in repository._objects:
                                instance = repository._objects[oid]['instance']
                                if hasattr(instance, 'watch'):
                                    if oid not in self.watched_ids:
                                        instance.watch(self.observer)
                                        self.watched_ids.append(oid)
                                        
                                        # Send immediate update
                                        if isinstance(instance, Game):
                                            self.observer.update(instance)
                                        if isinstance(instance, Cup):
                                            for game in instance.games:
                                                self.observer.update(game)

                return {
                    "status": "OK", 
                    "username": username, 
                    "message": f"Logged in as {username}",
                    "watched_ids": self.watched_ids
                }

            elif cmd == "USER":
                self.user = req.get("username", "Anonymous")
                return {"status": "OK", "message": f"User set to {self.user}"}

            elif cmd == "GET_TEAMS":
                with repo_lock:
                    teams = []
                    for oid, data in repository._objects.items():
                        if isinstance(data['instance'], Team):
                            team = data['instance']
                            players = {}
                            for pid, pdata in team.players.items():
                                players[pdata['name']] = {"no": pdata['no']}

                            team_data = {
                                "id": oid,
                                "name": team.team_name,
                                "players": players
                            }

                            # Add custom fields (generic attributes)
                            for key, value in team._generic_attrs.items():
                                team_data[key] = value

                            teams.append(team_data)
                return {"status": "OK", "teams": teams}

            elif cmd == "GET_CUPS":
                with repo_lock:
                    cups = []
                    for oid, data in repository._objects.items():
                        if isinstance(data['instance'], Cup):
                            c = data['instance']

                            # Get cup name from metadata
                            cup_name = data.get('metadata', {}).get('name', f"Tournament #{oid}")

                            # Get team IDs
                            team_ids = []
                            for team in c.teams:
                                for tid, tdata in repository._objects.items():
                                    if tdata['instance'] is team:
                                        team_ids.append(tid)
                                        break

                            cups.append({
                                "id": oid,
                                "name": cup_name,
                                "type": c.cup_type,
                                "teams": team_ids,
                                "gameCount": len(c.games),
                                "desc": str(c)
                            })
                return {"status": "OK", "cups": cups}

            elif cmd == "GET_GAMES":
                with repo_lock:
                    games = []
                    for oid, data in repository._objects.items():
                        if isinstance(data['instance'], Game):
                            g = data['instance']

                            # Find team IDs by searching repository for team objects
                            home_id = None
                            away_id = None
                            for tid, tdata in repository._objects.items():
                                if tdata['instance'] is g.home_:
                                    home_id = tid
                                if tdata['instance'] is g.away_:
                                    away_id = tid

                            # Get scorers from stats
                            stats = g.stats()
                            home_scorers = []
                            away_scorers = []

                            # Extract scorers from players (those with score > 0)
                            for player_name, score in stats['Home']['Players'].items():
                                if score > 0:
                                    home_scorers.append({"name": player_name, "goals": score})

                            for player_name, score in stats['Away']['Players'].items():
                                if score > 0:
                                    away_scorers.append({"name": player_name, "goals": score})

                            games.append({
                                "id": oid,
                                "home": g.home().team_name,
                                "away": g.away().team_name,
                                "home_id": home_id,
                                "away_id": away_id,
                                "state": g.state.name,
                                "score": {"home": g.home_score, "away": g.away_score},
                                "scorers": {"home": home_scorers, "away": away_scorers},
                                "timeline": g.timeline,
                                "datetime": g.datetime.isoformat() if g.datetime and hasattr(g.datetime, 'isoformat') else str(g.datetime) if g.datetime else None,
                                "group": g.group
                            })
                return {"status": "OK", "games": games}

            elif cmd == "SEARCH":
                query = req.get("query")
                if not query: return {"status": "ERROR", "message": "Missing 'query' parameter for SEARCH command."}

                with repo_lock:
                    results = []
                    for oid, data in repository._objects.items():
                        obj = data['instance']
                        if query.lower() in str(obj).lower():
                            results.append({
                                "id": oid,
                                "type": type(obj).__name__,
                                "desc": str(obj)
                            })
                return {"status": "OK", "results": results}

            elif cmd == "CREATE_TEAM":
                name = req.get("name")
                if not name: return {"status": "ERROR", "message": "Missing 'name' parameter for CREATE_TEAM command."}

                with repo_lock: # Ensure thread-safe creation.
                    tid = repository.create(type="team", name=name)
                    repository.attach(tid, self.user)
                    self.attached_ids.append(tid)
                    save_state()
                return {"status": "OK", "id": tid, "message": "Team created"}
            
            elif cmd == "UPDATE_TEAM":
                tid = req.get("id")
                if tid is None: return {"status": "ERROR", "message": "Missing 'id' parameter for UPDATE_TEAM command."}

                updates = {k: v for k, v in req.items() if k not in ["command", "id", "requestId"]}
                with repo_lock:
                    obj = repository._objects.get(int(tid))
                    if obj and isinstance(obj['instance'], Team):
                        obj['instance'].update(**updates)
                        save_state()
                        return {"status": "OK", "message": f"Team {tid} updated"}
                    return {"status": "ERROR", "message": f"Team with ID {tid} not found for UPDATE_TEAM command."}

            elif cmd == "ADD_PLAYER":
                tid = req.get("team_id")
                pname = req.get("name")
                pno = req.get("no")
                if tid is None or not pname or pno is None:
                    return {"status": "ERROR", "message": "Missing 'team_id', 'name', or 'no' parameters for ADD_PLAYER command."}
                with repo_lock:
                    obj = repository._objects.get(int(tid))
                    if obj and isinstance(obj['instance'], Team):
                        pid = obj['instance'].addplayer(pname, int(pno))
                        save_state()
                        return {"status": "OK", "message": f"Player added with ID {pid}"}
                    return {"status": "ERROR", "message": f"Team with ID {tid} not found for ADD_PLAYER command."}

            elif cmd == "REMOVE_PLAYER":
                tid = req.get("team_id")
                pname = req.get("name")
                if tid is None or not pname:
                    return {"status": "ERROR", "message": "Missing 'team_id' or 'name' parameters for REMOVE_PLAYER command."}
                with repo_lock:
                    obj = repository._objects.get(int(tid))
                    if obj and isinstance(obj['instance'], Team):
                        obj['instance'].delplayer(pname)
                        save_state()
                        return {"status": "OK", "message": f"Player {pname} removed"}
                    return {"status": "ERROR", "message": f"Team with ID {tid} not found for REMOVE_PLAYER command."}

            elif cmd == "GET_PLAYERS":
                tid = req.get("team_id")
                if tid is None: return {"status": "ERROR", "message": "Missing 'team_id' parameter for GET_PLAYERS command."}
                with repo_lock:
                    obj = repository._objects.get(int(tid))
                    if obj and isinstance(obj['instance'], Team):
                        # Team.players is Dict[int, Dict[str, Any]] -> {id: {"name": str, "no": int}}
                        players = [{"name": pdata["name"], "no": pdata["no"]} for pdata in obj['instance'].players.values()]
                        return {"status": "OK", "players": players}
                    return {"status": "ERROR", "message": f"Team with ID {tid} not found for GET_PLAYERS command."}

            elif cmd == "CREATE_GAME":
                h_id = req.get("home_id")
                a_id = req.get("away_id")
                if h_id is None or a_id is None:
                    return {"status": "ERROR", "message": "Missing 'home_id' or 'away_id' parameters for CREATE_GAME command."}

                with repo_lock:
                    h_data = repository._objects.get(int(h_id))
                    a_data = repository._objects.get(int(a_id))
                    if not h_data or not a_data:
                        return {"status": "ERROR", "message": f"One or both teams (Home: {h_id}, Away: {a_id}) not found for CREATE_GAME command."}

                    gid = repository.create(
                        type="game",
                        home=h_data['instance'],
                        away=a_data['instance'],
                        datetime=datetime.now()
                    )
                    save_state()
                return {"status": "OK", "id": gid, "message": "Game created"}
            
            elif cmd == "UPDATE_GAME":
                gid = req.get("id")
                if gid is None: return {"status": "ERROR", "message": "Missing 'id' parameter for UPDATE_GAME command."}
                
                updates = {k: v for k, v in req.items() if k not in ["command", "id"]}
                
                # Handle datetime conversion if present
                if "datetime" in updates:
                    try:
                        updates["datetime"] = datetime.fromisoformat(updates["datetime"])
                    except (ValueError, TypeError):
                        return {"status": "ERROR", "message": "Invalid datetime format for UPDATE_GAME command (use ISO format)."}

                with repo_lock:
                    # Resolve team IDs to objects if provided
                    if "home_id" in updates:
                        hid = updates.pop("home_id")
                        h_data = repository._objects.get(int(hid))
                        if not h_data: return {"status": "ERROR", "message": f"Home team with ID {hid} not found for UPDATE_GAME command."}
                        updates["home"] = h_data["instance"]
                    if "away_id" in updates:
                        aid = updates.pop("away_id")
                        a_data = repository._objects.get(int(aid))
                        if not a_data: return {"status": "ERROR", "message": f"Away team with ID {aid} not found for UPDATE_GAME command."}
                        updates["away"] = a_data["instance"]

                    game = self.find_game(int(gid))
                    if game:
                        game.update(**updates)
                        save_state()
                        return {"status": "OK", "message": f"Game {gid} updated"}
                    return {"status": "ERROR", "message": f"Game with ID {gid} not found for UPDATE_GAME command."}

            elif cmd == "WATCH":
                oid = req.get("id")
                if oid is None: return {"status": "ERROR", "message": "Missing 'id' parameter for WATCH command."}

                with repo_lock:
                    oid = int(oid)
                    if oid not in repository._objects:
                        return {"status": "ERROR", "message": f"Object with ID {oid} not found for WATCH command."}

                    # Attach this session's observer to the game object.
                    instance = repository._objects[oid]['instance']
                    if hasattr(instance, 'watch'):
                        instance.watch(self.observer)
                        if oid not in self.watched_ids:
                            self.watched_ids.append(oid)
                        
                        # Persist watch for user
                        if self.user != "Anonymous":
                            with users_lock:
                                if self.user not in user_watches:
                                    user_watches[self.user] = set()
                                user_watches[self.user].add(oid)
                                save_state()

                        # If it's a game, send immediate update so client has initial state
                        if isinstance(instance, Game):
                            self.observer.update(instance)

                        # If it's a cup, send updates for all its games
                        if isinstance(instance, Cup):
                            for game in instance.games:
                                self.observer.update(game)

                        return {"status": "OK", "message": f"Watching {oid}"}
                    return {"status": "ERROR", "message": f"Object with ID {oid} is not watchable (must implement 'watch' method)."}

            elif cmd == "UNWATCH":
                oid = req.get("id")
                if oid is None: return {"status": "ERROR", "message": "Missing 'id' parameter for UNWATCH command."}

                with repo_lock:
                    oid = int(oid)
                    if oid not in repository._objects:
                        return {"status": "ERROR", "message": f"Object with ID {oid} not found for UNWATCH command."}

                    # Remove this session's observer from the object
                    instance = repository._objects[oid]['instance']
                    if hasattr(instance, 'unwatch'):
                        instance.unwatch(self.observer)
                        if oid in self.watched_ids:
                            self.watched_ids.remove(oid)
                        
                        # Remove persistence
                        if self.user != "Anonymous":
                            with users_lock:
                                if self.user in user_watches and oid in user_watches[self.user]:
                                    user_watches[self.user].remove(oid)
                                    save_state()

                        return {"status": "OK", "message": f"Unwatched {oid}"}
                    return {"status": "ERROR", "message": f"Object with ID {oid} is not watchable (must implement 'unwatch' method)."}

            elif cmd == "GET_WATCHED_GAMES":
                with repo_lock:
                    watched_games = []
                    for oid in self.watched_ids:
                        if oid in repository._objects:
                            instance = repository._objects[oid]['instance']
                            if isinstance(instance, Game):
                                # Find team IDs
                                home_id = None
                                away_id = None
                                for tid, tdata in repository._objects.items():
                                    if tdata['instance'] is instance.home_:
                                        home_id = tid
                                    if tdata['instance'] is instance.away_:
                                        away_id = tid

                                # Get scorers from stats
                                stats = instance.stats()
                                home_scorers = []
                                away_scorers = []

                                # Extract scorers from players (those with score > 0)
                                for player_name, score in stats['Home']['Players'].items():
                                    if score > 0:
                                        home_scorers.append({"name": player_name, "goals": score})

                                for player_name, score in stats['Away']['Players'].items():
                                    if score > 0:
                                        away_scorers.append({"name": player_name, "goals": score})

                                watched_games.append({
                                    "id": oid,
                                    "home": instance.home().team_name,
                                    "away": instance.away().team_name,
                                    "home_id": home_id,
                                    "away_id": away_id,
                                    "state": instance.state.name,
                                    "score": {"home": instance.home_score, "away": instance.away_score},
                                    "scorers": {"home": home_scorers, "away": away_scorers},
                                    "timeline": instance.timeline,
                                    "datetime": instance.datetime.isoformat() if instance.datetime and hasattr(instance, 'isoformat') else str(instance.datetime) if instance.datetime else None,
                                    "group": instance.group
                                })
                    return {"status": "OK", "games": watched_games}

            elif cmd == "GET_GAME_STATS":
                gid = req.get("id")
                if gid is None: return {"status": "ERROR", "message": "Missing 'id' parameter for GET_GAME_STATS command."}
                with repo_lock:
                    game = self.find_game(int(gid))
                    if game:
                        return {"status": "OK", "stats": game.stats()}
                    return {"status": "ERROR", "message": f"Game with ID {gid} not found for GET_GAME_STATS command."}

            elif cmd == "START":
                gid = req.get("id")
                if gid is None: return {"status": "ERROR", "message": "Missing 'id' parameter for START command."}

                with repo_lock:
                    game = self.find_game(int(gid))
                    if game:
                        if game.state == GameState.ENDED:
                            return {"status": "ERROR", "message": f"Cannot start game {gid} because it has already ended."}

                        game.start()
                        save_state()
                        return {
                            "status": "OK",
                            "message": f"Game started: {game.home().team_name} vs {game.away().team_name}"
                        }
                    return {"status": "ERROR", "message": f"Game with ID {gid} not found for START command."}

            elif cmd == "PAUSE":
                gid = req.get("id")
                if gid is None: return {"status": "ERROR", "message": "Missing 'id' parameter for PAUSE command."}

                with repo_lock:
                    game = self.find_game(int(gid))
                    if game:
                        game.pause()
                        save_state()
                        return {
                            "status": "OK",
                            "message": f"Game paused: {game.home().team_name} vs {game.away().team_name}"
                        }
                    return {"status": "ERROR", "message": f"Game with ID {gid} not found for PAUSE command."}

            elif cmd == "RESUME":
                gid = req.get("id")
                if gid is None: return {"status": "ERROR", "message": "Missing 'id' parameter for RESUME command."}

                with repo_lock:
                    game = self.find_game(int(gid))
                    if game:
                        game.resume()
                        save_state()
                        return {
                            "status": "OK",
                            "message": f"Game resumed: {game.home().team_name} vs {game.away().team_name}"
                        }
                    return {"status": "ERROR", "message": f"Game with ID {gid} not found for RESUME command."}
            elif cmd == "SCORE":
                gid = req.get("id")
                pts = req.get("points")
                side = req.get("side", "").upper()
                player = req.get("player")
                if gid is None or pts is None or side not in ["HOME", "AWAY"]:
                    return {"status": "ERROR", "message": "Invalid parameters for SCORE command (requires 'id', 'points', 'side'='HOME'/'AWAY')."}

                with repo_lock:
                    game = self.find_game(int(gid))
                    if game:
                        # Safety check: only allow scoring if the game is actually running
                        if game.state != GameState.RUNNING:
                            return {"status": "ERROR", "message": f"Cannot score in game {gid}: Game is in {game.state.name} state (must be RUNNING)."}

                        team_obj = game.home() if side == "HOME" else game.away()
                        game.score(int(pts), team_obj, player=player)
                        save_state()
                        return {
                            "status": "OK",
                            "message": f"Score updated: {game.home().team_name} {game.home_score} - {game.away_score} {game.away().team_name}"
                        }
                    return {"status": "ERROR", "message": f"Game with ID {gid} not found for SCORE command."}

            elif cmd == "CREATE_CUP":
                c_type = req.get("cup_type")
                c_name = req.get("name", "")
                t_ids = req.get("team_ids")
                num_groups = req.get("num_groups", 4)  # Default: 4 groups
                playoff_teams = req.get("playoff_teams", 8)  # Default: 8 teams

                if not c_type or not t_ids:
                    return {"status": "ERROR", "message": "Missing 'cup_type' or 'team_ids' parameters for CREATE_CUP command."}

                with repo_lock:
                    # Resolve team IDs to Team objects
                    teams = []
                    for tid in t_ids:
                        obj_data = repository._objects.get(int(tid))
                        if not obj_data or not isinstance(obj_data['instance'], Team):
                            return {"status": "ERROR", "message": f"Team ID {tid} not found or invalid during CREATE_CUP command."}
                        teams.append(obj_data['instance'])

                    try:
                        # Prepare kwargs for Cup creation
                        cup_kwargs = {
                            "type": "cup",
                            "teams": teams,
                            "cup_type": c_type,
                            "interval": timedelta(days=1),
                        }

                        # Add GROUP-specific parameters if applicable
                        if c_type in ["GROUP", "GROUP2"]:
                            cup_kwargs["num_groups"] = int(num_groups)
                            cup_kwargs["playoff_teams"] = int(playoff_teams)

                        cid = repository.create(**cup_kwargs)

                        # Store cup name in metadata
                        if 'metadata' not in repository._objects[cid]:
                            repository._objects[cid]['metadata'] = {}
                        repository._objects[cid]['metadata']['name'] = c_name

                        # Attach user to the new Cup
                        repository.attach(cid, self.user)
                        self.attached_ids.append(cid)
                        save_state()

                    except ValueError as e:
                        return {"status": "ERROR", "message": f"Error creating cup: {str(e)}"}

                return {"status": "OK", "id": cid, "message": "Cup created"}

            elif cmd == "GET_STANDINGS":
                cid = req.get("id")
                if cid is None:
                    return {"status": "ERROR", "message": "Missing 'id' parameter for GET_STANDINGS command."}

                with repo_lock:
                    obj_data = repository._objects.get(int(cid))
                    if not obj_data:
                        return {"status": "ERROR", "message": f"Object with ID {cid} not found for GET_STANDINGS command."}

                    cup = obj_data['instance']
                    if not isinstance(cup, Cup):
                        return {"status": "ERROR", "message": f"Object with ID {cid} is not a Cup (found {type(cup).__name__}) for GET_STANDINGS command."}

                    # Calculate standings
                    raw_standings = cup.standings()

                    # Transform standings to frontend format
                    if isinstance(raw_standings, list):
                        # LEAGUE format: list of tuples (team, won, draw, lost, gf, ga, points)
                        standings = []
                        for row in raw_standings:
                            standings.append({
                                "team": row[0],
                                "played": row[1] + row[2] + row[3],  # won + draw + lost
                                "won": row[1],
                                "draw": row[2],
                                "lost": row[3],
                                "gf": row[4],
                                "ga": row[5],
                                "points": row[6]
                            })
                    elif isinstance(raw_standings, dict):
                        # GROUP format: nested dict with {Groups: {A: [...], B: [...]}, Playoffs: {...}}
                        standings = {}
                        for top_level_key, top_level_value in raw_standings.items():
                            if isinstance(top_level_value, dict):
                                # This is Groups or similar nested structure
                                standings[top_level_key] = {}
                                for group_name, group_standings in top_level_value.items():
                                    if isinstance(group_standings, list):
                                        standings[top_level_key][group_name] = []
                                        for row in group_standings:
                                            standings[top_level_key][group_name].append({
                                                "team": row[0],
                                                "played": row[1] + row[2] + row[3],
                                                "won": row[1],
                                                "draw": row[2],
                                                "lost": row[3],
                                                "gf": row[4],
                                                "ga": row[5],
                                                "points": row[6]
                                            })
                                    else:
                                        standings[top_level_key][group_name] = group_standings
                            elif isinstance(top_level_value, list):
                                # Direct list of tuples
                                standings[top_level_key] = []
                                for row in top_level_value:
                                    standings[top_level_key].append({
                                        "team": row[0],
                                        "played": row[1] + row[2] + row[3],
                                        "won": row[1],
                                        "draw": row[2],
                                        "lost": row[3],
                                        "gf": row[4],
                                        "ga": row[5],
                                        "points": row[6]
                                    })
                            else:
                                standings[top_level_key] = top_level_value
                    else:
                        standings = raw_standings

                return {"status": "OK", "standings": standings}

            elif cmd == "GET_GAMETREE":
                cid = req.get("id")
                if cid is None: return {"status": "ERROR", "message": "Missing 'id' parameter for GET_GAMETREE command."}
                with repo_lock:
                    obj = repository._objects.get(int(cid))
                    if not obj or not isinstance(obj['instance'], Cup):
                        return {"status": "ERROR", "message": f"Cup with ID {cid} not found for GET_GAMETREE command."}
                    try:
                        tree = obj['instance'].gametree()
                        return {"status": "OK", "gametree": tree}
                    except ValueError as e:
                        return {"status": "ERROR", "message": f"Error retrieving gametree for cup {cid}: {str(e)}"}

            elif cmd == "GET_CUP_GAMES":
                cid = req.get("id")
                if cid is None: return {"status": "ERROR", "message": "Missing 'id' parameter for GET_CUP_GAMES command."}

                with repo_lock:
                    obj = repository._objects.get(int(cid))
                    if not obj or not isinstance(obj['instance'], Cup):
                        return {"status": "ERROR", "message": f"Cup with ID {cid} not found for GET_CUP_GAMES command."}

                    cup = obj['instance']
                    games_data = []
                    for g in cup.games:
                        try:
                            gid = g.id()
                            
                            # Find team IDs
                            home_id = None
                            away_id = None
                            for tid, tdata in repository._objects.items():
                                if tdata['instance'] is g.home_:
                                    home_id = tid
                                if tdata['instance'] is g.away_:
                                    away_id = tid
                            
                            # Get scorers
                            stats = g.stats()
                            home_scorers = []
                            away_scorers = []
                            for player_name, score in stats['Home']['Players'].items():
                                if score > 0:
                                    home_scorers.append({"name": player_name, "goals": score})
                            for player_name, score in stats['Away']['Players'].items():
                                if score > 0:
                                    away_scorers.append({"name": player_name, "goals": score})

                            games_data.append({
                                "id": gid,
                                "home": g.home().team_name,
                                "away": g.away().team_name,
                                "home_id": home_id,
                                "away_id": away_id,
                                "state": g.state.name,
                                "score": {"home": g.home_score, "away": g.away_score},
                                "scorers": {"home": home_scorers, "away": away_scorers},
                                "timeline": g.timeline,
                                "datetime": g.datetime.isoformat() if g.datetime and hasattr(g.datetime, 'isoformat') else str(g.datetime) if g.datetime else None,
                                "group": g.group
                            })
                        except Exception as e:
                            print(f"Error processing game {g} in cup {cid}: {e}")
                            continue

                return {"status": "OK", "games": games_data}

            elif cmd == "GENERATE_PLAYOFFS":
                cid = req.get("id")
                if cid is None: return {"status": "ERROR", "message": "Missing 'id' parameter for GENERATE_PLAYOFFS command."}

                with repo_lock:
                    obj = repository._objects.get(int(cid))
                    if not obj or not isinstance(obj['instance'], Cup):
                        return {"status": "ERROR", "message": f"Cup with ID {cid} not found for GENERATE_PLAYOFFS command."}

                    cup = obj['instance']
                    
                    try:
                        # Capture the number of games before generation
                        count_before = len(cup.games)
                        cup.generate_playoffs()
                        new_games = len(cup.games) - count_before

                        # We must save the new state immediately
                        save_state()

                        return {"status": "OK", "message": f"Playoffs generated. {new_games} new games created."}
                    except ValueError as e:
                        return {"status": "ERROR", "message": f"Error generating playoffs for cup {cid}: {str(e)}"}

            elif cmd == "SAVE":
                save_state()
                return {"status": "OK", "message": "State saved"}

            elif cmd == "END":
                gid = req.get("id")
                if gid is None: return {"status": "ERROR", "message": "Missing 'id' parameter for END command."}

                with repo_lock:
                    game = self.find_game(int(gid))
                    if game:
                        game.end()
                        # Final skoru göster
                        return {
                            "status": "OK", 
                            "message": f"Game ended: {game.home().team_name} {game.home_score} - {game.away_score} {game.away().team_name}"
                        }
                    return {"status": "ERROR", "message": f"Game with ID {gid} not found for END command."}

            elif cmd == "LIST":
                with repo_lock:
                    results = repository.list()
                    items = [{"id": r[0], "desc": r[1]} for r in results]
                return {"status": "OK", "items": items}

            elif cmd == "LIST_ATTACHED":
                with repo_lock:
                    results = repository.listattached(self.user)
                    items = [{"id": r[0], "desc": r[1]} for r in results]
                return {"status": "OK", "items": items}

            elif cmd == "ATTACH":
                oid = req.get("id")
                if oid is None: return {"status": "ERROR", "message": "Missing 'id' parameter for ATTACH command."}
                with repo_lock:
                    try:
                        repository.attach(int(oid), self.user)
                        if int(oid) not in self.attached_ids:
                            self.attached_ids.append(int(oid))
                        return {"status": "OK", "message": f"Attached to {oid}"}
                    except ValueError as e:
                        return {"status": "ERROR", "message": f"Error attaching to object {oid}: {str(e)}"}

            elif cmd == "DETACH":
                oid = req.get("id")
                if oid is None: return {"status": "ERROR", "message": "Missing 'id' parameter for DETACH command."}
                with repo_lock:
                    try:
                        repository.detach(int(oid), self.user)
                        if int(oid) in self.attached_ids:
                            self.attached_ids.remove(int(oid))
                        return {"status": "OK", "message": f"Detached from {oid}"}
                    except ValueError as e:
                        return {"status": "ERROR", "message": f"Error detaching from object {oid}: {str(e)}"}

            elif cmd == "DELETE":
                oid = req.get("id")
                if oid is None: return {"status": "ERROR", "message": "Missing 'id' parameter for DELETE command."}
                with repo_lock:
                    try:
                        obj_data = repository._objects.get(int(oid))

                        # If deleting a Cup, also delete all its games
                        if obj_data and isinstance(obj_data['instance'], Cup):
                            cup = obj_data['instance']
                            game_ids_to_delete = []

                            # Find all game IDs that belong to this cup
                            for gid, gdata in repository._objects.items():
                                if isinstance(gdata['instance'], Game):
                                    game = gdata['instance']
                                    # Check if this game is in the cup's games list
                                    if game in cup.games:
                                        game_ids_to_delete.append(gid)

                            # Delete all games first
                            for gid in game_ids_to_delete:
                                # Attempt to detach user if attached (handles persistence across restarts)
                                if gid in repository._objects:
                                    repository.detach(gid, self.user)
                                if gid in self.attached_ids:
                                    self.attached_ids.remove(gid)
                                if gid in self.watched_ids:
                                    self.watched_ids.remove(gid)
                                repository.delete(gid)
                                
                                # Clean up global watches for this game
                                with users_lock:
                                    for u_watches in user_watches.values():
                                        if gid in u_watches:
                                            u_watches.discard(gid)

                        # Auto-detach current user to allow deletion if they are the only one
                        # Attempt to detach user if attached (handles persistence across restarts)
                        if obj_data:
                            repository.detach(int(oid), self.user)
                        if int(oid) in self.attached_ids:
                            self.attached_ids.remove(int(oid))

                        repository.delete(int(oid))

                        if int(oid) in self.watched_ids:
                            self.watched_ids.remove(int(oid))
                        
                        # Clean up global watches for this object
                        with users_lock:
                            for u_watches in user_watches.values():
                                if int(oid) in u_watches:
                                    u_watches.discard(int(oid))

                        save_state()
                        return {"status": "OK", "message": "Object deleted"}
                    except ValueError as e:
                        return {"status": "ERROR", "message": f"Error deleting object {oid}: {str(e)}"}

            else:
                return {"status": "ERROR", "message": f"Unknown command received: '{cmd}'"}

        except (ValueError, KeyError, TypeError, AttributeError) as e:
            return {"status": "ERROR", "message": f"Invalid parameter or ID processing command '{cmd}': {str(e)}"}
        except Exception as e:
            return {"status": "ERROR", "message": f"Internal Server Error processing command '{cmd}': {str(e)}"}

    def cleanup(self):
        """
        Crucial for graceful shutdown. Detaches this session's observer from all
        watched objects to prevent the server from trying to send notifications
        to a closed connection.
        """
        with repo_lock:
            for oid in self.watched_ids:
                if oid in repository._objects:
                    obj = repository._objects[oid]['instance']
                    if hasattr(obj, 'unwatch'):
                        obj.unwatch(self.observer)
            for oid in self.attached_ids:
                if oid in repository._objects:
                    repository.detach(oid, self.user)

def agent(websocket):
    """
    The main handler for a WebSocket connection.
    This function is called in a new thread for each client by `server.serve`.
    """
    session = Session(websocket)
    print(f"Accepted connection from {session.client_address}")

    try:
        # Send welcome message
        welcome = {"type": "INFO", "message": "Connected to Sports Tracker (WebSocket Mode)"}
        websocket.send(json.dumps(welcome))

        # Loop for incoming messages
        # TODO: Learn - 'for message in websocket' is a blocking loop that yields messages as they arrive.
        for message in websocket:
            try:
                request = json.loads(message)
                response = session.process_command(request)
                if response:
                    websocket.send(json.dumps(response))
            except json.JSONDecodeError:
                err = {"status": "ERROR", "message": "Invalid JSON format received from client."}
                websocket.send(json.dumps(err))

    except (ConnectionClosedError, ConnectionClosedOK):
        print(f"Connection closed normally for {session.client_address}")
    except Exception as e:
        print(f"Unexpected error for {session.client_address}: {e}")
    finally:
        # Cleanup
        session.running = False
        session.output_queue.put(None) # Signal notifier to stop
        session.cleanup()
        print(f"Session cleaned up for {session.client_address}")

def load_state():
    """
    Implements persistency by loading the entire repository from a pickle file.
    This is done once at server startup.
    """
    global repository, registered_users, user_watches
    if os.path.exists(SAVE_FILE):
        try:
            with repo_lock:
                with open(SAVE_FILE, 'rb') as f:
                    saved_data = pickle.load(f)

                    # Support both old format (just Repo) and new format (dict with repo + users)
                    if isinstance(saved_data, Repo):
                        repository = saved_data
                    elif isinstance(saved_data, dict):
                        repository = saved_data.get('repository', Repo())
                        with users_lock:
                            registered_users = saved_data.get('users', set())
                            user_watches = saved_data.get('user_watches', {})
                    else:
                        repository = Repo()

                # Ensure _last_id is consistent with the highest existing ID
                if repository._objects:
                    max_id = max(repository._objects.keys())
                    if repository._last_id < max_id:
                        print(f"Migrating _last_id from {repository._last_id} to {max_id}")
                        repository._last_id = max_id

                # Restore repo references for objects that need them (e.g. Cups)
                for data in repository._objects.values():
                    if isinstance(data['instance'], Cup):
                        data['instance'].repo = repository

            print(f"DEBUG: Loaded state. Users: {len(registered_users)}, Watches: {sum(len(v) for v in user_watches.values())}")
            print("Server state loaded from 'server_state.pkl'.")
        except Exception as e:
            print(f"Could not load state: {e}. Starting with a new repository.")


def save_state():
    """
    Implements persistency by saving the entire repository to a pickle file.
    This can be triggered by a client command or on server shutdown.
    """
    with repo_lock:
        try:
            # Use a temporary file for atomic write to prevent corruption
            temp_file = f"{SAVE_FILE}.tmp"
            with open(temp_file, 'wb') as f:
                # Save both repository and registered users
                with users_lock:
                    saved_data = {
                        'repository': repository,
                        'users': registered_users,
                        'user_watches': user_watches
                    }
                pickle.dump(saved_data, f)
            print(f"DEBUG: Saved state. Users: {len(registered_users)}, Watches: {sum(len(v) for v in user_watches.values())}")
            os.replace(temp_file, SAVE_FILE)
            print(f"Server state saved to '{SAVE_FILE}'.")
        except Exception as e:
            print(f"Error saving state: {e}")


if __name__ == "__main__":
    load_state()
    
    # TODO: Learn - This starts the WebSocket server. 'serve' creates a thread for each connection calling 'agent'.
    print(f"WebSocket Server listening on {HOST}:{PORT}...")
    try:
        # TODO: Learn - This starts the WebSocket server. 'serve' creates a thread for each connection calling 'agent'.
        with serve(agent, HOST, PORT) as server:
            server.serve_forever()
    except KeyboardInterrupt:
        print("\nServer shutting down.")
    finally:
        save_state()
        # Force exit to prevent hanging on non-daemon threads from the websocket server.
        os._exit(0)
