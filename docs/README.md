# 3D Mountain Chess

A comprehensive 3D chess game with multiplayer support, computer AI using Stockfish, and full containerization support. Features a unique mountain-peak design with elevation levels, real-time gameplay, and extensive game management capabilities.

## 📖 Table of Contents
- [Project Structure](#-project-structure)
- [Quick Start Options](#-quick-start-options)
- [How to Play](#-how-to-play)
- [Testing](#-testing)
- [API Documentation](#-api-documentation)
- [Docker Deployment](#docker-deployment)
- [Configuration](#configuration)
- [Development](#development)
- [Troubleshooting](#troubleshooting)
- [License](#license)

## 📁 Project Structure

```
3d-chess/
├── backend.py              # Flask backend server with WebSocket support
├── chess-client.js         # JavaScript client library
├── 3d-chess-backend.html   # Main game interface with backend integration
├── 3d-chess.html          # Original standalone version
├── requirements.txt       # Python dependencies
├── setup.sh              # Setup script for virtual environment
├── Dockerfile             # Container configuration
├── docker-compose.yml     # Docker orchestration
├── .dockerignore          # Docker build optimization
├── test_backend.py        # Backend unit tests
├── test_docker.py         # Docker integration tests
├── test_docker.sh         # Docker test automation script
├── games/                 # Directory for PGN exports
└── README.md             # This comprehensive documentation
```

## 🚀 Quick Start Options

### Option 1: Docker (Recommended)

The fastest way to get started:

```bash
# Build and run the application
docker-compose up --build

# Access the game at http://localhost:1111
```

### Option 2: Virtual Environment

For development or custom configurations:

```bash
# Automated setup
chmod +x setup.sh
./setup.sh

# Manual setup
python3 -m venv chess_env
source chess_env/bin/activate
pip install -r requirements.txt

# Install Stockfish (macOS)
brew install stockfish

# Start the server
python backend.py
```

The server will start on `http://localhost:5001`

## 🎮 How to Play

### Getting Started
Open your browser and navigate to:
- **Docker**: `http://localhost:1111`
- **Virtual Environment**: `http://localhost:5001`

### Game Modes

#### Single Player (vs Computer)
1. Click "Play vs Computer"
2. Select ELO difficulty (800-3000):
   - 800-999: Beginner
   - 1000-1299: Novice  
   - 1300-1699: Intermediate
   - 1700-2199: Advanced
   - 2200-2699: Expert
   - 2700-3000: Master
3. Click "Start Game"
4. You play as white, computer responds as black

#### Multiplayer
1. **Player 1**: Click "Create Multiplayer Game"
2. Share the Game ID with another player
3. **Player 2**: In a new window, enter the Game ID and click "Join Game"
4. Take turns making moves in real-time

### Move Controls
- **Move Notation**: Use algebraic notation (e.g., `e2e4`, `g1f3`, `e7e8q`)
- **Move History**: View all moves in the right panel with auto-scroll
- **Resign**: Click the red "Resign" button with confirmation
- **Export PGN**: Save your game in standard chess notation format

## 🧪 Testing

The project includes comprehensive testing suites for different deployment scenarios:

### Running All Tests

#### Virtual Environment Tests
```bash
# Activate virtual environment
source chess_env/bin/activate

# Run backend unit tests
python -m pytest test_backend.py -v

# Run individual test modules
python test_backend.py
```

#### Docker Tests
```bash
# Automated Docker testing (recommended)
chmod +x test_docker.sh
./test_docker.sh

# Manual Docker testing
python test_docker.py
```

### Test Coverage

#### Backend Unit Tests (`test_backend.py`)
- ✅ Game creation and initialization
- ✅ Move validation and execution
- ✅ Computer opponent integration
- ✅ PGN export functionality
- ✅ Resign game functionality
- ✅ ELO rating system
- ✅ WebSocket communication
- ✅ API endpoint responses
- ✅ Error handling and edge cases

#### Docker Integration Tests (`test_docker.py`)
- ✅ Container startup and health checks
- ✅ Network connectivity and port mapping
- ✅ Stockfish engine availability in container
- ✅ WebSocket connections through Docker
- ✅ Game creation and move execution in containerized environment
- ✅ PGN export and file persistence
- ✅ Volume mounting for game storage

#### Test Automation (`test_docker.sh`)
- ✅ Automated container lifecycle management
- ✅ Service health verification
- ✅ Cleanup after test completion
- ✅ Exit code reporting for CI/CD integration

## 🔧 API Documentation

### REST API Endpoints

#### Game Management
- `POST /api/game/create` - Create a new game
  ```json
  {
    "game_type": "single|multiplayer",
    "elo_rating": 1500  // Optional, for computer games (800-3000)
  }
  ```
- `POST /api/game/{game_id}/join` - Join an existing game
- `GET /api/game/{game_id}/state` - Get current game state
- `DELETE /api/game/{game_id}` - Delete a game

#### Game Actions
- `POST /api/game/{game_id}/move` - Make a move
  ```json
  {
    "move": "e2e4",  // Algebraic notation
    "player": "white|black"
  }
  ```
- `POST /api/game/{game_id}/resign` - Resign from game
- `GET /api/game/{game_id}/pgn` - Export game in PGN format

### WebSocket Events

#### Client → Server
- `join_game` - Join a game room for real-time updates
- `make_move` - Make a move in real-time
- `resign_game` - Resign from the game

#### Server → Client
- `move_made` - Receive move updates
- `game_update` - Receive game state updates
- `game_ended` - Game finished notification
- `error` - Error messages and validation failures

## 🐳 Docker Deployment

### Container Specifications
- **Base Image**: python:3.11-slim
- **Stockfish Version**: 15.1 (installed via apt-get)
- **Port Mapping**: External 1111 → Internal 5001
- **Volume**: `./games:/app/games` for PGN persistence
- **Network**: Custom bridge network `chess-network`

### Docker Commands

#### Development
```bash
# Build and run with logs
docker-compose up --build

# Run in detached mode
docker-compose up -d

# View logs
docker-compose logs -f chess-backend

# Stop services
docker-compose down
```

#### Production
```bash
# Build for production
docker build -t 3d-chess .

# Run with custom configuration
docker run -p 1111:5001 -v $(pwd)/games:/app/games 3d-chess
```

## ⚙️ Configuration

### Stockfish Configuration
The backend automatically detects Stockfish in the following order:
1. Environment variable `STOCKFISH_PATH`
2. `/opt/homebrew/bin/stockfish` (macOS Homebrew on Apple Silicon)
3. `/usr/local/bin/stockfish` (macOS Homebrew on Intel)
4. `/usr/bin/stockfish` (Standard Linux path)
5. `/usr/games/stockfish` (Debian/Ubuntu games path - Docker default)
6. `stockfish` (Assumes in PATH)

### Server Settings
- **Default Port**: 5001 (Virtual Env) / 1111 (Docker)
- **CORS**: Enabled for all origins
- **Debug Mode**: Enabled (disable for production)
- **WebSocket Transport**: Auto-fallback from WebSocket to polling

## 🛠️ Development

### Local Development Setup
```bash
# Clone repository
git clone https://github.com/thatrandomfrenchdude/3d-chess.git
cd 3d-chess

# Setup virtual environment
python3 -m venv chess_env
source chess_env/bin/activate

# Install dependencies
pip install -r requirements.txt

# Install Stockfish
brew install stockfish  # macOS
sudo apt-get install stockfish  # Ubuntu/Debian

# Run development server
python backend.py
```

### Development vs Production

#### Local Development
```bash
source chess_env/bin/activate
python backend.py
# Access at http://localhost:5001
```

#### Docker Development
```bash
docker-compose up --build
# Access at http://localhost:1111
```

## 🔍 Troubleshooting

### Common Issues

#### Connection Issues
- **Symptom**: Cannot connect to game server
- **Solutions**:
  - Ensure the backend server is running on the correct port
  - Check browser console for WebSocket connection errors
  - Verify CORS settings if hosting on different domains
  - For Docker: Ensure port 1111 is not in use by another service

#### Stockfish Issues
- **Symptom**: Computer opponent not working
- **Solutions**:
  - Install Stockfish: `brew install stockfish` (macOS) or `sudo apt-get install stockfish` (Linux)
  - Verify installation: Run `stockfish` in terminal
  - Check path configuration in `backend.py`
  - For Docker: Restart container to ensure Stockfish is properly installed

#### Move Issues
- **Symptom**: Moves not registering or being rejected
- **Solutions**:
  - Use proper algebraic notation (e.g., `e2e4`, not `E2-E4`)
  - Ensure it's your turn before making a move
  - Check that the move is legal in the current position
  - Verify piece positions on the 3D board match the game state

#### Docker Issues
- **Symptom**: Container won't start or crashes
- **Solutions**:
  ```bash
  # Check container logs
  docker-compose logs chess-backend
  
  # Restart with fresh build
  docker-compose down
  docker-compose up --build
  
  # Check if port is in use
  lsof -i :1111
  ```

#### PGN Export Issues
- **Symptom**: PGN files not downloading or saving
- **Solutions**:
  - Ensure the `games/` directory exists and is writable
  - Check browser's download settings
  - For Docker: Verify volume mounting is working correctly
  - Try playing a few moves before exporting

#### Virtual Environment Issues
- **Symptom**: Dependencies not found or import errors
- **Solutions**:
  ```bash
  # Recreate virtual environment
  rm -rf chess_env
  python3 -m venv chess_env
  source chess_env/bin/activate
  pip install -r requirements.txt
  ```

### Performance Optimization

#### For Development
- Use local virtual environment for faster iteration
- Enable Flask debug mode for hot reloading
- Use browser developer tools to debug JavaScript issues

#### For Production
- Use Gunicorn or uWSGI instead of Flask development server
- Add nginx reverse proxy for static file serving
- Configure proper logging levels
- Set up monitoring and health checks
- Use Docker with resource limits

### Debugging Tips

#### Backend Debugging
```bash
# Enable verbose logging
export FLASK_ENV=development
python backend.py

# Test API endpoints directly
curl http://localhost:5001/api/game/create -X POST -H "Content-Type: application/json" -d '{"game_type": "single"}'
```

#### Frontend Debugging
- Open browser developer console (F12)
- Check Network tab for failed API requests
- Monitor WebSocket connections in the Network tab
- Use console.log statements in JavaScript for debugging

#### Docker Debugging
```bash
# Access container shell
docker-compose exec chess-backend /bin/bash

# Check Stockfish in container
docker-compose exec chess-backend /usr/games/stockfish --help

# Monitor container resources
docker stats
```

## 📄 License

This project is open source and available under the MIT License. Read the [LICENSE](LICENSE) file for more information.
