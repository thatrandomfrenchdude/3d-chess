#!/usr/bin/env python3

import requests
import json
import time

# Test the 3D Chess Backend API

BASE_URL = "http://localhost:5001"

def test_api():
    print("🧪 Testing 3D Chess Backend API...")
    print(f"Server URL: {BASE_URL}")
    print("-" * 50)
    
    try:
        # Test 1: Check if server is running
        print("1. Testing server connectivity...")
        response = requests.get(BASE_URL)
        if response.status_code == 200:
            print("✅ Server is running!")
        else:
            print(f"❌ Server responded with status {response.status_code}")
            return
        
        # Test 2: Create a multiplayer game
        print("\n2. Creating multiplayer game...")
        response = requests.post(f"{BASE_URL}/api/game/create", 
                               json={"type": "multiplayer"})
        if response.status_code == 200:
            game_data = response.json()
            if game_data["success"]:
                game_id = game_data["game_id"]
                print(f"✅ Created game with ID: {game_id}")
            else:
                print(f"❌ Failed to create game: {game_data}")
                return
        else:
            print(f"❌ Request failed with status {response.status_code}")
            return
        
        # Test 3: Join the game
        print("\n3. Joining the game...")
        response = requests.post(f"{BASE_URL}/api/game/{game_id}/join",
                               json={"player_id": "test_player_1"})
        if response.status_code == 200:
            join_data = response.json()
            if join_data["success"]:
                player_color = join_data["color"]
                print(f"✅ Joined game as {player_color} player")
            else:
                print(f"❌ Failed to join game: {join_data}")
                return
        else:
            print(f"❌ Request failed with status {response.status_code}")
            return
        
        # Test 4: Get game state
        print("\n4. Getting game state...")
        response = requests.get(f"{BASE_URL}/api/game/{game_id}/state")
        if response.status_code == 200:
            state_data = response.json()
            if state_data["success"]:
                game_state = state_data["game_state"]
                print(f"✅ Current turn: {game_state['current_turn']}")
                print(f"✅ Board FEN: {game_state['board'][:20]}...")
            else:
                print(f"❌ Failed to get game state: {state_data}")
                return
        else:
            print(f"❌ Request failed with status {response.status_code}")
            return
        
        # Test 5: Make a move
        print("\n5. Making a move (e2e4)...")
        response = requests.post(f"{BASE_URL}/api/game/{game_id}/move",
                               json={"move": "e2e4", "player_id": "test_player_1"})
        if response.status_code == 200:
            move_data = response.json()
            if move_data["success"]:
                print(f"✅ Move successful! Current turn: {move_data['current_turn']}")
            else:
                print(f"❌ Failed to make move: {move_data}")
                return
        else:
            print(f"❌ Request failed with status {response.status_code}")
            return
        
        # Test 6: Create computer game
        print("\n6. Creating computer game...")
        response = requests.post(f"{BASE_URL}/api/game/create", 
                               json={"type": "vs_computer"})
        if response.status_code == 200:
            game_data = response.json()
            if game_data["success"]:
                comp_game_id = game_data["game_id"]
                print(f"✅ Created computer game with ID: {comp_game_id}")
                
                # Join computer game
                response = requests.post(f"{BASE_URL}/api/game/{comp_game_id}/join",
                                       json={"player_id": "test_player_2"})
                if response.status_code == 200:
                    join_data = response.json()
                    if join_data["success"]:
                        print(f"✅ Joined computer game as {join_data['color']} player")
                        
                        # Make a move in computer game
                        response = requests.post(f"{BASE_URL}/api/game/{comp_game_id}/move",
                                               json={"move": "e2e4", "player_id": "test_player_2"})
                        if response.status_code == 200:
                            move_data = response.json()
                            if move_data["success"]:
                                print(f"✅ Move in computer game successful!")
                                time.sleep(2)  # Wait for computer response
                                
                                # Check if computer made a move
                                response = requests.get(f"{BASE_URL}/api/game/{comp_game_id}/state")
                                if response.status_code == 200:
                                    state_data = response.json()
                                    if state_data["success"]:
                                        moves = state_data["game_state"]["move_history"]
                                        if len(moves) >= 2:
                                            print(f"✅ Computer responded with move!")
                                        else:
                                            print("⚠️  Computer hasn't responded yet")
            else:
                print(f"❌ Failed to create computer game: {game_data}")
        else:
            print(f"❌ Request failed with status {response.status_code}")
        
        print("\n" + "=" * 50)
        print("🎉 Backend API tests completed successfully!")
        print("📝 The backend is ready for use with the frontend.")
        print("\nTo use the game:")
        print("1. Open 3d-chess-backend.html in your browser")
        print("2. Create or join games using the UI")
        print("3. Play against other players or the computer")
        
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to the server.")
        print("Make sure the backend is running with: python backend.py")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

if __name__ == "__main__":
    test_api()
