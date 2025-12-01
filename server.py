import socket
import sys
import threading
import pickle
import os
import queue
from typing import Any, List

# Import your library classes
from repo import Repo
from game import Game
from team import Team
from cup import Cup
from constants import GameState

# --- Global Shared State ---
# Initialize the repository.
# The load_state() function below will override this if a save file exists.
repository = Repo()

# Thread-safe lock for accessing the shared repository
# CRITICAL: Any time you read/write to 'repository', use 'with repo_lock:'
repo_lock = threading.RLock()

# Configuration
HOST = ''
PORT = 8888
SAVE_FILE = 'server_state.pkl'


class SocketObserver:
    """
    Bridge between the Phase 1 Observer pattern and the TCP socket.
    Instead of printing to stdout, it pushes messages to a thread-safe queue.
    """

    def __init__(self, message_queue: queue.Queue):
        self.message_queue = message_queue

    def update(self, game: Any) -> None:
        """
        Called by the Game object when state changes.
        """
        # TODO: Format the notification message nicely.
        # You might want to include a timestamp or specific event details.
        try:
            msg = f"NOTIFICATION Game {game.id()} ({game.home().team_name} vs {game.away().team_name}): State={game.state.name}, Score={game.home_score}-{game.away_score}\n"
            self.message_queue.put(msg)
        except Exception as e:
            # Fallback in case of error during string formatting
            self.message_queue.put(f"NOTIFICATION Error formatting update: {e}\n")


class Session(threading.Thread):
    """
    Handles a single client connection.
    Responsible for reading commands (Input) and managing the notification agent (Output).
    """

    def __init__(self, client_socket: socket.socket, client_address):
        super().__init__()
        self.client_socket = client_socket
        self.client_address = client_address
        self.user = "Polat Alemdar"  # Default until USER command is received

        # Queue for messages destined for this client (Notifications)
        self.output_queue = queue.Queue()

        # The observer instance specific to this session
        self.observer = SocketObserver(self.output_queue)

        # Track objects to clean up on disconnect
        self.watched_ids: List[int] = []
        self.attached_ids: List[int] = []

    def notification_agent(self):
        """
        Runs in a separate thread (or essentially concurrently).
        Blocks on the output_queue and sends messages to the socket whenever they appear.
        """
        while True:
            try:
                # Block until a message is available
                msg = self.output_queue.get()

                # Sentinel value to stop the thread gracefully
                if msg is None:
                    break

                # Send data to socket
                self.client_socket.sendall(msg.encode('utf-8'))

            except Exception as e:
                print(f"Error in notification agent for {self.client_address}: {e}")
                break

    def run(self):
        """
        Main loop for the session thread. Reads input from socket.
        """
        print(f"Connection from {self.client_address}")

        # Start the notification thread for this session
        notifier = threading.Thread(target=self.notification_agent, daemon=True)
        notifier.start()

        try:
            while True:
                # TODO: Implement robust buffering if you expect partial packets.
                # For this assignment, assuming commands fit in 1024 bytes is usually okay.
                data = self.client_socket.recv(1024)

                if not data:
                    break  # Client disconnected

                # Decode and strip whitespace
                command_str = data.decode('utf-8').strip()
                if not command_str:
                    continue

                # Process the command
                response = self.process_command(command_str)

                # Send the synchronous response (e.g., "OK", "ERROR")
                if response:
                    self.client_socket.sendall(response.encode('utf-8'))

        except ConnectionResetError:
            print(f"Connection reset by {self.client_address}")
        except Exception as e:
            print(f"Session error for {self.client_address}: {e}")
        finally:
            self.cleanup()
            # Stop the notifier thread
            self.output_queue.put(None)
            self.client_socket.close()
            print(f"Connection closed for {self.client_address}")

    def process_command(self, command_line: str) -> str:
        """
        Parses the command string and executes logic on the repository.
        Returns a response string to be sent back to the client.
        """
        parts = command_line.split()
        if not parts:
            return ""

        cmd = parts[0].upper()
        args = parts[1:]

        # CRITICAL: All access to 'repository' must be inside the lock!

        try:
            if cmd == "USER":
                if len(args) < 1: return "ERROR Usage: USER <username>\n"
                self.user = args[0]
                return f"OK Welcome {self.user}\n"

            # --- CREATION COMMANDS ---
            elif cmd == "CREATE_TEAM":
                # Example: CREATE_TEAM Galatasaray
                if len(args) < 1: return "ERROR Usage: CREATE_TEAM <name>\n"

                with repo_lock:
                    # TODO: Add logic to handle spaces in names if needed (e.g. joining args)
                    team_name = " ".join(args)
                    tid = repository.create(type="team", name=team_name)
                    # Automatically attach creator? Optional.
                    repository.attach(tid, self.user)
                    self.attached_ids.append(tid)

                return f"OK Team created with ID {tid}\n"

            elif cmd == "CREATE_GAME":
                # Example: CREATE_GAME 1 2 (HomeID AwayID)
                if len(args) < 2: return "ERROR Usage: CREATE_GAME <home_id> <away_id>\n"

                h_id, a_id = int(args[0]), int(args[1])

                with repo_lock:
                    # Retrieve Team objects first
                    home_data = repository._objects.get(h_id)
                    away_data = repository._objects.get(a_id)

                    if not home_data or not away_data:
                        return "ERROR Invalid Team IDs\n"

                    gid = repository.create(
                        type="game",
                        home=home_data['instance'],
                        away=away_data['instance'],
                        datetime=None  # TODO: Add datetime logic
                    )
                return f"OK Game created with ID {gid}\n"

            # --- INTERACTION COMMANDS ---
            elif cmd == "WATCH":
                # Example: WATCH 5
                if len(args) < 1: return "ERROR Usage: WATCH <id>\n"
                obj_id = int(args[0])

                with repo_lock:
                    if obj_id not in repository._objects:
                        return "ERROR Object not found\n"

                    # 1. Attach via Repo (lifecycle management)
                    repository.attach(obj_id, self.user)
                    if obj_id not in self.attached_ids:
                        self.attached_ids.append(obj_id)

                    # 2. Watch via Observer (notification management)
                    obj_instance = repository._objects[obj_id]['instance']
                    if hasattr(obj_instance, 'watch'):
                        obj_instance.watch(self.observer)
                        if obj_id not in self.watched_ids:
                            self.watched_ids.append(obj_id)
                        return f"OK Watching object {obj_id}\n"
                    else:
                        return "ERROR Object is not watchable (not a Game/Cup)\n"

            elif cmd == "START":
                # Example: START 5
                if len(args) < 1: return "ERROR Usage: START <game_id>\n"
                gid = int(args[0])

                with repo_lock:
                    if gid not in repository._objects:
                        return "ERROR Game not found\n"

                    game = repository._objects[gid]['instance']
                    if not isinstance(game, Game):
                        return "ERROR Object is not a game\n"

                    game.start()
                return "OK Game started\n"

            elif cmd == "SCORE":
                # Example: SCORE <game_id> <points> <Home/Away>
                # TODO: Implement parsing logic for this
                return "TODO: Implement SCORE command\n"

            elif cmd == "PAUSE":
                # TODO: Implement
                return "TODO: Implement PAUSE\n"

            # --- SYSTEM COMMANDS ---
            elif cmd == "SAVE":
                save_state()
                return "OK State saved\n"

            elif cmd == "HELP":
                return "INFO Available: USER, CREATE_TEAM, CREATE_GAME, WATCH, START, SCORE, SAVE\n"

            else:
                return f"ERROR Unknown command: {cmd}\n"

        except ValueError:
            return "ERROR Invalid arguments (check numbers)\n"
        except Exception as e:
            return f"ERROR Internal processing error: {e}\n"

    def cleanup(self):
        """
        Clean up resources: unwatch games, detach from repo objects.
        This is crucial for the reference counting in Repo.delete().
        """
        print(f"Cleaning up session resources for {self.user}...")

        with repo_lock:
            # 1. Unwatch objects (Observer pattern)
            for obj_id in self.watched_ids:
                try:
                    if obj_id in repository._objects:
                        instance = repository._objects[obj_id]['instance']
                        if hasattr(instance, 'unwatch'):
                            instance.unwatch(self.observer)
                except Exception as e:
                    print(f"Error unwatching {obj_id}: {e}")

            # 2. Detach objects (Repo pattern)
            for obj_id in self.attached_ids:
                try:
                    repository.detach(obj_id, self.user)
                except Exception as e:
                    print(f"Error detaching {obj_id}: {e}")


