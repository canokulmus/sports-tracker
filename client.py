import socket
import threading
import sys
import json
import os

# This client provides a simple command-line interface to the sports tracker server.
# It operates in two main threads:
# 1. The main thread, which reads user input and sends it to the server.
# 2. A receiver thread, which listens for and displays asynchronous messages
#    (like game notifications) from the server.

# Configuration
HOST = '127.0.0.1'
PORT = 8888


def receive_loop(sock, stop_event):
    """
    Listens for messages from the server in a dedicated thread.
    This is necessary to handle asynchronous notifications from the server
    without blocking the user's ability to type new commands.
    """
    # Wrap the socket in a file-like object for convenient line-by-line reading.
    # The server sends newline-delimited JSON (NDJSON).
    sock_file = sock.makefile('r', encoding='utf-8')

    while not stop_event.is_set():
        try:
            # Blocking call to read the next line from the server.
            line = sock_file.readline()
            if not line:
                print("\n[!] Server closed connection.")
                stop_event.set()
                os._exit(0)  # Force exit to unblock the main thread's input()

            try:
                data = json.loads(line)

                # Clear the current line to prevent mixing user input with server messages.
                sys.stdout.write("\r" + " " * 50 + "\r")

                if data.get("type") == "NOTIFICATION":
                    # A game update notification, as required by the project.
                    print(f"🔔 [GAME {data['game_id']}] UPDATE")
                    print(f"   {data['home']} vs {data['away']}")
                    print(f"   State: {data['state']} | Score: {data['score']['home']} - {data['score']['away']}")
                elif data.get("status") == "ERROR":
                    print(f"❌ Error: {data['message']}")
                elif data.get("status") == "OK":
                    print(f"✅ {data.get('message', 'Success')}")
                    if "id" in data:
                        print(f"   -> Object ID: {data['id']}")
                    if "game_ids" in data:
                        print(f"   -> Game IDs: {data['game_ids']}")
                        
                if "standings" in data:
                    standings = data['standings']
                    print(f"   -> Standings:")
                    
                    # if list (LEAGUE)
                    if isinstance(standings, list):
                        print(f"\n      {'Pos':<5} {'Team':<20} {'W':<4} {'D':<4} {'L':<4} {'GF':<5} {'GA':<5} {'Pts':<5}")
                        print(f"      {'-'*60}")
                        for i, row in enumerate(standings, 1):
                            team, won, draw, lost, gf, ga, pts = row
                            print(f"      {i:<5} {team:<20} {won:<4} {draw:<4} {lost:<4} {gf:<5} {ga:<5} {pts:<5}")
                    
                    # if dict (ELIMINATION/GROUP)
                    elif isinstance(standings, dict):
                        print(json.dumps(standings, indent=4))
                
                if "items" in data:
                    print("   -> Items:")
                    for item in data['items']:
                        print(f"      {item['id']}: {item['desc']}")

                if "teams" in data:
                    print("   -> Teams:")
                    for t in data['teams']:
                        print(f"      {t['id']}: {t['name']}")

                if "cups" in data:
                    print("   -> Cups:")
                    for c in data['cups']:
                        print(f"      {c['id']} ({c['type']}): {c['desc']}")

                if "games" in data:
                    print("   -> Games:")
                    for g in data['games']:
                        print(f"      {g['id']}: {g['home']} vs {g['away']} [{g['state']}] {g['score']['home']}-{g['score']['away']}")

                if "players" in data:
                    print("   -> Players:")
                    for p in data['players']:
                        print(f"      #{p['no']} {p['name']}")

                if "stats" in data:
                    print(json.dumps(data['stats'], indent=4))

                if "gametree" in data:
                    print(json.dumps(data['gametree'], indent=4))
                
                if "results" in data:
                    print("   -> Results:")
                    for r in data['results']:
                        print(f"      [{r['type']}] {r['id']}: {r['desc']}")

                # Restore the user input prompt.
                sys.stdout.write("> ")
                sys.stdout.flush()

            except json.JSONDecodeError:
                print(f"\n[!] Received non-JSON data: {line.strip()}")

        except (OSError, ValueError):
            # This can happen if the socket is closed while readline() is blocking.
            break


