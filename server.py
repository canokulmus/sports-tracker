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


class SocketObserver:
    """
    Implements the Observer pattern. When a watched object (e.g., a Game)
    is updated, its `update` method is called. This observer's role is to
    format the update as a JSON notification and put it into a session-specific queue.
    """

    def __init__(self, message_queue: queue.Queue):
        self.message_queue = message_queue

    def update(self, game: Any) -> None:
        """Constructs a game update notification and adds it to the client's message queue."""
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
            if cmd == "USER":
                self.user = req.get("username", "Anonymous")
                return {"status": "OK", "message": f"User set to {self.user}"}

            elif cmd == "GET_TEAMS":
                with repo_lock:
                    teams = []
                    for oid, data in repository._objects.items():
                        if isinstance(data['instance'], Team):
                            teams.append({"id": oid, "name": data['instance'].team_name})
                return {"status": "OK", "teams": teams}

            elif cmd == "GET_CUPS":
                with repo_lock:
                    cups = []
                    for oid, data in repository._objects.items():
                        if isinstance(data['instance'], Cup):
                            cups.append({"id": oid, "type": data['instance'].cup_type, "desc": str(data['instance'])})
                return {"status": "OK", "cups": cups}

            elif cmd == "GET_GAMES":
                with repo_lock:
                    games = []
                    for oid, data in repository._objects.items():
                        if isinstance(data['instance'], Game):
                            g = data['instance']
                            games.append({
                                "id": oid,
                                "home": g.home().team_name,
                                "away": g.away().team_name,
                                "state": g.state.name,
                                "score": {"home": g.home_score, "away": g.away_score}
                            })
                return {"status": "OK", "games": games}

            elif cmd == "SEARCH":
                query = req.get("query")
                if not query: return {"status": "ERROR", "message": "Missing 'query'"}

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
                if not name: return {"status": "ERROR", "message": "Missing 'name'"}

                with repo_lock: # Ensure thread-safe creation.
                    tid = repository.create(type="team", name=name)
                    repository.attach(tid, self.user)
                    self.attached_ids.append(tid)
                return {"status": "OK", "id": tid, "message": "Team created"}
            
            elif cmd == "UPDATE_TEAM":
                tid = req.get("id")
                if tid is None: return {"status": "ERROR", "message": "Missing 'id'"}
                
                updates = {k: v for k, v in req.items() if k not in ["command", "id"]}
                with repo_lock:
                    obj = repository._objects.get(int(tid))
                    if obj and isinstance(obj['instance'], Team):
                        obj['instance'].update(**updates)
                        return {"status": "OK", "message": f"Team {tid} updated"}
                    return {"status": "ERROR", "message": "Team not found"}

            elif cmd == "ADD_PLAYER":
                tid = req.get("team_id")
                pname = req.get("name")
                pno = req.get("no")
                if tid is None or not pname or pno is None:
                    return {"status": "ERROR", "message": "Missing params"}
                with repo_lock:
                    obj = repository._objects.get(int(tid))
                    if obj and isinstance(obj['instance'], Team):
                        pid = obj['instance'].addplayer(pname, int(pno))
                        return {"status": "OK", "message": f"Player added with ID {pid}"}
                    return {"status": "ERROR", "message": "Team not found"}

            elif cmd == "REMOVE_PLAYER":
                tid = req.get("team_id")
                pname = req.get("name")
                if tid is None or not pname:
                    return {"status": "ERROR", "message": "Missing 'team_id' or 'name'"}
                with repo_lock:
                    obj = repository._objects.get(int(tid))
                    if obj and isinstance(obj['instance'], Team):
                        obj['instance'].delplayer(pname)
                        return {"status": "OK", "message": f"Player {pname} removed"}
                    return {"status": "ERROR", "message": "Team not found"}

            elif cmd == "GET_PLAYERS":
                tid = req.get("team_id")
                if tid is None: return {"status": "ERROR", "message": "Missing 'team_id'"}
                with repo_lock:
                    obj = repository._objects.get(int(tid))
                    if obj and isinstance(obj['instance'], Team):
                        # Assuming Team.players is a dictionary of {name: number}
                        players = [{"name": name, "no": no} for name, no in obj['instance'].players.items()]
                        return {"status": "OK", "players": players}
                    return {"status": "ERROR", "message": "Team not found"}

            elif cmd == "CREATE_GAME":
                h_id = req.get("home_id")
                a_id = req.get("away_id")
                if h_id is None or a_id is None:
                    return {"status": "ERROR", "message": "Missing team IDs"}

                with repo_lock:
                    h_data = repository._objects.get(int(h_id))
                    a_data = repository._objects.get(int(a_id))
                    if not h_data or not a_data:
                        return {"status": "ERROR", "message": "Teams not found"}

                    gid = repository.create(
                        type="game",
                        home=h_data['instance'],
                        away=a_data['instance'],
                        datetime=datetime.now()
                    )
                return {"status": "OK", "id": gid, "message": "Game created"}
            
            elif cmd == "UPDATE_GAME":
                gid = req.get("id")
                if gid is None: return {"status": "ERROR", "message": "Missing 'id'"}
                
                updates = {k: v for k, v in req.items() if k not in ["command", "id"]}
                
                # Handle datetime conversion if present
                if "datetime" in updates:
                    try:
                        updates["datetime"] = datetime.fromisoformat(updates["datetime"])
                    except (ValueError, TypeError):
                        return {"status": "ERROR", "message": "Invalid datetime format (use ISO)"}

                with repo_lock:
                    # Resolve team IDs to objects if provided
                    if "home_id" in updates:
                        hid = updates.pop("home_id")
                        h_data = repository._objects.get(int(hid))
                        if not h_data: return {"status": "ERROR", "message": f"Home team {hid} not found"}
                        updates["home"] = h_data["instance"]
                    if "away_id" in updates:
                        aid = updates.pop("away_id")
                        a_data = repository._objects.get(int(aid))
                        if not a_data: return {"status": "ERROR", "message": f"Away team {aid} not found"}
                        updates["away"] = a_data["instance"]

                    game = self.find_game(int(gid))
                    if game:
                        game.update(**updates)
                        return {"status": "OK", "message": f"Game {gid} updated"}
                    return {"status": "ERROR", "message": "Game not found"}

            elif cmd == "WATCH":
                oid = req.get("id")
                if oid is None: return {"status": "ERROR", "message": "Missing 'id'"}

                with repo_lock:
                    oid = int(oid)
                    if oid not in repository._objects:
                        return {"status": "ERROR", "message": "Object not found"}

                    # Attach this session's observer to the game object.
                    instance = repository._objects[oid]['instance']
                    if hasattr(instance, 'watch'):
                        instance.watch(self.observer)
                        if oid not in self.watched_ids:
                            self.watched_ids.append(oid)
                        
                        # If it's a game, send immediate update so client has initial state
                        if isinstance(instance, Game):
                            self.observer.update(instance)

                        # If it's a cup, send updates for all its games
                        if isinstance(instance, Cup):
                            for game in instance.games:
                                self.observer.update(game)

                        return {"status": "OK", "message": f"Watching {oid}"}
                    return {"status": "ERROR", "message": "Object not watchable"}

            elif cmd == "GET_GAME_STATS":
                gid = req.get("id")
                if gid is None: return {"status": "ERROR", "message": "Missing 'id'"}
                with repo_lock:
                    game = self.find_game(int(gid))
                    if game:
                        return {"status": "OK", "stats": game.stats()}
                    return {"status": "ERROR", "message": "Game not found"}

            elif cmd == "START":
                gid = req.get("id")
                if gid is None: return {"status": "ERROR", "message": "Missing 'id'"}

                with repo_lock:
                    game = self.find_game(int(gid))
                    if game:
                        if game.state == GameState.FINISHED:
                            return {"status": "ERROR", "message": "Cannot start a finished game"}
                        
                        game.start()
                        return {
                            "status": "OK", 
                            "message": f"Game started: {game.home().team_name} vs {game.away().team_name}"
                        }
                    return {"status": "ERROR", "message": "Game not found"}

            elif cmd == "PAUSE":
                gid = req.get("id")
                if gid is None: return {"status": "ERROR", "message": "Missing 'id'"}

                with repo_lock:
                    game = self.find_game(int(gid))
                    if game:
                        game.pause()
                        return {
                            "status": "OK", 
                            "message": f"Game paused: {game.home().team_name} vs {game.away().team_name}"
                        }
                    return {"status": "ERROR", "message": "Game not found"}

            elif cmd == "RESUME":
                gid = req.get("id")
                if gid is None: return {"status": "ERROR", "message": "Missing 'id'"}

                with repo_lock:
                    game = self.find_game(int(gid))
                    if game:
                        game.resume()
                        return {
                            "status": "OK", 
                            "message": f"Game resumed: {game.home().team_name} vs {game.away().team_name}"
                        }
                    return {"status": "ERROR", "message": "Game not found"}
            elif cmd == "SCORE":
                gid = req.get("id")
                pts = req.get("points")
                side = req.get("side", "").upper()
                player = req.get("player")
                if gid is None or pts is None or side not in ["HOME", "AWAY"]:
                    return {"status": "ERROR", "message": "Invalid params"}

                with repo_lock:
                    game = self.find_game(int(gid))
                    if game:
                        # Safety check: only allow scoring if the game is actually running
                        if game.state != GameState.STARTED:
                            return {"status": "ERROR", "message": f"Cannot score: Game is in {game.state.name} state"}
                        
                        team_obj = game.home() if side == "HOME" else game.away()
                        game.score(int(pts), team_obj, player=player)
                        return {
                            "status": "OK", 
                            "message": f"Score updated: {game.home().team_name} {game.home_score} - {game.away_score} {game.away().team_name}"
                        }
                    return {"status": "ERROR", "message": "Game not found"}

            elif cmd == "CREATE_CUP":
                c_type = req.get("cup_type")
                t_ids = req.get("team_ids")
                if not c_type or not t_ids:
                    return {"status": "ERROR", "message": "Missing 'cup_type' or 'team_ids'"}

                with repo_lock:
                    # Resolve team IDs to Team objects
                    teams = []
                    for tid in t_ids:
                        obj_data = repository._objects.get(int(tid))
                        if not obj_data or not isinstance(obj_data['instance'], Team):
                            return {"status": "ERROR", "message": f"Team ID {tid} not found or invalid"}
                        teams.append(obj_data['instance'])

                    try:
                        cid = repository.create(
                            type="cup",
                            teams=teams,
                            cup_type=c_type,
                            interval=timedelta(days=1),
                        )

                        # Attach user to the new Cup
                        repository.attach(cid, self.user)
                        self.attached_ids.append(cid)

                    except ValueError as e:
                        return {"status": "ERROR", "message": str(e)}

                return {"status": "OK", "id": cid, "message": "Cup created"}

            elif cmd == "GET_STANDINGS":
                cid = req.get("id")
                if cid is None:
                    return {"status": "ERROR", "message": "Missing 'id'"}

                with repo_lock:
                    obj_data = repository._objects.get(int(cid))
                    if not obj_data:
                        return {"status": "ERROR", "message": "Object not found"}

                    cup = obj_data['instance']
                    if not isinstance(cup, Cup):
                        return {"status": "ERROR", "message": "Object is not a cup"}

                    # Calculate standings
                    standings = cup.standings()

                return {"status": "OK", "standings": standings}

            elif cmd == "GET_GAMETREE":
                cid = req.get("id")
                if cid is None: return {"status": "ERROR", "message": "Missing 'id'"}
                with repo_lock:
                    obj = repository._objects.get(int(cid))
                    if not obj or not isinstance(obj['instance'], Cup):
                        return {"status": "ERROR", "message": "Cup not found"}
                    try:
                        tree = obj['instance'].gametree()
                        return {"status": "OK", "gametree": tree}
                    except ValueError as e:
                        return {"status": "ERROR", "message": str(e)}

            elif cmd == "GET_CUP_GAMES":
                cid = req.get("id")
                if cid is None: return {"status": "ERROR", "message": "Missing 'id'"}

                with repo_lock:
                    obj = repository._objects.get(int(cid))
                    if not obj or not isinstance(obj['instance'], Cup):
                        return {"status": "ERROR", "message": "Cup not found"}

                    cup = obj['instance']
                    # Return list of game IDs associated with this cup
                    game_ids = [g.id() for g in cup.games]

                return {"status": "OK", "game_ids": game_ids}

            elif cmd == "GENERATE_PLAYOFFS":
                cid = req.get("id")
                if cid is None: return {"status": "ERROR", "message": "Missing 'id'"}

                with repo_lock:
                    obj = repository._objects.get(int(cid))
                    if not obj or not isinstance(obj['instance'], Cup):
                        return {"status": "ERROR", "message": "Cup not found"}

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
                        return {"status": "ERROR", "message": str(e)}

            elif cmd == "SAVE":
                save_state()
                return {"status": "OK", "message": "State saved"}

            elif cmd == "END":
                gid = req.get("id")
                if gid is None: return {"status": "ERROR", "message": "Missing 'id'"}

                with repo_lock:
                    game = self.find_game(int(gid))
                    if game:
                        game.end()
                        # Final skoru göster
                        return {
                            "status": "OK", 
                            "message": f"Game ended: {game.home().team_name} {game.home_score} - {game.away_score} {game.away().team_name}"
                        }
                    return {"status": "ERROR", "message": "Game not found"}

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
                if oid is None: return {"status": "ERROR", "message": "Missing 'id'"}
                with repo_lock:
                    try:
                        repository.attach(int(oid), self.user)
                        if int(oid) not in self.attached_ids:
                            self.attached_ids.append(int(oid))
                        return {"status": "OK", "message": f"Attached to {oid}"}
                    except ValueError as e:
                        return {"status": "ERROR", "message": str(e)}

            elif cmd == "DETACH":
                oid = req.get("id")
                if oid is None: return {"status": "ERROR", "message": "Missing 'id'"}
                with repo_lock:
                    try:
                        repository.detach(int(oid), self.user)
                        if int(oid) in self.attached_ids:
                            self.attached_ids.remove(int(oid))
                        return {"status": "OK", "message": f"Detached from {oid}"}
                    except ValueError as e:
                        return {"status": "ERROR", "message": str(e)}

            elif cmd == "DELETE":
                oid = req.get("id")
                if oid is None: return {"status": "ERROR", "message": "Missing 'id'"}
                with repo_lock:
                    try:
                        # Auto-detach current user to allow deletion if they are the only one
                        if int(oid) in self.attached_ids:
                            repository.detach(int(oid), self.user)
                            self.attached_ids.remove(int(oid))
                        
                        repository.delete(int(oid))
                        
                        if int(oid) in self.watched_ids:
                            self.watched_ids.remove(int(oid))
                            
                        return {"status": "OK", "message": "Object deleted"}
                    except ValueError as e:
                        return {"status": "ERROR", "message": str(e)}

            else:
                return {"status": "ERROR", "message": f"Unknown command: {cmd}"}

        except (ValueError, KeyError, TypeError, AttributeError) as e:
            return {"status": "ERROR", "message": f"Invalid parameter or ID: {str(e)}"}
        except Exception as e:
            return {"status": "ERROR", "message": f"Internal Server Error: {str(e)}"}

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
                err = {"status": "ERROR", "message": "Invalid JSON format"}
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
    global repository
    if os.path.exists(SAVE_FILE):
        try:
            with repo_lock:
                with open(SAVE_FILE, 'rb') as f:
                    loaded_repo = pickle.load(f)
                    if isinstance(loaded_repo, Repo):
                        repository = loaded_repo

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
                pickle.dump(repository, f)
            os.replace(temp_file, SAVE_FILE)
            print(f"Server state saved to '{SAVE_FILE}'.")
        except Exception as e:
            print(f"Error saving state: {e}")


if __name__ == "__main__":
    load_state()
    
    # TODO: Learn - This starts the WebSocket server. 'serve' creates a thread for each connection calling 'agent'.
    print(f"WebSocket Server listening on {HOST}:{PORT}...")
    with serve(agent, HOST, PORT) as server:
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            print("\nServer shutting down.")
        finally:
            save_state()
