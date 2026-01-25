#!/usr/bin/env python3
"""
Test client for the Merlin API - helps test the API without running the full DM service.
"""

import json
import uuid
import requests
from typing import Optional


class MerlinAPIClient:
    """Simple client for testing the Merlin API."""
    
    def __init__(self, api_base_url: str, game_id: str):
        self.api_base_url = api_base_url.rstrip('/')
        self.game_id = game_id
    
    def get_messages(self, start: Optional[int] = None, end: Optional[int] = None):
        """Get messages from the game."""
        url = f"{self.api_base_url}/api/v1/{self.game_id}/messages"
        params = {}
        if start is not None:
            params['start'] = start
        if end is not None:
            params['end'] = end
        
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json()
    
    def post_player_message(self, text: str, player_id: int = 1):
        """Post a player message."""
        url = f"{self.api_base_url}/api/v1/{self.game_id}/messages"
        
        payload = {
            "id": str(uuid.uuid4()),
            "user": {
                "id": player_id,
                "type": "player"
            },
            "effect": {
                "text": text
            }
        }
        
        response = requests.post(url, json=payload)
        response.raise_for_status()
        return response.json()
    
    def post_dm_message(self, text: str):
        """Post a DM message."""
        url = f"{self.api_base_url}/api/v1/{self.game_id}/messages"
        
        payload = {
            "id": str(uuid.uuid4()),
            "user": {
                "id": 0,
                "type": "dm"
            },
            "effect": {
                "text": text
            }
        }
        
        response = requests.post(url, json=payload)
        response.raise_for_status()
        return response.json()


def main():
    """Interactive test client."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Merlin API Test Client")
    parser.add_argument("--api-url", required=True, help="Base URL of the Merlin API")
    parser.add_argument("--game-id", default="test_game_001", help="Game ID")
    
    args = parser.parse_args()
    
    client = MerlinAPIClient(args.api_url, args.game_id)
    
    print(f"Merlin API Test Client")
    print(f"API: {args.api_url}")
    print(f"Game: {args.game_id}")
    print()
    print("Commands:")
    print("  get             - Get all messages")
    print("  get [start]     - Get messages after seq number")
    print("  player [text]   - Post a player message")
    print("  dm [text]       - Post a DM message")
    print("  quit            - Exit")
    print()
    
    while True:
        try:
            cmd = input("> ").strip()
            
            if not cmd or cmd == "quit":
                break
            
            parts = cmd.split(maxsplit=1)
            action = parts[0].lower()
            
            if action == "get":
                start = int(parts[1]) if len(parts) > 1 else None
                result = client.get_messages(start=start)
                print(json.dumps(result, indent=2))
            
            elif action == "player":
                if len(parts) < 2:
                    print("Usage: player <message text>")
                    continue
                text = parts[1]
                result = client.post_player_message(text)
                print(f"Posted player message: {text}")
                print(json.dumps(result, indent=2))
            
            elif action == "dm":
                if len(parts) < 2:
                    print("Usage: dm <message text>")
                    continue
                text = parts[1]
                result = client.post_dm_message(text)
                print(f"Posted DM message: {text}")
                print(json.dumps(result, indent=2))
            
            else:
                print(f"Unknown command: {action}")
        
        except KeyboardInterrupt:
            print("\nExiting...")
            break
        except Exception as e:
            print(f"Error: {e}")


if __name__ == "__main__":
    main()
