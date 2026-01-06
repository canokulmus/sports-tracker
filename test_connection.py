#!/usr/bin/env python3
"""Quick test script to verify WebSocket server is working"""

import asyncio
import json
from websockets.sync.client import connect

def test_connection():
    print("Connecting to WebSocket server...")

    try:
        with connect("ws://localhost:8888") as websocket:
            print("✅ Connected!")

            # Receive welcome message
            welcome = websocket.recv()
            print(f"Welcome: {welcome}")

            # Test GET_TEAMS command
            print("\n📤 Sending GET_TEAMS command...")
            websocket.send(json.dumps({"command": "GET_TEAMS"}))
            response = websocket.recv()
            data = json.loads(response)
            print(f"📥 Response: {json.dumps(data, indent=2)}")

            # Test CREATE_TEAM command
            print("\n📤 Creating a test team...")
            websocket.send(json.dumps({"command": "CREATE_TEAM", "name": "Test Team"}))
            response = websocket.recv()
            data = json.loads(response)
            print(f"📥 Response: {json.dumps(data, indent=2)}")

            # Verify team was created
            print("\n📤 Fetching teams again...")
            websocket.send(json.dumps({"command": "GET_TEAMS"}))
            response = websocket.recv()
            data = json.loads(response)
            print(f"📥 Response: {json.dumps(data, indent=2)}")

            print("\n✅ All tests passed!")

    except Exception as e:
        print(f"❌ Error: {e}")
        return False

    return True

if __name__ == "__main__":
    success = test_connection()
    exit(0 if success else 1)
