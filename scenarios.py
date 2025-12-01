import socket
import threading
import time
import json
import sys

HOST = '127.0.0.1'
PORT = 8888


class TestClient(threading.Thread):
    def __init__(self, name, actions):
        super().__init__()
        self.name = name
        self.actions = actions
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.running = True
        self.notifications = []

    def run(self):
        try:
            self.sock.connect((HOST, PORT))
            # REMOVED: self.sock.readline() which caused the error.
            # The welcome message will be handled by the listen thread instead.
            print(f"[{self.name}] Connected.")

            # Background listener for notifications
            listener = threading.Thread(target=self.listen, daemon=True)
            listener.start()

            for action in self.actions:
                if "wait" in action:
                    print(f"[{self.name}] Sleeping {action['wait']}s...")
                    time.sleep(action['wait'])
                    continue

                payload = action['payload']
                print(f"[{self.name}] >> {payload['command']}")
                msg = json.dumps(payload) + "\n"
                self.sock.sendall(msg.encode('utf-8'))
                time.sleep(0.2)  # Small delay to ensure order

            # Stay alive briefly to catch final notifications
            time.sleep(2)
            self.running = False
            try:
                self.sock.shutdown(socket.SHUT_RDWR)
            except:
                pass
            self.sock.close()

        except Exception as e:
            print(f"[{self.name}] Error: {e}")

    def listen(self):
        # We create a file-like object here to safely use readline()
        sock_file = self.sock.makefile('r', encoding='utf-8')
        while self.running:
            try:
                line = sock_file.readline()
                if not line: break
                data = json.loads(line)

                if data.get("type") == "NOTIFICATION":
                    print(f"   🔔 [{self.name}] NOTIFIED: Game {data.get('game_id')} state={data.get('state')}")
                elif data.get("type") == "INFO":
                    # This handles the welcome message
                    print(f"   ℹ️ [{self.name}] INFO: {data.get('message')}")
                elif data.get("status") == "OK" and "id" in data:
                    print(f"   ✅ [{self.name}] Result ID: {data['id']}")
                elif data.get("status") == "ERROR":
                    print(f"   ❌ [{self.name}] Error: {data['message']}")
            except ValueError:
                continue  # Ignore parse errors
            except Exception:
                break


# --- SCENARIO 1: CONCURRENCY (The "Most Important" Requirement) ---
def run_concurrency_scenario():
    print("\n" + "=" * 50)
    print("SCENARIO 1: CONCURRENCY & OBSERVERS")
    print("Testing: 2 Watchers, 1 Updater interacting simultaneously.")
    print("=" * 50 + "\n")

    # 1. Admin creates a game
    admin_actions = [
        {"payload": {"command": "USER", "username": "Admin"}},
        {"payload": {"command": "CREATE_TEAM", "name": "Team A"}},  # ID 1
        {"payload": {"command": "CREATE_TEAM", "name": "Team B"}},  # ID 2
        {"payload": {"command": "CREATE_GAME", "home_id": 1, "away_id": 2}}  # ID 3
    ]

    # 2. Watcher 1 (Alice)
    alice_actions = [
        {"payload": {"command": "USER", "username": "Alice"}},
        {"wait": 2},  # Wait for creation
        {"payload": {"command": "WATCH", "id": 3}},
        {"wait": 5}  # Just listen
    ]

    # 3. Watcher 2 (Bob)
    bob_actions = [
        {"payload": {"command": "USER", "username": "Bob"}},
        {"wait": 2},
        {"payload": {"command": "WATCH", "id": 3}},
        {"wait": 5}
    ]

    # 4. Updater (Charlie)
    charlie_actions = [
        {"payload": {"command": "USER", "username": "Charlie"}},
        {"wait": 3},
        {"payload": {"command": "START", "id": 3}},
        {"payload": {"command": "SCORE", "id": 3, "points": 2, "side": "HOME"}},
        {"payload": {"command": "SCORE", "id": 3, "points": 3, "side": "AWAY"}},
    ]

    # Run threads
    t_admin = TestClient("Admin", admin_actions)
    t_alice = TestClient("Alice", alice_actions)
    t_bob = TestClient("Bob", bob_actions)
    t_charlie = TestClient("Charlie", charlie_actions)

    t_admin.start();
    t_admin.join()  # Let admin finish setup
    t_alice.start();
    t_bob.start();
    t_charlie.start()
    t_alice.join();
    t_bob.join();
    t_charlie.join()


# --- SCENARIO 2: LEAGUE TOURNAMENT ---
def run_league_scenario():
    print("\n" + "=" * 50)
    print("SCENARIO 2: LEAGUE CUP")
    print("Testing: Create League, Play Game, Check Standings")
    print("=" * 50 + "\n")

    actions = [
        {"payload": {"command": "USER", "username": "LeagueAdmin"}},
        # Create 3 Teams
        {"payload": {"command": "CREATE_TEAM", "name": "L-Team 1"}},  # ID 4
        {"payload": {"command": "CREATE_TEAM", "name": "L-Team 2"}},  # ID 5
        {"payload": {"command": "CREATE_TEAM", "name": "L-Team 3"}},  # ID 6
        # Create Cup (IDs 4,5,6)
        {"payload": {"command": "CREATE_CUP", "cup_type": "LEAGUE", "team_ids": [4, 5, 6]}},  # Cup ID 7
        # Note: Cup generation creates Games. We assume Game IDs continue incrementing.
        # If Game ID 3 was last, Cup probably created Games 4, 5, 6.
        # Let's try to update one.
        {"payload": {"command": "WATCH", "id": 7}},  # Watch the Cup? (If implemented)
        {"payload": {"command": "GET_STANDINGS", "id": 7}}
    ]

    t = TestClient("LeagueAdmin", actions)
    t.start();
    t.join()


# --- SCENARIO 3: ELIMINATION TOURNAMENT ---
def run_elimination_scenario():
    print("\n" + "=" * 50)
    print("SCENARIO 3: ELIMINATION CUP")
    print("Testing: Bracket logic over TCP")
    print("=" * 50 + "\n")

    actions = [
        {"payload": {"command": "USER", "username": "ElimAdmin"}},
        # Create 4 Teams for Semis
        {"payload": {"command": "CREATE_TEAM", "name": "E-Team 1"}},  # 8
        {"payload": {"command": "CREATE_TEAM", "name": "E-Team 2"}},  # 9
        {"payload": {"command": "CREATE_TEAM", "name": "E-Team 3"}},  # 10
        {"payload": {"command": "CREATE_TEAM", "name": "E-Team 4"}},  # 11
        # Create Cup
        {"payload": {"command": "CREATE_CUP", "cup_type": "ELIMINATION", "team_ids": [8, 9, 10, 11]}},  # Cup ID 12
        {"payload": {"command": "GET_STANDINGS", "id": 12}}
    ]

    t = TestClient("ElimAdmin", actions)
    t.start();
    t.join()


if __name__ == "__main__":
    run_concurrency_scenario()
    time.sleep(1)
    run_league_scenario()
    time.sleep(1)
    run_elimination_scenario()
