class ChessGameClient {
    constructor(serverUrl = 'http://localhost:5001') {
        this.serverUrl = serverUrl;
        this.socket = null;
        this.gameId = null;
        this.playerId = null;
        this.playerColor = null;
        this.callbacks = {};
    }

    // Connect to the server using Socket.IO
    connect() {
        return new Promise((resolve, reject) => {
            try {
                this.socket = io(this.serverUrl);
                
                this.socket.on('connect', () => {
                    console.log('Connected to chess server');
                    resolve();
                });
                
                this.socket.on('disconnect', () => {
                    console.log('Disconnected from chess server');
                    this.triggerCallback('disconnect');
                });
                
                this.socket.on('move_made', (data) => {
                    console.log('Move made:', data);
                    this.triggerCallback('move_made', data);
                });
                
                this.socket.on('game_update', (data) => {
                    console.log('Game update:', data);
                    this.triggerCallback('game_update', data);
                });
                
                this.socket.on('error', (data) => {
                    console.error('Game error:', data);
                    this.triggerCallback('error', data);
                });
                
                this.socket.on('connect_error', (error) => {
                    console.error('Connection error:', error);
                    reject(error);
                });
                
            } catch (error) {
                reject(error);
            }
        });
    }

    // Create a new game
    async createGame(gameType = 'multiplayer') {
        try {
            const response = await fetch(`${this.serverUrl}/api/game/create`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ type: gameType }),
            });
            
            const data = await response.json();
            
            if (data.success) {
                this.gameId = data.game_id;
                console.log(`Created ${gameType} game with ID: ${this.gameId}`);
                return data;
            } else {
                throw new Error(data.error || 'Failed to create game');
            }
        } catch (error) {
            console.error('Error creating game:', error);
            throw error;
        }
    }

    // Join an existing game
    async joinGame(gameId, playerId = null, color = null) {
        try {
            const body = {};
            if (playerId) body.player_id = playerId;
            if (color) body.color = color;
            
            const response = await fetch(`${this.serverUrl}/api/game/${gameId}/join`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(body),
            });
            
            const data = await response.json();
            
            if (data.success) {
                this.gameId = gameId;
                this.playerId = data.player_id;
                this.playerColor = data.color;
                
                // Join the Socket.IO room
                if (this.socket) {
                    this.socket.emit('join_game', {
                        game_id: this.gameId,
                        player_id: this.playerId
                    });
                }
                
                console.log(`Joined game ${gameId} as ${data.color} player`);
                return data;
            } else {
                throw new Error(data.error || 'Failed to join game');
            }
        } catch (error) {
            console.error('Error joining game:', error);
            throw error;
        }
    }

    // Make a move
    async makeMove(move) {
        if (!this.gameId) {
            throw new Error('Not connected to a game');
        }

        try {
            // Use Socket.IO for real-time updates
            if (this.socket && this.socket.connected) {
                this.socket.emit('make_move', {
                    game_id: this.gameId,
                    move: move,
                    player_id: this.playerId
                });
                return { success: true };
            } else {
                // Fallback to HTTP API
                const response = await fetch(`${this.serverUrl}/api/game/${this.gameId}/move`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        move: move,
                        player_id: this.playerId
                    }),
                });
                
                const data = await response.json();
                return data;
            }
        } catch (error) {
            console.error('Error making move:', error);
            throw error;
        }
    }

    // Get current game state
    async getGameState() {
        if (!this.gameId) {
            throw new Error('Not connected to a game');
        }

        try {
            const response = await fetch(`${this.serverUrl}/api/game/${this.gameId}/state`);
            const data = await response.json();
            
            if (data.success) {
                return data.game_state;
            } else {
                throw new Error(data.error || 'Failed to get game state');
            }
        } catch (error) {
            console.error('Error getting game state:', error);
            throw error;
        }
    }

    // Leave the current game
    leaveGame() {
        if (this.socket && this.gameId) {
            this.socket.emit('leave_game', {
                game_id: this.gameId,
                player_id: this.playerId
            });
        }
        
        this.gameId = null;
        this.playerId = null;
        this.playerColor = null;
    }

    // Set up event callbacks
    on(event, callback) {
        if (!this.callbacks[event]) {
            this.callbacks[event] = [];
        }
        this.callbacks[event].push(callback);
    }

    // Remove event callback
    off(event, callback) {
        if (this.callbacks[event]) {
            const index = this.callbacks[event].indexOf(callback);
            if (index > -1) {
                this.callbacks[event].splice(index, 1);
            }
        }
    }

    // Trigger callbacks
    triggerCallback(event, data) {
        if (this.callbacks[event]) {
            this.callbacks[event].forEach(callback => {
                try {
                    callback(data);
                } catch (error) {
                    console.error(`Error in ${event} callback:`, error);
                }
            });
        }
    }

    // Convert chess.js board format to your current format
    convertBoardFormat(fen) {
        const chess = new Chess(fen);
        const board = chess.board();
        
        // Convert to your existing format
        const convertedBoard = [];
        for (let rank = 0; rank < 8; rank++) {
            convertedBoard[rank] = [];
            for (let file = 0; file < 8; file++) {
                const piece = board[rank][file];
                if (piece) {
                    convertedBoard[rank][file] = {
                        type: piece.type,
                        color: piece.color
                    };
                } else {
                    convertedBoard[rank][file] = null;
                }
            }
        }
        
        return convertedBoard;
    }

    // Utility method to check if it's the current player's turn
    isMyTurn(gameState) {
        if (!gameState || !this.playerColor) return false;
        return gameState.current_turn === this.playerColor;
    }

    // Disconnect from server
    disconnect() {
        this.leaveGame();
        if (this.socket) {
            this.socket.disconnect();
            this.socket = null;
        }
    }
}

// Export for use in your HTML file
if (typeof window !== 'undefined') {
    window.ChessGameClient = ChessGameClient;
}
