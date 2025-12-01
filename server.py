import socket
import sys
import threading
import pickle
import os
import queue
import json
from typing import Any, List, Dict, Tuple

# Import Phase 1 classes
from repo import Repo
from game import Game
from team import Team
from cup import Cup
from constants import GameState

# --- Configuration & Globals ---
HOST = ''
PORT = 8888
SAVE_FILE = 'server_state.pkl'

# Global Repository & Lock
repository = Repo()
repo_lock = threading.RLock()


class SocketObserver:
    """
    Observer that queues JSON messages.
    """

    def __init__(self, message_queue: queue.Queue):
        self.message_queue = message_queue

    def update(self, game: Any) -> None:
        try:
            # Construct a structured event payload
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
            # Serialize to JSON string
            self.message_queue.put(json.dumps(payload))
        except Exception as e:
            error_payload = {"type": "ERROR", "message": f"Notification failed: {str(e)}"}
            self.message_queue.put(json.dumps(error_payload))


class Session(threading.Thread):
    def __init__(self, client_socket: socket.socket, client_address: Tuple[str, int]):
        super().__init__()
        self.client_socket = client_socket
        self.client_address = client_address
        self.user = "Anonymous"

        self.output_queue: queue.Queue[str | None] = queue.Queue()
        self.observer = SocketObserver(self.output_queue)

        self.watched_ids: List[int] = []
        self.attached_ids: List[int] = []
        self.running = True

    def notification_agent(self) -> None:
        """Background thread to push JSON messages to the client."""
        while self.running:
            try:
                msg = self.output_queue.get()
                if msg is None:
                    break
                # Send with newline delimiter
                self.client_socket.sendall(f"{msg}\n".encode('utf-8'))
            except (OSError, Exception):
                break

    def run(self) -> None:
        print(f"Accepted connection from {self.client_address}")

        # Start notification agent
        agent = threading.Thread(target=self.notification_agent, daemon=True)
        agent.start()

        # Use a file-like object wrapper for easier line-by-line reading
        socket_file = self.client_socket.makefile('r', encoding='utf-8')

        try:
            # Send welcome message as JSON
            welcome = {"type": "INFO", "message": "Connected to Sports Tracker (JSON Mode)"}
            self.client_socket.sendall(f"{json.dumps(welcome)}\n".encode('utf-8'))

            while True:
                # Read line-by-line (blocking)
                line = socket_file.readline()
                if not line:
                    break  # EOF

                line = line.strip()
                if not line:
                    continue

                try:
                    request = json.loads(line)
                    response = self.process_command(request)
                    if response:
                        # Send response as JSON line
                        self.client_socket.sendall(f"{json.dumps(response)}\n".encode('utf-8'))
                except json.JSONDecodeError:
                    err = {"status": "ERROR", "message": "Invalid JSON format"}
                    self.client_socket.sendall(f"{json.dumps(err)}\n".encode('utf-8'))

        except (ConnectionResetError, OSError):
            print(f"Connection lost from {self.client_address}")
        finally:
            self.running = False
            self.output_queue.put(None)
            self.cleanup()
            self.client_socket.close()
            print(f"Session closed for {self.client_address}")

    def process_command(self, req: Dict[str, Any]) -> Dict[str, Any]:
        """
        Takes a dictionary (parsed JSON) and executes logic.
        Returns a dictionary to be sent back.
        """
        cmd = req.get("command", "").upper()

        try:
            if cmd == "USER":
                self.user = req.get("username", "Anonymous")
                return {"status": "OK", "message": f"User set to {self.user}"}

            elif cmd == "CREATE_TEAM":
                name = req.get("name")
                if not name: return {"status": "ERROR", "message": "Missing 'name'"}

                with repo_lock:
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

                    # Create with dummy time for now
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

                    repository.attach(oid, self.user)
                    if oid not in self.attached_ids:
                        self.attached_ids.append(oid)

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
                    gid = int(gid)
                    if gid not in repository._objects:
                        return {"status": "ERROR", "message": "Game not found"}
                    game = repository._objects[gid]['instance']
                    if isinstance(game, Game):
                        game.start()
                        return {"status": "OK", "message": "Game started"}
                    return {"status": "ERROR", "message": "Not a game"}

            elif cmd == "SCORE":
                gid = req.get("id")
                pts = req.get("points")
                side = req.get("side", "").upper()

                if gid is None or pts is None or side not in ["HOME", "AWAY"]:
                    return {"status": "ERROR", "message": "Invalid params"}

                with repo_lock:
                    gid = int(gid)
                    if gid not in repository._objects:
                        return {"status": "ERROR", "message": "Game not found"}
                    game = repository._objects[gid]['instance']
                    if isinstance(game, Game):
                        team_obj = game.home() if side == "HOME" else game.away()
                        # Phase 1 logic handles the update and notification
                        game.score(int(pts), team_obj)
                        return {"status": "OK", "message": "Score updated"}
                    return {"status": "ERROR", "message": "Not a game"}

            elif cmd == "SAVE":
                save_state()
                return {"status": "OK", "message": "State saved"}

            else:
                return {"status": "ERROR", "message": f"Unknown command: {cmd}"}

        except ValueError as e:
            return {"status": "ERROR", "message": f"Value Error: {str(e)}"}
        except Exception as e:
            return {"status": "ERROR", "message": f"Internal Error: {str(e)}"}

    def cleanup(self):
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
    global repository
    if os.path.exists(SAVE_FILE):
        try:
            with open(SAVE_FILE, 'rb') as f:
                repository = pickle.load(f)
            print("State loaded.")
        except:
            print("New repository started.")


def save_state():
    with repo_lock:
        with open(SAVE_FILE, 'wb') as f:
            pickle.dump(repository, f)
        print("State saved.")


if __name__ == "__main__":
    load_state()
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((HOST, PORT))
    server.listen()
    print(f"JSON Server listening on {PORT}...")
    try:
        while True:
            c, a = server.accept()
            Session(c, a).start()
    except KeyboardInterrupt:
        pass
    finally:
        save_state()
        server.close()