def parse_input_to_json(text):
    """
    Translates user-friendly shorthand commands into the server's JSON protocol.
    This simplifies the user experience, as they don't have to write full JSON.
    """
    parts = text.strip().split()
    if not parts: return None

    cmd = parts[0].upper()
    args = parts[1:]

    payload = {"command": cmd}

    # --- Command-to-JSON Mapping ---
    if cmd == "USER":
        if len(args) < 1:
            print("Usage: USER <name>")
            return None
        payload["username"] = args[0]

    elif cmd == "CREATE_TEAM":
        if len(args) < 1:
            print("Usage: CREATE_TEAM <name>")
            return None
        payload["name"] = " ".join(args)
    
    elif cmd == "UPDATE_TEAM":
        if len(args) < 2:
            print("Usage: UPDATE_TEAM <id> <key>=<value> ...")
            return None
        payload["id"] = args[0]
        for item in args[1:]:
            if "=" in item:
                k, v = item.split("=", 1)
                payload[k] = v

    elif cmd == "ADD_PLAYER":
        if len(args) < 3:
            print("Usage: ADD_PLAYER <team_id> <no> <name>")
            return None
        payload["team_id"] = args[0]
        payload["no"] = args[1]
        payload["name"] = " ".join(args[2:])

    elif cmd == "REMOVE_PLAYER":
        if len(args) < 2:
            print("Usage: REMOVE_PLAYER <team_id> <name>")
            return None
        payload["team_id"] = args[0]
        payload["name"] = " ".join(args[1:])

    elif cmd == "GET_PLAYERS":
        if len(args) < 1:
            print("Usage: GET_PLAYERS <team_id>")
            return None
        payload["team_id"] = args[0]

    elif cmd == "CREATE_GAME":
        if len(args) < 2:
            print("Usage: CREATE_GAME <home_id> <away_id>")
            return None
        payload["home_id"] = args[0]
        payload["away_id"] = args[1]
    
    elif cmd == "UPDATE_GAME":
        if len(args) < 2:
            print("Usage: UPDATE_GAME <id> <key>=<value> ...")
            return None
        payload["id"] = args[0]
        for item in args[1:]:
            if "=" in item:
                k, v = item.split("=", 1)
                payload[k] = v

    elif cmd == "GET_GAME_STATS":
        if len(args) < 1:
            print("Usage: GET_GAME_STATS <id>")
            return None
        payload["id"] = args[0]

    elif cmd == "CREATE_CUP":
        if len(args) < 3:
            print("Usage: CREATE_CUP <type> <team_id1> <team_id2> ...")
            print("Types: LEAGUE, ELIMINATION, GROUP")
            return None
        payload["cup_type"] = args[0].upper()
        # Takes all remaining arguments as team IDs
        payload["team_ids"] = args[1:]

    elif cmd == "WATCH":
        if len(args) < 1:
            print("Usage: WATCH <id>")
            return None
        payload["id"] = args[0]

    elif cmd == "START":
        if len(args) < 1:
            print("Usage: START <id>")
            return None
        payload["id"] = args[0]

    elif cmd == "PAUSE":
        if len(args) < 1:
            print("Usage: PAUSE <id>")
            return None
        payload["id"] = args[0]

    elif cmd == "RESUME":
        if len(args) < 1:
            print("Usage: RESUME <id>")
            return None
        payload["id"] = args[0]

    elif cmd == "END":
        if len(args) < 1:
            print("Usage: END <id>")
            return None
        payload["id"] = args[0]

    elif cmd == "SCORE":
        if len(args) < 3:
            print("Usage: SCORE <id> <points> <HOME/AWAY> [player_name]")
            return None
        payload["id"] = args[0]
        payload["points"] = args[1]
        payload["side"] = args[2].upper()
        if len(args) > 3:
            payload["player"] = " ".join(args[3:])

    elif cmd == "GET_STANDINGS":
        if len(args) < 1:
            print("Usage: GET_STANDINGS <cup_id>")
            return None
        payload["id"] = args[0]

    elif cmd == "GET_CUP_GAMES":
        if len(args) < 1:
            print("Usage: GET_CUP_GAMES <cup_id>")
            return None
        payload["id"] = args[0]

    elif cmd == "GET_GAMETREE":
        if len(args) < 1:
            print("Usage: GET_GAMETREE <cup_id>")
            return None
        payload["id"] = args[0]

    elif cmd == "GENERATE_PLAYOFFS":
        if len(args) < 1:
            print("Usage: GENERATE_PLAYOFFS <cup_id>")
            return None
        payload["id"] = args[0]

    elif cmd == "LIST":
        pass

    elif cmd == "LIST_ATTACHED":
        pass

    elif cmd == "ATTACH":
        if len(args) < 1:
            print("Usage: ATTACH <id>")
            return None
        payload["id"] = args[0]

    elif cmd == "DETACH":
        if len(args) < 1:
            print("Usage: DETACH <id>")
            return None
        payload["id"] = args[0]

    elif cmd == "DELETE":
        if len(args) < 1:
            print("Usage: DELETE <id>")
            return None
        payload["id"] = args[0]

    elif cmd == "SEARCH":
        if len(args) < 1:
            print("Usage: SEARCH <query>")
            return None
        payload["query"] = " ".join(args)

    elif cmd == "GET_TEAMS":
        pass

    elif cmd == "GET_CUPS":
        pass

    elif cmd == "GET_GAMES":
        pass

    elif cmd == "SAVE":
        pass  # No arguments needed for SAVE.

    else:
        # Allow unrecognized commands to be sent raw, or handled by server defaults
        pass

    return payload


