import socket
import threading
import sys
import json
import os

# Configuration
HOST = '127.0.0.1'
PORT = 8888


def receive_loop(sock, stop_event):
    """
    Reads newline-delimited JSON from the server and prints it nicely.
    """
    # Create a file-like wrapper for easy readline()
    sock_file = sock.makefile('r', encoding='utf-8')

    while not stop_event.is_set():
        try:
            # readline is blocking, but socket timeout or shutdown will break it
            line = sock_file.readline()
            if not line:
                print("\n[!] Server closed connection.")
                stop_event.set()
                os._exit(0)  # Force exit main thread input

            try:
                data = json.loads(line)

                # --- PRETTY PRINTING ---
                # Clear current input line to show message cleanly
                sys.stdout.write("\r" + " " * 50 + "\r")

                if data.get("type") == "NOTIFICATION":
                    # It's a game update!
                    print(f"🔔 [GAME {data['game_id']}] UPDATE")
                    print(f"   {data['home']} vs {data['away']}")
                    print(f"   State: {data['state']} | Score: {data['score']['home']} - {data['score']['away']}")
                elif data.get("status") == "ERROR":
                    print(f"❌ Error: {data['message']}")
                elif data.get("status") == "OK":
                    print(f"✅ {data.get('message', 'Success')}")
                    if "id" in data:
                        print(f"   -> Object ID: {data['id']}")
                else:
                    # Generic print for other messages (like welcome)
                    print(f"📥 {json.dumps(data, indent=2)}")

                # Restore prompt
                sys.stdout.write("> ")
                sys.stdout.flush()

            except json.JSONDecodeError:
                print(f"\n[!] raw: {line.strip()}")

        except (OSError, ValueError):
            break


def parse_input_to_json(text):
    """
    Maps simple user text to the JSON protocol structure.
    """
    parts = text.strip().split()
    if not parts: return None

    cmd = parts[0].upper()
    args = parts[1:]

    payload = {"command": cmd}

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

    elif cmd == "CREATE_GAME":
        if len(args) < 2:
            print("Usage: CREATE_GAME <home_id> <away_id>")
            return None
        payload["home_id"] = args[0]
        payload["away_id"] = args[1]

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

    elif cmd == "SCORE":
        if len(args) < 3:
            print("Usage: SCORE <id> <points> <HOME/AWAY>")
            return None
        payload["id"] = args[0]
        payload["points"] = args[1]
        payload["side"] = args[2]

    elif cmd == "SAVE":
        pass  # No args needed

    else:
        # Pass through unknown commands just in case
        pass

    return payload


def main():
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        client.connect((HOST, PORT))
    except ConnectionRefusedError:
        print(f"Could not connect to {HOST}:{PORT}")
        return

    stop_event = threading.Event()

    # Start receiver thread
    t = threading.Thread(target=receive_loop, args=(client, stop_event), daemon=True)
    t.start()

    print("Commands: USER, CREATE_TEAM, CREATE_GAME, WATCH, START, SCORE, SAVE")

    try:
        while not stop_event.is_set():
            user_input = input("> ")
            if user_input.lower() in ["exit", "quit"]:
                break

            payload = parse_input_to_json(user_input)
            if payload:
                # Send as NDJSON line
                msg = json.dumps(payload) + "\n"
                client.sendall(msg.encode('utf-8'))

    except KeyboardInterrupt:
        print("\nExiting...")
    finally:
        stop_event.set()
        client.close()


if __name__ == "__main__":
    main()