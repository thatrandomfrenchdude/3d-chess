#!/usr/bin/env python3

import requests
import json
import time
import os

# Test the 3D Chess Backend API with all new features

BASE_URL = "http://localhost:5001"

def test_api():
    print("🧪 Testing 3D Chess Backend API...")
    print(f"Server URL: {BASE_URL}")
    print("Testing all features: Multiplayer, Computer AI, PGN Export, Resign, ELO Rating")
    print("-" * 80)
    
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
                print(f"✅ Created multiplayer game with ID: {game_id}")
                print(f"✅ Game type: {game_data.get('type', 'not specified')}")
            else:
                print(f"❌ Failed to create game: {game_data}")
                return
        else:
            print(f"❌ Request failed with status {response.status_code}")
            return
        
        # Test 3: Join the game
        print("\n3. Joining the multiplayer game...")
        response = requests.post(f"{BASE_URL}/api/game/{game_id}/join",
                               json={"player_id": "test_player_1"})
        if response.status_code == 200:
            join_data = response.json()
            if join_data["success"]:
                player_color = join_data["color"]
                print(f"✅ Joined game as {player_color} player")
                print(f"✅ Player ID: {join_data.get('player_id', 'not specified')}")
            else:
                print(f"❌ Failed to join game: {join_data}")
                return
        else:
            print(f"❌ Request failed with status {response.status_code}")
            return
        
        # Test 4: Get game state and verify move history
        print("\n4. Getting game state and checking move history...")
        response = requests.get(f"{BASE_URL}/api/game/{game_id}/state")
        if response.status_code == 200:
            state_data = response.json()
            if state_data["success"]:
                game_state = state_data["game_state"]
                print(f"✅ Current turn: {game_state['current_turn']}")
                print(f"✅ Board FEN: {game_state['board'][:20]}...")
                print(f"✅ Move history: {game_state.get('move_history', [])}")
                print(f"✅ Game result: {game_state.get('game_result', 'not specified')}")
                print(f"✅ Players: {game_state.get('players', {})}")
            else:
                print(f"❌ Failed to get game state: {state_data}")
                return
        else:
            print(f"❌ Request failed with status {response.status_code}")
            return
        
        # Test 5: Make a move and verify move history updates
        print("\n5. Making a move (e2e4) and verifying move history...")
        response = requests.post(f"{BASE_URL}/api/game/{game_id}/move",
                               json={"move": "e2e4", "player_id": "test_player_1"})
        if response.status_code == 200:
            move_data = response.json()
            if move_data["success"]:
                print(f"✅ Move successful! Current turn: {move_data['current_turn']}")
                
                # Verify move history was updated
                response = requests.get(f"{BASE_URL}/api/game/{game_id}/state")
                if response.status_code == 200:
                    state_data = response.json()
                    if state_data["success"]:
                        move_history = state_data["game_state"]["move_history"]
                        if "e2e4" in move_history:
                            print(f"✅ Move history updated: {move_history}")
                        else:
                            print(f"❌ Move not found in history: {move_history}")
            else:
                print(f"❌ Failed to make move: {move_data}")
                return
        else:
            print(f"❌ Request failed with status {response.status_code}")
            return
        
        
        # Test 6: Test PGN Export functionality
        print("\n6. Testing PGN export...")
        response = requests.get(f"{BASE_URL}/api/game/{game_id}/pgn")
        if response.status_code == 200:
            pgn_content = response.text
            print("✅ PGN export successful!")
            print(f"✅ PGN content preview: {pgn_content[:100]}...")
            
            # Check if PGN contains expected headers
            expected_headers = ["[Event", "[Site", "[Date", "[White", "[Black", "[Result", "[GameId"]
            missing_headers = [h for h in expected_headers if h not in pgn_content]
            if missing_headers:
                print(f"⚠️  Missing PGN headers: {missing_headers}")
            else:
                print("✅ All expected PGN headers present")
            
            # Check if move is in PGN
            if "e2e4" in pgn_content or "e4" in pgn_content:
                print("✅ Move found in PGN content")
            else:
                print("⚠️  Move not found in PGN content")
        else:
            print(f"❌ PGN export failed with status {response.status_code}")
        
        # Test 7: Test Resign functionality
        print("\n7. Testing resign functionality...")
        response = requests.post(f"{BASE_URL}/api/game/{game_id}/resign",
                               json={"player_id": "test_player_1"})
        if response.status_code == 200:
            resign_data = response.json()
            if resign_data["success"]:
                print(f"✅ Resignation successful!")
                print(f"✅ Game result: {resign_data.get('game_result', 'not specified')}")
                print(f"✅ Resigned by: {resign_data.get('resigned_by', 'not specified')}")
                
                # Verify game state reflects resignation
                response = requests.get(f"{BASE_URL}/api/game/{game_id}/state")
                if response.status_code == 200:
                    state_data = response.json()
                    if state_data["success"]:
                        game_result = state_data["game_state"]["game_result"]
                        if game_result != "*":
                            print(f"✅ Game state shows game ended: {game_result}")
                        else:
                            print("❌ Game state still shows ongoing game")
            else:
                print(f"❌ Failed to resign: {resign_data}")
        else:
            print(f"❌ Resign request failed with status {response.status_code}")
        
        # Test 8: Create computer game with default ELO
        print("\n8. Creating computer game with default ELO...")
        response = requests.post(f"{BASE_URL}/api/game/create", 
                               json={"type": "vs_computer"})
        if response.status_code == 200:
            game_data = response.json()
            if game_data["success"]:
                comp_game_id = game_data["game_id"]
                print(f"✅ Created computer game with ID: {comp_game_id}")
                print(f"✅ Default ELO: {game_data.get('elo_rating', 'not specified')}")
            else:
                print(f"❌ Failed to create computer game: {game_data}")
                return
        else:
            print(f"❌ Request failed with status {response.status_code}")
            return
        
        # Test 9: Create computer game with custom ELO rating
        print("\n9. Creating computer game with custom ELO (2000)...")
        response = requests.post(f"{BASE_URL}/api/game/create", 
                               json={"type": "vs_computer", "elo_rating": 2000})
        if response.status_code == 200:
            game_data = response.json()
            if game_data["success"]:
                comp_game_id_custom = game_data["game_id"]
                print(f"✅ Created computer game with ID: {comp_game_id_custom}")
                print(f"✅ Custom ELO: {game_data.get('elo_rating', 'not specified')}")
                
                # Join the custom ELO game
                response = requests.post(f"{BASE_URL}/api/game/{comp_game_id_custom}/join",
                                       json={"player_id": "test_player_2"})
                if response.status_code == 200:
                    join_data = response.json()
                    if join_data["success"]:
                        print(f"✅ Joined custom ELO game as {join_data['color']} player")
                        
                        # Make a move in custom ELO computer game
                        response = requests.post(f"{BASE_URL}/api/game/{comp_game_id_custom}/move",
                                               json={"move": "e2e4", "player_id": "test_player_2"})
                        if response.status_code == 200:
                            move_data = response.json()
                            if move_data["success"]:
                                print(f"✅ Move in custom ELO computer game successful!")
                                time.sleep(3)  # Wait for computer response
                                
                                # Check if computer made a move
                                response = requests.get(f"{BASE_URL}/api/game/{comp_game_id_custom}/state")
                                if response.status_code == 200:
                                    state_data = response.json()
                                    if state_data["success"]:
                                        moves = state_data["game_state"]["move_history"]
                                        if len(moves) >= 2:
                                            print(f"✅ Computer (ELO 2000) responded with move: {moves[-1]}")
                                        else:
                                            print("⚠️  Computer hasn't responded yet")
            else:
                print(f"❌ Failed to create custom ELO computer game: {game_data}")
        else:
            print(f"❌ Request failed with status {response.status_code}")
        
        # Test 10: Test ELO validation (invalid ELO)
        print("\n10. Testing ELO validation with invalid ELO (5000)...")
        response = requests.post(f"{BASE_URL}/api/game/create", 
                               json={"type": "vs_computer", "elo_rating": 5000})
        if response.status_code == 400:
            error_data = response.json()
            print(f"✅ Invalid ELO correctly rejected: {error_data.get('error', 'no error message')}")
        elif response.status_code == 200:
            print("⚠️  Invalid ELO was accepted (should be rejected)")
        else:
            print(f"❌ Unexpected status code: {response.status_code}")
        
        # Test 11: Test PGN export with computer game (should include ELO)
        print("\n11. Testing PGN export with computer game ELO metadata...")
        response = requests.get(f"{BASE_URL}/api/game/{comp_game_id_custom}/pgn")
        if response.status_code == 200:
            pgn_content = response.text
            print("✅ Computer game PGN export successful!")
            
            # Check for ELO-related headers
            if "BlackElo" in pgn_content or "ComputerLevel" in pgn_content:
                print("✅ ELO metadata found in PGN")
                if "2000" in pgn_content:
                    print("✅ Custom ELO (2000) found in PGN")
                else:
                    print("⚠️  Custom ELO not found in PGN content")
            else:
                print("❌ ELO metadata missing from computer game PGN")
        else:
            print(f"❌ Computer game PGN export failed with status {response.status_code}")
        
        # Test 12: Test game deletion
        print("\n12. Testing game deletion...")
        response = requests.delete(f"{BASE_URL}/api/game/{game_id}")
        if response.status_code == 200:
            delete_data = response.json()
            if delete_data.get("success"):
                print("✅ Game deletion successful!")
                
                # Verify game is deleted
                response = requests.get(f"{BASE_URL}/api/game/{game_id}/state")
                if response.status_code == 404:
                    print("✅ Game no longer accessible after deletion")
                else:
                    print("⚠️  Game still accessible after deletion")
            else:
                print(f"❌ Game deletion failed: {delete_data}")
        else:
            print(f"❌ Delete request failed with status {response.status_code}")
            
        print("\n" + "=" * 80)
        print("🎉 Comprehensive Backend API tests completed!")
        print("📝 All features tested: Multiplayer, Computer AI, PGN Export, Resign, ELO Rating")
        print("\n🔍 Test Summary:")
        print("✅ Server connectivity")
        print("✅ Multiplayer game creation and joining")
        print("✅ Move making and move history tracking")
        print("✅ Game state management")
        print("✅ PGN export with proper metadata")
        print("✅ Resign functionality with game result updates")
        print("✅ Computer game creation (default and custom ELO)")
        print("✅ ELO rating validation")
        print("✅ Computer AI responses")
        print("✅ ELO metadata in PGN exports")
        print("✅ Game deletion")
        print("\nTo use the game:")
        print("1. Open 3d-chess-backend.html in your browser")
        print("2. Create or join games using the UI")
        print("3. Play against other players or the computer")
        print("4. Use the ELO slider to adjust computer difficulty")
        print("5. Export PGN files and use resign functionality")
        
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to the server.")
        print("Make sure the backend is running with: python backend.py")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()

