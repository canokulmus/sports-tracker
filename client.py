import socket
import threading
import sys
import os

# Configuration
HOST = '127.0.0.1'
PORT = 8888


def receive_messages(sock):
    """
    Background thread: Listens for incoming messages (responses/notifications).
    """
    while True:
        try:
            # 1. Block until data arrives (Buffer size 4096 is generous for text)
            data = sock.recv(4096)

            if not data:
                print("\n[!] Server disconnected.")
                # Force exit because the main thread is stuck in input()
                os._exit(0)

            # 2. Decode bytes to string
            message = data.decode('utf-8')

            # 3. Print cleanly
            # \r moves cursor to start of line to overwrite the user's prompt
            # We print the message, then restore the prompt "> "
            sys.stdout.write(f"\r{message}\n> ")
            sys.stdout.flush()

        except OSError:
            break


def send_command(sock, text):
    """
    Encapsulates sending logic.
    FUTURE TODO: Change this function to wrap 'text' in json.dumps() later.
    """
    if not text.strip():
        return

    try:
        # Currently: Raw text protocol
        sock.sendall(text.encode('utf-8'))

        # Future JSON Example:
        # import json
        # payload = json.dumps({"command": text.split()[0], "args": text.split()[1:]})
        # sock.sendall(payload.encode('utf-8'))

    except OSError:
        print("[!] Failed to send.")


def main():
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        print(f"Connecting to {HOST}:{PORT}...")
        client.connect((HOST, PORT))
    except ConnectionRefusedError:
        print("[!] Connection failed. Is server.py running?")
        return

    # Start the background listener thread
    listener = threading.Thread(target=receive_messages, args=(client,), daemon=True)
    listener.start()

    print("Connected. Type commands (e.g., USER Alice, WATCH 1). Type 'exit' to quit.")

    # Main Loop: Handle User Input
    try:
        while True:
            # blocking input
            msg = input("> ")

            if msg.lower() == 'exit':
                break

            send_command(client, msg)

    except KeyboardInterrupt:
        print("\nExiting...")
    finally:
        client.close()


if __name__ == "__main__":
    main()
