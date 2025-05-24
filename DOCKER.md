# Docker Setup for 3D Chess Application

## Overview

This document provides instructions for running the 3D Chess application using Docker. The application has been fully dockerized and is accessible through a web browser at `http://localhost:1111`.

## ✅ Complete Setup

The application includes:
- **Flask backend** with WebSocket support for multiplayer functionality
- **Stockfish 15.1 engine** for computer opponent (single-player mode)
- **3D chess interface** with Three.js visualization
- **PGN export functionality** with persistent game storage
- **Full multiplayer support** via WebSocket connections

## Quick Start

1. **Build and run the application:**
   ```bash
   docker-compose up --build
   ```

2. **Access the application:**
   Open your browser and go to `http://localhost:1111`

3. **Stop the application:**
   ```bash
   docker-compose down
   ```

## Files Configuration

### Created Docker Files

- **`Dockerfile`** - Container configuration with Python 3.11 and Stockfish
- **`docker-compose.yml`** - Service orchestration mapping port 1111 to internal port 5001
- **`.dockerignore`** - Build optimization excluding test files and documentation

### Modified Files

- **`backend.py`** - Updated for Docker compatibility:
  - Stockfish path detection including `/usr/games/stockfish` for Docker
  - Added route handlers for serving HTML and JS files directly
  - Flask-SocketIO configuration with `allow_unsafe_werkzeug=True`
  - Host binding to `0.0.0.0` for container accessibility

- **`3d-chess-backend.html`** - Dynamic server connection:
  - Uses `window.location.origin` instead of hardcoded localhost URL
  - Ensures compatibility between local and Docker environments

## Features Verified ✅

### Core Functionality
- ✅ **Web interface accessible** at `http://localhost:1111`
- ✅ **3D chess board rendering** with Three.js
- ✅ **Computer opponent** using Stockfish 15.1 engine
- ✅ **Multiplayer support** via WebSocket connections
- ✅ **Move validation** and game logic
- ✅ **PGN export** with persistent storage in `games/` directory

### Docker-Specific Features
- ✅ **Container isolation** with proper networking
- ✅ **Volume mounting** for game persistence
- ✅ **Stockfish integration** at `/usr/games/stockfish`
- ✅ **Port mapping** 1111:5001 working correctly
- ✅ **Dynamic URL handling** for client-server connection

## Technical Details

### Container Specifications
- **Base Image:** python:3.11-slim
- **Stockfish Version:** 15.1 (installed via apt-get)
- **Port Mapping:** External 1111 → Internal 5001
- **Volume:** `./games:/app/games` for PGN persistence
- **Network:** Custom bridge network `chess-network`

### Stockfish Path Resolution
The backend automatically detects Stockfish in the following order:
1. Environment variable `STOCKFISH_PATH`
2. `/opt/homebrew/bin/stockfish` (macOS Homebrew)
3. `/usr/local/bin/stockfish` (Alternative Linux path)
4. `/usr/bin/stockfish` (Standard Linux path)
5. `/usr/games/stockfish` (Debian/Ubuntu games path) ← **Used in Docker**
6. `stockfish` (Assumes in PATH)

### WebSocket Configuration
- **CORS enabled** for all origins
- **Transport fallback** from WebSocket to polling
- **Session persistence** across container restarts
- **Multiplayer room management** with unique game IDs

## Usage Instructions

### Single Player (vs Computer)
1. Access `http://localhost:1111`
2. Click "Create Single Player Game"
3. Play against Stockfish engine

### Multiplayer
1. **Player 1:** Click "Create Multiplayer Game"
2. **Player 2:** Enter the game ID and click "Join Game"
3. **Play:** Take turns making moves

### Game Management
- **Save games:** Games automatically save as PGN files in `games/` directory
- **View history:** Access move history via the interface
- **Export PGN:** Download game notation for external analysis

## Troubleshooting

### Common Issues

**Container won't start:**
```bash
docker-compose logs chess-backend
```

**Port already in use:**
```bash
# Change port in docker-compose.yml
ports:
  - "1112:5001"  # Use different external port
```

**Stockfish not working:**
```bash
# Test Stockfish in container
docker-compose exec chess-backend /usr/games/stockfish --help
```

### Performance Optimization

**For production use:**
- Consider using a production WSGI server like Gunicorn
- Add nginx reverse proxy for better performance
- Configure proper logging and monitoring

## Development

### Local Development vs Docker

**Local development:**
```bash
source chess_env/bin/activate
python backend.py
# Access at http://localhost:5001
```

**Docker development:**
```bash
docker-compose up
# Access at http://localhost:1111
```

### File Watching
To enable file watching during development:
```bash
docker-compose up --build  # Rebuild when files change
```

## Success Confirmation

The dockerization is complete and working when you see:

1. ✅ Container starts without errors
2. ✅ Log shows `Stockfish path: /usr/games/stockfish`
3. ✅ Web interface loads at `http://localhost:1111`
4. ✅ WebSocket connections establish successfully
5. ✅ Computer moves work in single-player mode
6. ✅ Multiplayer rooms can be created and joined

**🎉 Docker setup completed successfully!**

The 3D Chess application is now fully containerized and ready for deployment or distribution via Docker.
