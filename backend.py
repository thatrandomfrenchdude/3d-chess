from flask import Flask, request, jsonify, render_template_string, send_file
from flask_cors import CORS
from flask_socketio import SocketIO, emit, join_room, leave_room
import chess
import chess.engine
import chess.pgn
import json
import uuid
from threading import Lock
import os
import io
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'
CORS(app, origins="*")
socketio = SocketIO(app, cors_allowed_origins="*")

# Game state storage
games = {}
games_lock = Lock()

# Create games directory if it doesn't exist
GAMES_DIR = 'games'
if not os.path.exists(GAMES_DIR):
    os.makedirs(GAMES_DIR)

# Stockfish engine path - adjust this based on your system
STOCKFISH_PATH = os.environ.get('STOCKFISH_PATH', '/opt/homebrew/bin/stockfish')
if not os.path.exists(STOCKFISH_PATH):
    STOCKFISH_PATH = '/usr/local/bin/stockfish'  # Alternative path
if not os.path.exists(STOCKFISH_PATH):
    STOCKFISH_PATH = '/usr/bin/stockfish'  # Docker/Linux path
if not os.path.exists(STOCKFISH_PATH):
    STOCKFISH_PATH = '/usr/games/stockfish'  # Debian/Ubuntu games path
if not os.path.exists(STOCKFISH_PATH):
    STOCKFISH_PATH = 'stockfish'  # Assume it's in PATH