def load_state():
    """Loads the repository state from disk if it exists."""
    global repository
    if os.path.exists(SAVE_FILE):
        try:
            print(f"Loading state from {SAVE_FILE}...")
            with open(SAVE_FILE, 'rb') as f:
                repository = pickle.load(f)
            print("State loaded successfully.")
        except Exception as e:
            print(f"Failed to load state: {e}")
            print("Starting with a fresh repository.")


def save_state():
    """Saves the repository state to disk using pickle."""
    # Acquire lock to ensure we don't save while the state is being modified
    with repo_lock:
        try:
            print(f"Saving state to {SAVE_FILE}...")
            with open(SAVE_FILE, 'wb') as f:
                pickle.dump(repository, f)
            print("State saved successfully.")
        except Exception as e:
            print(f"Failed to save state: {e}")


def main():
    # Load previous state if available
    load_state()

    # Create server socket
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # Allow address reuse to avoid "Address already in use" errors on restart
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    # Optional: Get port from command line args
    port = int(sys.argv[1]) if len(sys.argv) > 1 else PORT

    try:
        server.bind((HOST, port))
        server.listen(10)  # Backlog of 10 connections
        print(f"Server listening on port {port}...")
        print("Press Ctrl+C to stop.")

        while True:
            # Accept new connections
            client_sock, addr = server.accept()

            # Start a new session thread for this client
            session = Session(client_sock, addr)
            session.start()

    except KeyboardInterrupt:
        print("\nServer stopping...")
    finally:
        save_state()
        server.close()


if __name__ == "__main__":
    main()