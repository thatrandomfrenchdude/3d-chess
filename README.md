# 3D Mountain Chess

A comprehensive 3D chess game with multiplayer support, computer AI using Stockfish, and full containerization support. Features a unique mountain-peak design with elevation levels, real-time gameplay, and extensive game management capabilities.

## 📖 Table of Contents
- [Features](#-features)
- [Quick Start](#-quick-start)
    - [Docker (Recommended)](#docker-recommended)
    - [Virtual Environment](#virtual-environment)
- [Docs](#docs)
- [License](#license)

## 🚀 Features

### Core Gameplay
- 🏔️ **3D Mountain Board**: Unique mountain-peak design with elevation levels
- 👥 **Multiplayer**: Play against other players in real-time via WebSocket
- 🤖 **AI Opponent**: Play against Stockfish computer AI with customizable difficulty
- ⚡ **Real-time Updates**: WebSocket-based real-time game updates

### Deployment Options
- 🐳 **Docker Support**: Fully containerized with docker-compose
- 🖥️ **Virtual Environment**: Traditional Python virtual environment setup
- 🔧 **Easy Setup**: Automated setup scripts and configuration

## 🚀 Quick Start

### Docker (Recommended)

The fastest way to get started:

```bash
# Build and run the application
docker-compose up --build

# Access the game at http://localhost:1111
```

### Virtual Environment

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

## Docs

For more detailed documentation, please refer to the [docs](docs) directory.

## 📄 License

This project is open source and available under the MIT License. Read the [LICENSE](LICENSE) file for more information.