class ChessGame:
    def __init__(self, game_id, game_type='multiplayer', elo_rating=1500):
        self.game_id = game_id
        self.board = chess.Board()
        self.game_type = game_type  # 'multiplayer' or 'vs_computer'
        self.elo_rating = elo_rating  # Computer skill level (800-3000)
        self.players = {}
        self.current_turn = 'white'
        self.move_history = []
        self.engine = None
        self.game_result = '*'  # '*' = ongoing, '1-0' = white wins, '0-1' = black wins, '1/2-1/2' = draw
        self.start_time = datetime.now()
        self.end_time = None
        
        if game_type == 'vs_computer':
            try:
                self.engine = chess.engine.SimpleEngine.popen_uci(STOCKFISH_PATH)
                # Convert ELO rating to Stockfish skill level (0-20)
                skill_level = self._elo_to_skill_level(elo_rating)
                self.engine.configure({"Skill Level": skill_level})
                print(f"Initialized Stockfish with skill level {skill_level} (ELO {elo_rating})")
            except Exception as e:
                print(f"Failed to initialize Stockfish: {e}")
                self.engine = None
    
    def _elo_to_skill_level(self, elo):
        """Convert ELO rating to Stockfish skill level (0-20)"""
        # Map ELO 800-3000 to skill level 0-20
        # 800 ELO -> 0, 1500 ELO -> 10, 3000 ELO -> 20
        if elo <= 800:
            return 0
        elif elo >= 3000:
            return 20
        else:
            # Linear interpolation
            return int((elo - 800) * 20 / (3000 - 800))
    
    def add_player(self, player_id, color=None):
        if len(self.players) >= 2:
            return False
        
        if color is None:
            # Auto-assign color
            if len(self.players) == 0:
                color = 'white'
            else:
                color = 'black'
        
        if color in self.players.values():
            return False
        
        self.players[player_id] = color
        return True
    
    def remove_player(self, player_id):
        if player_id in self.players:
            del self.players[player_id]
    
    def make_move(self, move_str, player_id=None):
        # Validate player turn for multiplayer
        if self.game_type == 'multiplayer':
            if player_id not in self.players:
                return {"success": False, "error": "Player not in game"}
            
            player_color = self.players[player_id]
            if player_color != self.current_turn:
                return {"success": False, "error": "Not your turn"}
        
        try:
            move = chess.Move.from_uci(move_str)
            if move in self.board.legal_moves:
                self.board.push(move)
                self.move_history.append(move_str)
                self.current_turn = 'black' if self.current_turn == 'white' else 'white'
                
                # Check for game ending conditions
                if self.board.is_checkmate():
                    self.game_result = '0-1' if self.current_turn == 'white' else '1-0'
                    self.end_time = datetime.now()
                elif self.board.is_stalemate() or self.board.is_insufficient_material():
                    self.game_result = '1/2-1/2'
                    self.end_time = datetime.now()
                
                result = {
                    "success": True,
                    "board": self.board.fen(),
                    "move": move_str,
                    "current_turn": self.current_turn,
                    "is_check": self.board.is_check(),
                    "is_checkmate": self.board.is_checkmate(),
                    "is_stalemate": self.board.is_stalemate(),
                    "move_history": self.move_history,
                    "game_result": self.game_result
                }
                
                return result
            else:
                return {"success": False, "error": "Invalid move"}
        except Exception as e:
            return {"success": False, "error": f"Invalid move format: {str(e)}"}
    
    def resign(self, player_id):
        if player_id not in self.players:
            return {"success": False, "error": "Player not in game"}
        
        # Set game result based on who resigned
        resigning_color = self.players[player_id]
        if resigning_color == 'white':
            self.game_result = '0-1'  # Black wins
        else:
            self.game_result = '1-0'  # White wins
        
        self.end_time = datetime.now()
        
        return {
            "success": True,
            "game_result": self.game_result,
            "resigned_by": resigning_color
        }
    
    def get_computer_move(self):
        if self.engine and not self.board.is_game_over():
            try:
                result = self.engine.play(self.board, chess.engine.Limit(time=1.0))
                return result.move.uci()
            except Exception as e:
                print(f"Engine error: {e}")
                return None
        return None
    
    def get_board_state(self):
        return {
            "board": self.board.fen(),
            "current_turn": self.current_turn,
            "is_check": self.board.is_check(),
            "is_checkmate": self.board.is_checkmate(),
            "is_stalemate": self.board.is_stalemate(),
            "move_history": self.move_history,
            "players": self.players,
            "game_result": self.game_result
        }
    
    def generate_pgn(self):
        """Generate PGN format for the game"""
        game = chess.pgn.Game()
        
        # Set headers
        game.headers["Event"] = "3D Chess Game"
        game.headers["Site"] = "3D Chess Web Application"
        game.headers["Date"] = self.start_time.strftime("%Y.%m.%d")
        game.headers["Round"] = "1"
        game.headers["White"] = "Player" if self.game_type == 'multiplayer' else "Player"
        game.headers["Black"] = "Computer" if self.game_type == 'vs_computer' else "Player"
        game.headers["Result"] = self.game_result
        game.headers["GameId"] = self.game_id
        game.headers["TimeControl"] = "-"
        
        if self.game_type == 'vs_computer':
            game.headers["BlackElo"] = str(self.elo_rating)
            game.headers["ComputerLevel"] = f"ELO {self.elo_rating}"
        
        if self.end_time:
            game.headers["EndTime"] = self.end_time.strftime("%H:%M:%S")
        
        # Add moves
        node = game
        board = chess.Board()
        
        for move_uci in self.move_history:
            try:
                move = chess.Move.from_uci(move_uci)
                if move in board.legal_moves:
                    node = node.add_variation(move)
                    board.push(move)
            except Exception as e:
                print(f"Error adding move {move_uci} to PGN: {e}")
        
        return str(game)
    
    def cleanup(self):
        if self.engine:
            try:
                self.engine.quit()
            except:
                pass

