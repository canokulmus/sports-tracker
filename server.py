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
        
        First checks the repository directly for standalone games.
        Then searches through all cups to find games that are part of tournaments.
        """
        # Check if game exists directly in repository
        obj = repository._objects.get(game_id, {}).get('instance')
        if isinstance(obj, Game):
            return obj
        
        # Search through all cups
        for obj_data in repository._objects.values():
            instance = obj_data['instance']
            if isinstance(instance, Cup):
                try:
                    # Use Cup's __getitem__ to find game by ID
                    return instance[game_id]
                except KeyError:
                    # Game not in this cup, continue searching
                    continue
        
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

            # TODO: Frontend Helper - Your partner might need an endpoint to get all teams
            # to populate a dropdown menu.
            # elif cmd == "LIST_TEAMS":
            #     with repo_lock:
            #         teams = [{"id": k, "name": v['instance'].team_name} for k, v in repository._objects.items() if isinstance(v['instance'], Team)]
            #     return {"status": "OK", "teams": teams}

            elif cmd == "CREATE_TEAM":
                name = req.get("name")
                if not name: return {"status": "ERROR", "message": "Missing 'name'"}

                with repo_lock: # Ensure thread-safe creation.
                    tid = repository.create(type="team", name=name)
                    repository.attach(tid, self.user)
                    self.attached_ids.append(tid)
                return {"status": "OK", "id": tid, "message": "Team created"}

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
                        return {"status": "OK", "message": f"Watching {oid}"}
                    return {"status": "ERROR", "message": "Object not watchable"}

            elif cmd == "START":
                gid = req.get("id")
                if gid is None: return {"status": "ERROR", "message": "Missing 'id'"}

                with repo_lock:
                    game = self.find_game(int(gid))
                    if game:
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
                if gid is None or pts is None or side not in ["HOME", "AWAY"]:
                    return {"status": "ERROR", "message": "Invalid params"}

                with repo_lock:
                    game = self.find_game(int(gid))
                    if game:
                        team_obj = game.home() if side == "HOME" else game.away()
                        game.score(int(pts), team_obj)
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
                        # Manually create Cup to avoid 'type' parameter conflict in Repo.create
                        cup = Cup(
                            teams=teams,
                            cup_type=c_type,
                            interval=timedelta(days=1),
                            repo=repository
                        )

                        # Manually register in repository
                        repository._last_id += 1
                        cid = repository._last_id

                        repository._objects[cid] = {
                            "instance": cup,
                            "attachment_count": 0,
                            "users": []
                        }

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
                    
                    # Ensure the cup has a reference to the repo before generating playoffs
                    # This handles cases where the server restarted and the repo reference was lost
                    if not hasattr(cup, 'repo') or cup.repo is None:
                        cup.repo = repository
                    # -----------------------------

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

            else:
                return {"status": "ERROR", "message": f"Unknown command: {cmd}"}

        except (ValueError, KeyError) as e:
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
            with open(SAVE_FILE, 'rb') as f:
                repository = pickle.load(f)

            # Ensure _last_id is consistent with the highest existing ID
            if repository._objects:
                max_id = max(repository._objects.keys())
                if repository._last_id < max_id:
                    print(f"Migrating _last_id from {repository._last_id} to {max_id}")
                    repository._last_id = max_id

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
            with open(SAVE_FILE, 'wb') as f:
                pickle.dump(repository, f)
            print("Server state saved to 'server_state.pkl'.")
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
