import socket
import sys
import threading
import pickle
import os
import queue
import json
from typing import Any, List, Dict, Tuple

# This script implements a multithreaded TCP server for the Sports Tracker service,
# as per the Phase 2 requirements.
#
# Architecture:
# - A main thread listens for and accepts new TCP connections.
# - For each client, a new `Session` thread is created to handle all communication.
# - Communication is done via a JSON-based protocol over newline-delimited messages (NDJSON).
# - A global `repository` object stores all shared data (teams, games, etc.).
# - A `threading.RLock` is used to ensure thread-safe access to the shared repository.

# Import Phase 1 classes
from repo import Repo
from game import Game
from team import Team
from cup import Cup
from constants import GameState

# --- Configuration & Globals ---
HOST = ''  # Listen on all available interfaces.
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


class Session(threading.Thread):
    """
    Represents a single client session. Each session runs in its own thread.
    It uses a two-thread model internally:
    1. `run()`: The main thread for this session, blocking on `socket.readline()` to read commands.
    2. `notification_agent()`: A background thread that sends queued messages to the client.
    """
    def __init__(self, client_socket: socket.socket, client_address: Tuple[str, int]):
        super().__init__()
        self.client_socket = client_socket
        self.client_address = client_address
        self.user = "Anonymous"  # Default user, can be changed with the USER command.

        # This queue is the bridge between the game logic (which calls observer.update)
        # and the notification agent (which sends to the socket). This is a suggested
        # design in the project description to handle asynchronous notifications.
        self.output_queue: queue.Queue[str | None] = queue.Queue()
        self.observer = SocketObserver(self.output_queue)

        self.watched_ids: List[int] = []  # IDs of objects this session is watching.
        self.attached_ids: List[int] = [] # IDs of objects this session has interacted with.
        self.running = True

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
                self.client_socket.sendall(f"{msg}\n".encode('utf-8'))
            except (OSError, Exception):
                break # Stop if the socket is closed.

    def run(self) -> None:
        """Main loop for the client session. Handles command processing."""
        print(f"Accepted connection from {self.client_address}")

        # Start the background thread for sending notifications.
        agent = threading.Thread(target=self.notification_agent, daemon=True)
        agent.start()

        # Wrap the socket in a file-like object for convenient line-by-line reading.
        socket_file = self.client_socket.makefile('r', encoding='utf-8')

        try:
            welcome = {"type": "INFO", "message": "Connected to Sports Tracker (JSON Mode)"}
            self.client_socket.sendall(f"{json.dumps(welcome)}\n".encode('utf-8'))

            # Block and read commands line-by-line.
            for line in socket_file:
                line = line.strip()
                if not line:
                    continue

                try:
                    request = json.loads(line)
                    response = self.process_command(request)
                    if response:
                        self.client_socket.sendall(f"{json.dumps(response)}\n".encode('utf-8'))
                except json.JSONDecodeError:
                    err = {"status": "ERROR", "message": "Invalid JSON format"}
                    self.client_socket.sendall(f"{json.dumps(err)}\n".encode('utf-8'))

        except (ConnectionResetError, OSError):
            print(f"Connection lost from {self.client_address}")
        finally:
            # On disconnect, perform cleanup.
            self.running = False
            self.output_queue.put(None)  # Signal the notification agent to exit.
            self.cleanup()
            self.client_socket.close()
            print(f"Session closed for {self.client_address}")

    def process_command(self, req: Dict[str, Any]) -> Dict[str, Any]:
        """Parses the JSON request and executes the corresponding action."""
        cmd = req.get("command", "").upper()

        try:
            if cmd == "USER":
                self.user = req.get("username", "Anonymous")
                return {"status": "OK", "message": f"User set to {self.user}"}

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

                    from datetime import datetime
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
                    game = repository._objects.get(int(gid), {}).get('instance')
                    if isinstance(game, Game):
                        game.start() # This will trigger a notification to all watchers.
                        return {"status": "OK", "message": "Game started"}
                    return {"status": "ERROR", "message": "Not a game or game not found"}
                
            elif cmd == "PAUSE":
                gid = req.get("id")
                if gid is None: return {"status": "ERROR", "message": "Missing 'id'"}

                with repo_lock:
                    game = self.find_game(int(gid))
                    if game:
                        game.pause()
                        return {"status": "OK", "message": "Game paused"}
                    return {"status": "ERROR", "message": "Game not found"}

            elif cmd == "RESUME":
                gid = req.get("id")
                if gid is None: return {"status": "ERROR", "message": "Missing 'id'"}

                with repo_lock:
                    game = self.find_game(int(gid))
                    if game:
                        game.resume()
                        return {"status": "OK", "message": "Game resumed"}
                    return {"status": "ERROR", "message": "Game not found"}
            elif cmd == "SCORE":
                gid = req.get("id")
                pts = req.get("points")
                side = req.get("side", "").upper()
                if gid is None or pts is None or side not in ["HOME", "AWAY"]:
                    return {"status": "ERROR", "message": "Invalid params"}

                with repo_lock:
                    game = repository._objects.get(int(gid), {}).get('instance')
                    if isinstance(game, Game):
                        team_obj = game.home() if side == "HOME" else game.away()
                        game.score(int(pts), team_obj) # Triggers notification.
                        return {"status": "OK", "message": "Score updated"}
                    return {"status": "ERROR", "message": "Not a game or game not found"}

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
                        from datetime import timedelta
                        cup = Cup(
                            teams=teams,
                            type=c_type,
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
                    game = repository._objects.get(int(gid), {}).get('instance')
                    if isinstance(game, Game):
                        game.end()  # Transitions state to ENDED
                        return {"status": "OK", "message": "Game ended"}
                    return {"status": "ERROR", "message": "Not a game or game not found"}

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
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((HOST, PORT))
    server.listen()
    print(f"JSON Server listening on {HOST}:{PORT}...")

    try:
        # The main server loop. It does nothing but accept new connections
        # and hand them off to a new `Session` thread.
        while True:
            client_socket, client_address = server.accept()
            Session(client_socket, client_address).start()
    except KeyboardInterrupt:
        print("\nServer shutting down.")
    finally:
        # Ensure state is saved on shutdown.
        save_state()
        server.close()