@app.route('/')
def index():
    """Serve the main game HTML file"""
    try:
        with open('index.html', 'r') as f:
            return f.read()
    except FileNotFoundError:
        return """
        <!DOCTYPE html>
        <html>
        <head>
            <title>3D Chess Backend</title>
        </head>
        <body>
            <h1>3D Chess Backend API</h1>
            <p>Backend is running successfully!</p>
            <p>HTML file not found. Please ensure index.html is in the same directory.</p>
            <h2>Available Endpoints:</h2>
            <ul>
                <li>POST /api/game/create - Create a new game</li>
                <li>POST /api/game/{game_id}/join - Join a game</li>
                <li>POST /api/game/{game_id}/move - Make a move</li>
                <li>GET /api/game/{game_id}/state - Get game state</li>
                <li>GET /api/game/{game_id}/pgn - Export PGN</li>
                <li>POST /api/game/{game_id}/resign - Resign game</li>
            </ul>
        </body>
        </html>
        """

@app.route('/chess-client.js')
def serve_client_js():
    """Serve the chess client JavaScript file"""
    try:
        with open('chess-client.js', 'r') as f:
            response = app.response_class(
                response=f.read(),
                status=200,
                mimetype='application/javascript'
            )
            return response
    except FileNotFoundError:
        return "// chess-client.js not found", 404

@app.route('/styles.css')
def serve_styles_css():
    """Serve the CSS styles file"""
    try:
        with open('styles.css', 'r') as f:
            response = app.response_class(
                response=f.read(),
                status=200,
                mimetype='text/css'
            )
            return response
    except FileNotFoundError:
        return "/* styles.css not found */", 404
    
@app.route('/3d-chess-game.js')
def serve_chess_game_js():
    """Serve the chess game JavaScript file"""
    try:
        with open('3d-chess-game.js', 'r') as f:
            response = app.response_class(
                response=f.read(),
                status=200,
                mimetype='application/javascript'
            )
            return response
    except FileNotFoundError:
        return "// 3d-chess-game.js not found", 404

@app.route('/api/game/create', methods=['POST'])
def create_game():
    data = request.get_json() or {}
    game_type = data.get('type', 'multiplayer')  # 'multiplayer' or 'vs_computer'
    elo_rating = data.get('elo_rating', 1500)  # Default to 1500 ELO
    
    # Validate ELO rating
    if not isinstance(elo_rating, int) or elo_rating < 800 or elo_rating > 3000:
        return jsonify({"success": False, "error": "ELO rating must be between 800 and 3000"}), 400
    
    game_id = str(uuid.uuid4())
    
    with games_lock:
        games[game_id] = ChessGame(game_id, game_type, elo_rating)
    
    return jsonify({
        "success": True,
        "game_id": game_id,
        "type": game_type,
        "elo_rating": elo_rating if game_type == 'vs_computer' else None
    })

@app.route('/api/game/<game_id>/join', methods=['POST'])
def join_game(game_id):
    data = request.get_json() or {}
    player_id = data.get('player_id', str(uuid.uuid4()))
    color = data.get('color')  # Optional color preference
    
    with games_lock:
        if game_id not in games:
            return jsonify({"success": False, "error": "Game not found"}), 404
        
        game = games[game_id]
        success = game.add_player(player_id, color)
        
        if success:
            return jsonify({
                "success": True,
                "player_id": player_id,
                "color": game.players[player_id],
                "game_state": game.get_board_state()
            })
        else:
            return jsonify({"success": False, "error": "Cannot join game"}), 400

@app.route('/api/game/<game_id>/move', methods=['POST'])
def make_move(game_id):
    data = request.get_json()
    move = data.get('move')
    player_id = data.get('player_id')
    
    with games_lock:
        if game_id not in games:
            return jsonify({"success": False, "error": "Game not found"}), 404
        
        game = games[game_id]
        result = game.make_move(move, player_id)
        
        if result["success"]:
            # Emit move to all players in the game
            socketio.emit('move_made', result, room=game_id)
            
            # If it's a computer game and now it's the computer's turn
            if game.game_type == 'vs_computer' and game.current_turn == 'black' and game.game_result == '*':
                computer_move = game.get_computer_move()
                if computer_move:
                    computer_result = game.make_move(computer_move)
                    if computer_result["success"]:
                        socketio.emit('move_made', computer_result, room=game_id)
        
        return jsonify(result)