def main():
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        client.connect((HOST, PORT))
    except ConnectionRefusedError:
        print(f"Could not connect to server at {HOST}:{PORT}. Is it running?")
        return

    # Use an Event to signal the receiver thread to stop gracefully.
    stop_event = threading.Event()

    # Start the receiver thread. It's a daemon so it won't block program exit.
    t = threading.Thread(target=receive_loop, args=(client, stop_event), daemon=True)
    t.start()

    print("Connected to Sports Tracker. Available commands:")
    print("  USER <name>")
    print("  CREATE_TEAM <name>")
    print("  UPDATE_TEAM <id> <key>=<value> ...")
    print("  ADD_PLAYER <team_id> <no> <name>")
    print("  REMOVE_PLAYER <team_id> <name>")
    print("  GET_PLAYERS <team_id>")
    print("  CREATE_GAME <home_id> <away_id>")
    print("  UPDATE_GAME <id> <key>=<value> ...")
    print("  GET_GAME_STATS <id>")
    print("  CREATE_CUP <type> <id1> <id2> ...")
    print("  WATCH <id>")
    print("  START <id>")
    print("  SCORE <id> <points> <HOME/AWAY> [player]")
    print("  PAUSE <id>")
    print("  RESUME <id>")
    print("  END <id>")
    print("  GET_STANDINGS <cup_id>")
    print("  GET_GAMETREE <cup_id>")
    print("  GET_CUP_GAMES <cup_id>")
    print("  GENERATE_PLAYOFFS <cup_id>")
    print("  LIST")
    print("  LIST_ATTACHED")
    print("  ATTACH <id>")
    print("  DETACH <id>")
    print("  DELETE <id>")
    print("  SEARCH <query>")
    print("  GET_TEAMS / GET_CUPS / GET_GAMES")
    print("  SAVE")
    print("  exit")

    try:
        # Main thread loop for handling user input.
        while not stop_event.is_set():
            user_input = input("> ")
            if user_input.lower() in ["exit", "quit"]:
                break

            # Convert input to JSON and send to server.
            payload = parse_input_to_json(user_input)
            if payload:
                # Append a newline to adhere to the NDJSON protocol.
                msg = json.dumps(payload) + "\n"
                client.sendall(msg.encode('utf-8'))

    except KeyboardInterrupt:
        print("\nExiting...")
    finally:
        # Cleanly shut down the connection and threads.
        stop_event.set()
        client.close()


if __name__ == "__main__":
    main()