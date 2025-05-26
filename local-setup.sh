#!/bin/bash

# 3D Chess Backend Setup Script

echo "🏁 Setting up 3D Chess Backend..."

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3 first."
    exit 1
fi

# Check if pip is installed
if ! command -v pip3 &> /dev/null; then
    echo "❌ pip3 is not installed. Please install pip3 first."
    exit 1
fi

# Create virtual environment
echo "📦 Creating virtual environment..."
python3 -m venv chess_env

# Activate virtual environment
echo "🔄 Activating virtual environment..."
source chess_env/bin/activate

# Install Python dependencies
echo "📚 Installing Python dependencies..."
pip install -r requirements.txt

# Check if Stockfish is installed
echo "🤖 Checking for Stockfish installation..."
if command -v stockfish &> /dev/null; then
    echo "✅ Stockfish found in PATH"
elif [ -f "/opt/homebrew/bin/stockfish" ]; then
    echo "✅ Stockfish found at /opt/homebrew/bin/stockfish"
elif [ -f "/usr/local/bin/stockfish" ]; then
    echo "✅ Stockfish found at /usr/local/bin/stockfish"
else
    echo "⚠️  Stockfish not found. Installing via Homebrew..."
    if command -v brew &> /dev/null; then
        brew install stockfish
    else
        echo "❌ Homebrew not found. Please install Stockfish manually:"
        echo "   - macOS: brew install stockfish"
        echo "   - Ubuntu: sudo apt-get install stockfish"
        echo "   - Or download from: https://stockfishchess.org/download/"
    fi
fi

echo ""
echo "🎉 Setup complete!"
echo ""
echo "To start the backend server:"
echo "1. Activate the virtual environment: source chess_env/bin/activate"
echo "2. Run the server: python backend.py"
echo ""
echo "The server will be available at: http://localhost:5001"