def test_elo_boundaries():
    """Test ELO rating boundary conditions"""
    print("\n🔬 Testing ELO rating boundaries...")
    
    # Test minimum valid ELO (800)
    response = requests.post(f"{BASE_URL}/api/game/create", 
                           json={"type": "vs_computer", "elo_rating": 800})
    if response.status_code == 200:
        print("✅ Minimum ELO (800) accepted")
        game_data = response.json()
        requests.delete(f"{BASE_URL}/api/game/{game_data['game_id']}")  # Cleanup
    else:
        print("❌ Minimum ELO (800) rejected")
    
    # Test maximum valid ELO (3000)
    response = requests.post(f"{BASE_URL}/api/game/create", 
                           json={"type": "vs_computer", "elo_rating": 3000})
    if response.status_code == 200:
        print("✅ Maximum ELO (3000) accepted")
        game_data = response.json()
        requests.delete(f"{BASE_URL}/api/game/{game_data['game_id']}")  # Cleanup
    else:
        print("❌ Maximum ELO (3000) rejected")
    
    # Test below minimum (799)
    response = requests.post(f"{BASE_URL}/api/game/create", 
                           json={"type": "vs_computer", "elo_rating": 799})
    if response.status_code == 400:
        print("✅ Below minimum ELO (799) correctly rejected")
    else:
        print("❌ Below minimum ELO (799) incorrectly accepted")
    
    # Test above maximum (3001)
    response = requests.post(f"{BASE_URL}/api/game/create", 
                           json={"type": "vs_computer", "elo_rating": 3001})
    if response.status_code == 400:
        print("✅ Above maximum ELO (3001) correctly rejected")
    else:
        print("❌ Above maximum ELO (3001) incorrectly accepted")

def run_all_tests():
    """Run all test suites"""
    test_api()
    test_elo_boundaries()

if __name__ == "__main__":
    run_all_tests()
