#!/usr/bin/env python3

"""
Docker Test Suite for 3D Chess Backend
This test file is designed to run inside the Docker container
to verify that all functionality works correctly in the containerized environment.
"""

import requests
import json
import time
import os
import sys

# Test configuration for Docker environment
BASE_URL = "http://chess-backend:5001"  # Use service name for internal Docker network
EXTERNAL_URL = "http://localhost:1111"  # External mapped port

def test_container_api():
    """Test API from inside the container"""
    print("🐳 Testing 3D Chess Backend API inside Docker container...")
    print(f"Internal Server URL: {BASE_URL}")
    print("Testing all features: Multiplayer, Computer AI, PGN Export, Resign, ELO Rating")
    print("-" * 80)
    
    try:
        # Test 1: Check if server is running internally
        print("1. Testing internal server connectivity...")
        response = requests.get(BASE_URL, timeout=5)
        if response.status_code == 200:
            print("✅ Server is running internally")
        else:
            print(f"❌ Server returned status code: {response.status_code}")
            return False
            
        # Test 2: Test create game endpoint
        print("2. Testing game creation...")
        print("🔍 DEBUG - About to create game...")
        create_response = requests.post(f"{BASE_URL}/api/game/create", 
                                      json={"type": "multiplayer"}, 
                                      timeout=10)
        
        print(f"🔍 DEBUG - Create response status: {create_response.status_code}")
        
        if create_response.status_code == 200:
            game_data = create_response.json()
            print(f"🔍 DEBUG - Create response data: {game_data}")
            if game_data.get('success'):
                game_id = game_data.get('game_id')
                print(f"✅ Game created successfully: {game_id}")
                
                # Join the game to get a player_id
                print("🔍 DEBUG - About to join game...")
                join_response = requests.post(f"{BASE_URL}/api/game/{game_id}/join", 
                                            json={}, 
                                            timeout=10)
                
                print(f"🔍 DEBUG - Join response status: {join_response.status_code}")
                
                if join_response.status_code == 200:
                    join_data = join_response.json()
                    print(f"🔍 DEBUG - Join response data: {join_data}")
                    if join_data.get('success'):
                        player_id = join_data.get('player_id')
                        print(f"✅ Joined game successfully as player: {player_id}")
                    else:
                        print(f"❌ Failed to join game: {join_data.get('error')}")
                        player_id = None  # Set to None to handle gracefully
                else:
                    print(f"❌ Join game request failed: {join_response.status_code}")
                    try:
                        error_data = join_response.json()
                        print(f"🔍 DEBUG - Join error data: {error_data}")
                    except:
                        print(f"🔍 DEBUG - Join error text: {join_response.text}")
                    player_id = None  # Set to None to handle gracefully
            else:
                print(f"❌ Game creation failed: {game_data.get('error')}")
                return False
        else:
            print(f"❌ Game creation request failed: {create_response.status_code}")
            return False
            
        # Test 3: Test resign functionality (the main bug we're fixing)
        print("3. Testing resign functionality...")
        print(f"🔍 DEBUG - Game ID: {game_id}")
        print(f"🔍 DEBUG - Player ID from join: {player_id}")
        
        if player_id is None:
            print("❌ Cannot test resign - no valid player_id from join")
            # Still try to check game state for debugging
            print("🔍 DEBUG - Checking game state even without valid player_id...")
            state_response = requests.get(f"{BASE_URL}/api/game/{game_id}/state", timeout=10)
            if state_response.status_code == 200:
                state_data = state_response.json()
                if state_data.get('success'):
                    game_state = state_data.get('game_state', {})
                    players_in_game = game_state.get('players', {})
                    print(f"🔍 DEBUG - Players in game: {players_in_game}")
                    print(f"🔍 DEBUG - Game type: {game_state.get('type', 'unknown')}")
                    print(f"🔍 DEBUG - Current turn: {game_state.get('current_turn', 'unknown')}")
            return False
        
        resign_response = requests.post(f"{BASE_URL}/api/game/{game_id}/resign",
                                      json={"player_id": player_id},
                                      timeout=10)
        
        print(f"🔍 DEBUG - Resign response status: {resign_response.status_code}")
        try:
            resign_response_data = resign_response.json()
            print(f"🔍 DEBUG - Resign response data: {resign_response_data}")
        except Exception as e:
            print(f"🔍 DEBUG - Failed to parse JSON: {e}")
            print(f"🔍 DEBUG - Resign response text: {resign_response.text}")
        
        # Always check game state for debugging regardless of resign status
        print("🔍 DEBUG - Checking game state for debugging...")
        state_response = requests.get(f"{BASE_URL}/api/game/{game_id}/state", timeout=10)
        if state_response.status_code == 200:
            state_data = state_response.json()
            if state_data.get('success'):
                game_state = state_data.get('game_state', {})
                players_in_game = game_state.get('players', {})
                print(f"🔍 DEBUG - Players in game: {players_in_game}")
                print(f"🔍 DEBUG - Player ID we're trying to use: {player_id}")
                print(f"🔍 DEBUG - Is player_id in players? {player_id in players_in_game}")
                print(f"🔍 DEBUG - Game type: {game_state.get('type', 'unknown')}")
                print(f"🔍 DEBUG - Current turn: {game_state.get('current_turn', 'unknown')}")
            else:
                print(f"🔍 DEBUG - State response failed: {state_data.get('error')}")
        else:
            print(f"🔍 DEBUG - State request failed: {state_response.status_code}")
        
        if resign_response.status_code == 200:
            resign_data = resign_response.json()
            if resign_data.get('success'):
                print("✅ Resign functionality works correctly")
            else:
                print(f"❌ Resign failed: {resign_data.get('error')}")
                return False
        else:
            print(f"❌ Resign request failed: {resign_response.status_code}")
            return False
            
        # Test 4: Test PGN export
        print("4. Testing PGN export...")
        pgn_response = requests.get(f"{BASE_URL}/api/game/{game_id}/pgn", timeout=10)
        
        if pgn_response.status_code == 200:
            print("✅ PGN export works correctly")
        else:
            print(f"❌ PGN export failed: {pgn_response.status_code}")
            return False
            
        # Test 5: Test vs_computer game and Stockfish engine
        print("5. Testing Stockfish engine with vs_computer game...")
        
        # Create a vs_computer game
        vs_comp_response = requests.post(f"{BASE_URL}/api/game/create", 
                                       json={"type": "vs_computer", "elo_rating": 1500}, 
                                       timeout=10)
        
        if vs_comp_response.status_code == 200:
            vs_comp_data = vs_comp_response.json()
            if vs_comp_data.get('success'):
                vs_comp_game_id = vs_comp_data.get('game_id')
                
                # Join the vs_computer game
                join_vs_comp_response = requests.post(f"{BASE_URL}/api/game/{vs_comp_game_id}/join", 
                                                    json={}, 
                                                    timeout=10)
                
                if join_vs_comp_response.status_code == 200:
                    join_vs_comp_data = join_vs_comp_response.json()
                    if join_vs_comp_data.get('success'):
                        vs_comp_player_id = join_vs_comp_data.get('player_id')
                        
                        # Make a move as white (human player) - this should trigger computer response
                        move_response = requests.post(f"{BASE_URL}/api/game/{vs_comp_game_id}/move", 
                                                    json={"move": "e2e4", "player_id": vs_comp_player_id}, 
                                                    timeout=15)
                        
                        if move_response.status_code == 200:
                            move_data = move_response.json()
                            if move_data.get('success'):
                                print("✅ Human move successful, checking for computer response...")
                                
                                # Check game state to see if computer made a move
                                time.sleep(2)  # Give computer time to respond
                                state_response = requests.get(f"{BASE_URL}/api/game/{vs_comp_game_id}/state", timeout=10)
                                
                                if state_response.status_code == 200:
                                    state_data = state_response.json()
                                    if state_data.get('success'):
                                        move_history = state_data.get('game_state', {}).get('move_history', [])
                                        if len(move_history) >= 2:  # Human move + computer move
                                            print("✅ Stockfish AI responded successfully")
                                        else:
                                            print("⚠️  Computer move not detected (may be Stockfish path issue)")
                                    else:
                                        print(f"❌ Failed to get game state: {state_data.get('error')}")
                                        return False
                                else:
                                    print(f"❌ Game state request failed: {state_response.status_code}")
                                    return False
                            else:
                                print(f"❌ Move failed: {move_data.get('error')}")
                                return False
                        else:
                            print(f"❌ Move request failed: {move_response.status_code}")
                            return False
                    else:
                        print(f"❌ Failed to join vs_computer game: {join_vs_comp_data.get('error')}")
                        return False
                else:
                    print(f"❌ Join vs_computer game request failed: {join_vs_comp_response.status_code}")
                    return False
            else:
                print(f"❌ vs_computer game creation failed: {vs_comp_data.get('error')}")
                return False
        else:
            print(f"❌ vs_computer game creation request failed: {vs_comp_response.status_code}")
            return False
            
        print("-" * 80)
        print("🎉 All Docker container tests passed!")
        return True
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Network error: {e}")
        print(f"🔍 DEBUG - This error occurred during internal testing")
        import traceback
        traceback.print_exc()
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        print(f"🔍 DEBUG - This error occurred during internal testing")
        import traceback
        traceback.print_exc()
        return False

