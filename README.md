# 3D Mountain Chess

A beautiful 3D chess game with multiplayer support and computer AI using Stockfish.

## Features

- 🏔️ **3D Mountain Board**: Unique mountain-peak design with elevation levels
- 👥 **Multiplayer**: Play against other players in real-time
- 🤖 **AI Opponent**: Play against Stockfish computer AI
- ⚡ **Real-time Updates**: WebSocket-based real-time game updates
- 🎨 **Beautiful Graphics**: Soft gradient background and 3D pieces
- 📱 **Responsive**: Works on desktop browsers

## Backend Components

### Files Created
- `backend.py` - Flask server with WebSocket support
- `chess-client.js` - JavaScript client library for frontend
- `3d-chess-backend.html` - Updated HTML with backend integration
- `requirements.txt` - Python dependencies
- `setup.sh` - Setup script for easy installation

## Quick Start

### 1. Setup Backend

```bash
# Make setup script executable and run it
chmod +x setup.sh
./setup.sh
```

Or manually:

```bash
# Create virtual environment
python3 -m venv chess_env
source chess_env/bin/activate

# Install dependencies
pip install -r requirements.txt

# Install Stockfish (macOS)
brew install stockfish
```

### 2. Start the Server

```bash
# Activate virtual environment
source chess_env/bin/activate

# Start the backend server
python backend.py
```

The server will start on `http://localhost:5001`

### 3. Open the Game

Open `3d-chess-backend.html` in your web browser. You can:

- **Create Multiplayer Game**: Creates a game and gives you a Game ID to share
- **Play vs Computer**: Start a game against Stockfish AI
- **Join Game**: Enter a Game ID to join an existing multiplayer game

## API Endpoints

### REST API
- `POST /api/game/create` - Create a new game
- `POST /api/game/{game_id}/join` - Join an existing game
- `POST /api/game/{game_id}/move` - Make a move
- `GET /api/game/{game_id}/state` - Get current game state
- `DELETE /api/game/{game_id}` - Delete a game

### WebSocket Events
- `join_game` - Join a game room for real-time updates
- `make_move` - Make a move in real-time
- `move_made` - Receive move updates
- `game_update` - Receive game state updates

## How to Play

### Move Notation
Use algebraic notation for moves:
- `e2e4` - Move piece from e2 to e4
- `g1f3` - Move knight from g1 to f3
- `e7e8q` - Promote pawn to queen

### Multiplayer
1. One player creates a multiplayer game
2. Share the Game ID with another player
3. Second player joins using the Game ID
4. Take turns making moves

### vs Computer
1. Click "Play vs Computer"
2. You play as white, computer as black
3. Make your move, computer responds automatically

## Dependencies

### Python Backend
- `flask` - Web framework
- `flask-cors` - Cross-origin resource sharing
- `flask-socketio` - WebSocket support
- `python-chess` - Chess logic and board representation
- `stockfish` - Stockfish engine interface

### Frontend
- `Three.js` - 3D graphics
- `Socket.IO` - Real-time communication
- `chess.js` - Chess validation (client-side)

## Configuration

### Stockfish Path
The backend automatically detects Stockfish in common locations:
- `/opt/homebrew/bin/stockfish` (Homebrew on Apple Silicon)
- `/usr/local/bin/stockfish` (Homebrew on Intel)
- `stockfish` (in PATH)

To use a custom path, edit the `STOCKFISH_PATH` variable in `backend.py`.

### Server Settings
- Default port: 5000
- CORS enabled for all origins
- Debug mode enabled (disable for production)

## Troubleshooting

### Connection Issues
- Ensure the backend server is running on port 5001
- Check browser console for WebSocket connection errors
- Verify CORS settings if hosting on different domains

### Stockfish Issues
- Install Stockfish: `brew install stockfish` (macOS)
- Verify installation: `stockfish` in terminal
- Check path in `backend.py` if needed

### Move Issues
- Use proper algebraic notation (e.g., `e2e4`)
- Ensure it's your turn before making a move
- Check that the move is legal in the current position

## Development

### Running in Development
```bash
source chess_env/bin/activate
python backend.py
```

### File Structure
```
3d-chess/
├── backend.py              # Flask backend server
├── chess-client.js         # JavaScript client library
├── 3d-chess-backend.html   # Updated HTML with backend
├── 3d-chess.html          # Original standalone version
├── requirements.txt       # Python dependencies
├── setup.sh              # Setup script
└── README.md             # This file
```

## License

This project is open source and available under the MIT License.