#!/bin/bash

# Docker Test Runner for 3D Chess Backend
# This script helps run various tests for the Docker implementation

set -e

echo "🐳 3D Chess Docker Test Runner"
echo "=============================="

# Function to check if Docker and Docker Compose are available
check_docker() {
    if ! command -v docker &> /dev/null; then
        echo "❌ Docker is not installed or not in PATH"
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        echo "❌ Docker Compose is not installed or not in PATH"
        exit 1
    fi
    
    echo "✅ Docker and Docker Compose are available"
}

# Function to build the Docker image
build_image() {
    echo "🔨 Building Docker image..."
    docker-compose build
    echo "✅ Docker image built successfully"
}

# Function to run the chess backend
start_backend() {
    echo "🚀 Starting chess backend..."
    docker-compose up -d chess-backend
    echo "✅ Chess backend started"
    echo "📍 Access the game at: http://localhost:1111"
}

# Function to stop the backend
stop_backend() {
    echo "🛑 Stopping chess backend..."
    docker-compose down
    echo "✅ Chess backend stopped"
}

# Function to run internal container tests
run_container_tests() {
    echo "🧪 Running tests inside Docker container..."
    
    # Make sure the backend is running first
    echo "📋 Checking if backend is running..."
    if ! docker-compose ps chess-backend | grep -q "Up"; then
        echo "⚠️  Backend not running, starting it first..."
        start_backend
        echo "⏳ Waiting for backend to be ready..."
        sleep 5
    fi
    
    # Run the test service
    docker-compose --profile test run --rm chess-test
    
    echo "✅ Container tests completed"
}

# Function to run external tests (from host)
run_external_tests() {
    echo "🌐 Running external tests from host..."
    
    # Make sure the backend is running first
    if ! docker-compose ps chess-backend | grep -q "Up"; then
        echo "⚠️  Backend not running, starting it first..."
        start_backend
        echo "⏳ Waiting for backend to be ready..."
        sleep 5
    fi
    
    # Create a temporary test file for external testing
    cat > test_external_temp.py << 'EOF'
#!/usr/bin/env python3
import requests
import time

def test_external_access():
    print("🌐 Testing external access to Docker container...")
    BASE_URL = "http://localhost:1111"
    
    try:
        # Test basic connectivity
        response = requests.get(BASE_URL, timeout=10)
        if response.status_code == 200:
            print("✅ External access works!")
            
            # Test resign endpoint specifically (the bug we fixed)
            print("🧪 Testing resign functionality from external host...")
            
            # Create a game first
            create_response = requests.post(f"{BASE_URL}/api/game/create", 
                                          json={"type": "multiplayer"}, 
                                          timeout=10)
            
            if create_response.status_code == 200:
                game_data = create_response.json()
                if game_data.get('success'):
                    game_id = game_data.get('game_id')
                    
                    # Join the game to get player_id
                    join_response = requests.post(f"{BASE_URL}/api/game/{game_id}/join", 
                                                json={}, timeout=10)
                    if join_response.status_code == 200:
                        join_data = join_response.json()
                        player_id = join_data.get('player_id')
                        
                        # Test resign functionality
                        resign_response = requests.post(f"{BASE_URL}/api/game/{game_id}/resign",
                                                      json={"player_id": player_id},
                                                      timeout=10)
                        
                        if resign_response.status_code == 200:
                            resign_data = resign_response.json()
                            if resign_data.get('success'):
                                print("✅ Resign functionality works from external host!")
                                print("🎉 Bug fix confirmed working!")
                                return True
                            else:
                                print(f"❌ Resign failed: {resign_data.get('error')}")
                        else:
                            print(f"❌ Resign request failed: {resign_response.status_code}")
                    else:
                        print(f"❌ Join game failed: {join_response.status_code}")
                else:
                    print(f"❌ Game creation failed: {game_data.get('error')}")
            else:
                print(f"❌ Game creation request failed: {create_response.status_code}")
        else:
            print(f"❌ Server returned status code: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ External test failed: {e}")
        return False
    
    return False

if __name__ == "__main__":
    success = test_external_access()
    exit(0 if success else 1)
EOF
    
    # Run the external test
    python3 test_external_temp.py
    
    # Clean up
    rm test_external_temp.py
    
    echo "✅ External tests completed"
}

# Function to show logs
show_logs() {
    echo "📋 Showing backend logs..."
    docker-compose logs chess-backend
}

# Function to show usage
show_usage() {
    echo "Usage: $0 [COMMAND]"
    echo ""
    echo "Commands:"
    echo "  build           Build the Docker image"
    echo "  start           Start the chess backend"
    echo "  stop            Stop the chess backend"
    echo "  test-container  Run tests inside the Docker container"
    echo "  test-external   Run tests from the host machine"
    echo "  test-all        Run both container and external tests"
    echo "  logs            Show backend logs"
    echo "  full-test       Build, start, and run all tests"
    echo "  help            Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 full-test    # Complete test cycle"
    echo "  $0 start        # Just start the backend"
    echo "  $0 test-all     # Run all tests"
}

# Main script logic
case "${1:-help}" in
    build)
        check_docker
        build_image
        ;;
    start)
        check_docker
        start_backend
        ;;
    stop)
        check_docker
        stop_backend
        ;;
    test-container)
        check_docker
        run_container_tests
        ;;
    test-external)
        check_docker
        run_external_tests
        ;;
    test-all)
        check_docker
        echo "🧪 Running comprehensive test suite..."
        run_container_tests
        echo ""
        run_external_tests
        echo ""
        echo "🎉 All tests completed!"
        ;;
    logs)
        check_docker
        show_logs
        ;;
    full-test)
        check_docker
        echo "🚀 Running full test cycle..."
        build_image
        echo ""
        start_backend
        echo ""
        echo "⏳ Waiting for services to be ready..."
        sleep 8
        echo ""
        run_container_tests
        echo ""
        run_external_tests
        echo ""
        echo "🎉 Full test cycle completed!"
        echo "📍 Backend is still running at: http://localhost:1111"
        echo "💡 Run '$0 stop' to stop the backend"
        ;;
    help|--help|-h)
        show_usage
        ;;
    *)
        echo "❌ Unknown command: $1"
        echo ""
        show_usage
        exit 1
        ;;
esac
