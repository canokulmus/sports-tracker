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

                # --- PRETTY PRINTING LOGIC ---
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
                else:
                    # Print any other JSON messages from the server.
                    print(f"📥 {json.dumps(data, indent=2)}")

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
        pass  # No arguments needed for SAVE.

    else:
        # Allow unrecognized commands to be sent, in case the server supports them.
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
    print("USER, CREATE_TEAM, CREATE_GAME, WATCH, START, SCORE, SAVE, exit")

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