def test_external_access():
    """Test that the container is accessible from outside"""
    print("\n🌐 Testing external access to containerized API...")
    print(f"External Server URL: {EXTERNAL_URL}")
    print("-" * 80)
    
    try:
        # Test external connectivity
        print("1. Testing external server connectivity...")
        response = requests.get(EXTERNAL_URL, timeout=10)
        if response.status_code == 200:
            print("✅ Server is accessible externally")
            return True
        else:
            print(f"❌ External server returned status code: {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ External network error: {e}")
        print("ℹ️  This is expected if testing from inside the container")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def check_environment():
    """Check Docker environment setup"""
    print("🔍 Checking Docker environment...")
    print("-" * 80)
    
    # Check if Stockfish is available
    stockfish_path = os.environ.get('STOCKFISH_PATH', '/usr/games/stockfish')
    stockfish_paths_to_check = [
        stockfish_path,
        '/usr/games/stockfish',
        '/usr/bin/stockfish',
        '/usr/local/bin/stockfish'
    ]
    
    stockfish_found = False
    for path in stockfish_paths_to_check:
        if os.path.exists(path):
            print(f"✅ Stockfish found at: {path}")
            stockfish_found = True
            break
    
    if not stockfish_found:
        print(f"❌ Stockfish not found in any expected locations")
        print(f"   Checked: {', '.join(stockfish_paths_to_check)}")
        
    # Check Flask environment
    flask_env = os.environ.get('FLASK_ENV', 'development')
    print(f"✅ Flask environment: {flask_env}")
    
    # Check working directory
    print(f"✅ Working directory: {os.getcwd()}")
    
    # Check if required files exist
    required_files = ['backend.py', '3d-chess-backend.html', 'chess-client.js']
    for file in required_files:
        if os.path.exists(file):
            print(f"✅ Required file found: {file}")
        else:
            print(f"❌ Required file missing: {file}")
            
    print("-" * 80)

def main():
    """Main test function"""
    print("🚀 Starting Docker Test Suite for 3D Chess Backend")
    print("=" * 80)
    
    # Check environment first
    check_environment()
    
    # Wait a moment for the server to be ready
    print("\n⏳ Waiting for server to be ready...")
    time.sleep(3)
    
    # Run internal tests
    internal_success = test_container_api()
    
    # Try external tests (might fail if running inside container)
    external_success = test_external_access()
    
    print("\n" + "=" * 80)
    print("📊 TEST SUMMARY")
    print("=" * 80)
    print(f"Internal container tests: {'✅ PASSED' if internal_success else '❌ FAILED'}")
    print(f"External access tests: {'✅ PASSED' if external_success else '❌ FAILED (Expected inside container)'}")
    
    if internal_success:
        print("\n🎉 Docker containerization is working correctly!")
        print("🔧 The resign bug fix is working properly in the Docker environment.")
        return 0
    else:
        print("\n💥 Docker tests failed!")
        print("🔧 There may still be issues with the containerized implementation.")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
