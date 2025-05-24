# Use Python 3.11 slim image
FROM python:3.11-slim

# Install system dependencies including Stockfish
RUN apt-get update && apt-get install -y \
    stockfish \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements first for better Docker layer caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy essential application files
COPY backend.py .
COPY chess-client.js .
COPY 3d-chess-backend.html .

# Create games directory for PGN exports
RUN mkdir -p games

# Expose port 5001 (internal Flask port)
EXPOSE 5001

# Set environment variables
ENV FLASK_APP=backend.py
ENV FLASK_ENV=production
ENV STOCKFISH_PATH=/usr/bin/stockfish

# Run the application
CMD ["python", "backend.py"]