@app.route('/api/game/<game_id>/state', methods=['GET'])
def get_game_state(game_id):
    with games_lock:
        if game_id not in games:
            return jsonify({"success": False, "error": "Game not found"}), 404
        
        game = games[game_id]
        return jsonify({
            "success": True,
            "game_state": game.get_board_state()
        })

@app.route('/api/game/<game_id>/pgn', methods=['GET'])
def export_pgn(game_id):
    with games_lock:
        if game_id not in games:
            return jsonify({"success": False, "error": "Game not found"}), 404
        
        game = games[game_id]
        pgn_content = game.generate_pgn()
        
        # Save to games directory
        filename = f"chess_game_{game_id[:8]}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pgn"
        filepath = os.path.join(GAMES_DIR, filename)
        
        try:
            with open(filepath, 'w') as f:
                f.write(pgn_content)
            
            # Return the file as download
            return send_file(filepath, as_attachment=True, download_name=filename, mimetype='text/plain')
        except Exception as e:
            return jsonify({"success": False, "error": f"Failed to create PGN file: {str(e)}"}), 500

@app.route('/api/game/<game_id>/resign', methods=['POST'])
def resign_game(game_id):
    data = request.get_json()
    player_id = data.get('player_id')
    
    with games_lock:
        if game_id not in games:
            return jsonify({"success": False, "error": "Game not found"}), 404
        
        game = games[game_id]
        result = game.resign(player_id)
        
        if result["success"]:
            # Emit resignation to all players in the game
            game_state = game.get_board_state()
            socketio.emit('game_update', {
                **game_state,
                "resigned_by": result["resigned_by"],
                "message": f"{result['resigned_by'].title()} player has resigned"
            }, room=game_id)
            
            return jsonify({
                "success": True,
                "game_state": game_state,
                "resigned_by": result["resigned_by"]
            })
        else:
            return jsonify(result), 400

@app.route('/api/game/<game_id>', methods=['DELETE'])
def delete_game(game_id):
    with games_lock:
        if game_id in games:
            games[game_id].cleanup()
            del games[game_id]
            return jsonify({"success": True})
        else:
            return jsonify({"success": False, "error": "Game not found"}), 404

# WebSocket events
@socketio.on('join_game')
def on_join_game(data):
    game_id = data['game_id']
    player_id = data.get('player_id')
    
    join_room(game_id)
    
    with games_lock:
        if game_id in games:
            game = games[game_id]
            emit('game_update', game.get_board_state())

@socketio.on('leave_game')
def on_leave_game(data):
    game_id = data['game_id']
    player_id = data.get('player_id')
    
    leave_room(game_id)
    
    with games_lock:
        if game_id in games and player_id:
            games[game_id].remove_player(player_id)

@socketio.on('make_move')
def on_make_move(data):
    game_id = data['game_id']
    move = data['move']
    player_id = data.get('player_id')
    
    with games_lock:
        if game_id not in games:
            emit('error', {"message": "Game not found"})
            return
        
        game = games[game_id]
        result = game.make_move(move, player_id)
        
        if result["success"]:
            emit('move_made', result, room=game_id)
            
            # Handle computer move for vs_computer games
            if game.game_type == 'vs_computer' and game.current_turn == 'black' and game.game_result == '*':
                computer_move = game.get_computer_move()
                if computer_move:
                    computer_result = game.make_move(computer_move)
                    if computer_result["success"]:
                        emit('move_made', computer_result, room=game_id)
        else:
            emit('error', {"message": result["error"]})

if __name__ == '__main__':
    print("Starting 3D Chess Backend...")
    print(f"Stockfish path: {STOCKFISH_PATH}")
    print("Server will be available at http://localhost:5001")
    socketio.run(app, debug=False, host='0.0.0.0', port=5001, allow_unsafe_werkzeug=True)
