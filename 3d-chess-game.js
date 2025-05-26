
// Initialize scene, camera, and renderer
const scene = new THREE.Scene();

// Create light pale green gradient background
const canvas = document.createElement('canvas');
const context = canvas.getContext('2d');
canvas.width = 512;
canvas.height = 512;
const gradient = context.createLinearGradient(0, 0, 0, 512);
gradient.addColorStop(0, '#e8f5e8'); // light pale green
gradient.addColorStop(1, '#d4f0d4'); // slightly deeper pale green
context.fillStyle = gradient;
context.fillRect(0, 0, 512, 512);
const backgroundTexture = new THREE.CanvasTexture(canvas);
scene.background = backgroundTexture;

const camera = new THREE.PerspectiveCamera(45, window.innerWidth/window.innerHeight, 0.1, 1000);
camera.position.set(0, 25, 35);
camera.lookAt(0, 0, 0);

const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
renderer.setSize(window.innerWidth, window.innerHeight);
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFSoftShadowMap;
document.body.appendChild(renderer.domElement);

// Add orbit controls
const controls = new THREE.OrbitControls(camera, renderer.domElement);
controls.enableDamping = true;
controls.dampingFactor = 0.05;
controls.enablePan = false;
controls.minDistance = 15;
controls.maxDistance = 60;
controls.maxPolarAngle = Math.PI / 2;

// Add ambient and directional light
const ambientLight = new THREE.AmbientLight(0x404040, 0.4);
scene.add(ambientLight);
const directionalLight = new THREE.DirectionalLight(0xffffff, 0.8);
directionalLight.position.set(20, 30, 20);
directionalLight.castShadow = true;
directionalLight.shadow.mapSize.width = 2048;
directionalLight.shadow.mapSize.height = 2048;
scene.add(directionalLight);

// Create the semi-transparent mountain-like chessboard
const boardGroup = new THREE.Group();
const squareSize = 2;
const boardSize = 8;
const squares = [];

// Board view state
let isMountainView = true;
let isAnimating = false;
const animationDuration = 1500; // 1.5 seconds

// Store original elevations for animation
const mountainElevations = [];
const flatElevations = [];

for (let i = 0; i < boardSize; i++) {
    squares[i] = [];
    mountainElevations[i] = [];
    flatElevations[i] = [];
    for (let j = 0; j < boardSize; j++) {
    const geometry = new THREE.BoxGeometry(squareSize * 0.95, 0.3, squareSize * 0.95);
    const isLight = (i + j) % 2 === 0;
    const material = new THREE.MeshPhongMaterial({
        color: isLight ? 0xf0f0f0 : 0xa0a0a0,
        transparent: true,
        opacity: 0.7,
    });
    const square = new THREE.Mesh(geometry, material);
    const x = (i - boardSize / 2 + 0.5) * squareSize;
    const z = (j - boardSize / 2 + 0.5) * squareSize;
    
    // Create mountain peak with 4 levels based on distance from center
    const centerX = 3.5;
    const centerZ = 3.5;
    const distanceFromCenter = Math.max(Math.abs(i - centerX), Math.abs(j - centerZ));
    let mountainElevation;
    
    if (distanceFromCenter < 1.0) { // Center 4 squares (highest)
        mountainElevation = 6.0;
    } else if (distanceFromCenter < 2.0) { // Next ring
        mountainElevation = 4.0;
    } else if (distanceFromCenter < 3.0) { // Third ring
        mountainElevation = 2.0;
    } else { // Outer ring (lowest)
        mountainElevation = 0.0;
    }
    
    // Store elevations
    mountainElevations[i][j] = mountainElevation;
    flatElevations[i][j] = 0.0; // Flat board at ground level
    
    square.position.set(x, mountainElevation, z);
    square.receiveShadow = true;
    squares[i][j] = { mesh: square, elevation: mountainElevation, originalY: mountainElevation };
    boardGroup.add(square);
    }
}
scene.add(boardGroup);

// Add coordinate labels around the board
function createCoordinateLabels() {
    const labelGroup = new THREE.Group();
    
    // Create letters (a-h) along the bottom and top
    const letters = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h'];
    for (let i = 0; i < 8; i++) {
    const x = (i - boardSize / 2 + 0.5) * squareSize;
    
    // Bottom labels (from white's perspective)
    const bottomCanvas = document.createElement('canvas');
    const bottomContext = bottomCanvas.getContext('2d');
    bottomCanvas.width = 128;
    bottomCanvas.height = 128;
    bottomContext.font = 'Bold 48px Arial';
    bottomContext.fillStyle = '#ffffff';
    bottomContext.strokeStyle = '#000000';
    bottomContext.lineWidth = 3;
    bottomContext.textAlign = 'center';
    bottomContext.textBaseline = 'middle';
    bottomContext.strokeText(letters[i], 64, 64);
    bottomContext.fillText(letters[i], 64, 64);
    
    const bottomTexture = new THREE.CanvasTexture(bottomCanvas);
    const bottomMaterial = new THREE.SpriteMaterial({ map: bottomTexture });
    const bottomSprite = new THREE.Sprite(bottomMaterial);
    
    bottomSprite.position.set(x, 0.5, -10);
    bottomSprite.scale.set(2, 2, 1);
    labelGroup.add(bottomSprite);
    
    // Top labels (from white's perspective)
    const topCanvas = document.createElement('canvas');
    const topContext = topCanvas.getContext('2d');
    topCanvas.width = 128;
    topCanvas.height = 128;
    topContext.font = 'Bold 48px Arial';
    topContext.fillStyle = '#ffffff';
    topContext.strokeStyle = '#000000';
    topContext.lineWidth = 3;
    topContext.textAlign = 'center';
    topContext.textBaseline = 'middle';
    topContext.strokeText(letters[i], 64, 64);
    topContext.fillText(letters[i], 64, 64);
    
    const topTexture = new THREE.CanvasTexture(topCanvas);
    const topMaterial = new THREE.SpriteMaterial({ map: topTexture });
    const topSprite = new THREE.Sprite(topMaterial);
    
    topSprite.position.set(x, 0.5, 10);
    topSprite.scale.set(2, 2, 1);
    labelGroup.add(topSprite);
    }
    
    // Create numbers (1-8) along the left and right sides
    const numbers = ['8', '7', '6', '5', '4', '3', '2', '1']; // Fixed: reversed so 1 is on white side
    for (let i = 0; i < 8; i++) {
    const z = (i - boardSize / 2 + 0.5) * squareSize;
    
    // Left labels (from white's perspective)
    const leftCanvas = document.createElement('canvas');
    const leftContext = leftCanvas.getContext('2d');
    leftCanvas.width = 128;
    leftCanvas.height = 128;
    leftContext.font = 'Bold 48px Arial';
    leftContext.fillStyle = '#ffffff';
    leftContext.strokeStyle = '#000000';
    leftContext.lineWidth = 3;
    leftContext.textAlign = 'center';
    leftContext.textBaseline = 'middle';
    leftContext.strokeText(numbers[i], 64, 64);
    leftContext.fillText(numbers[i], 64, 64);
    
    const leftTexture = new THREE.CanvasTexture(leftCanvas);
    const leftMaterial = new THREE.SpriteMaterial({ map: leftTexture });
    const leftSprite = new THREE.Sprite(leftMaterial);
    
    leftSprite.position.set(-10, 0.5, z);
    leftSprite.scale.set(2, 2, 1);
    labelGroup.add(leftSprite);
    
    // Right labels (from white's perspective)
    const rightCanvas = document.createElement('canvas');
    const rightContext = rightCanvas.getContext('2d');
    rightCanvas.width = 128;
    rightCanvas.height = 128;
    rightContext.font = 'Bold 48px Arial';
    rightContext.fillStyle = '#ffffff';
    rightContext.strokeStyle = '#000000';
    rightContext.lineWidth = 3;
    rightContext.textAlign = 'center';
    rightContext.textBaseline = 'middle';
    rightContext.strokeText(numbers[i], 64, 64);
    rightContext.fillText(numbers[i], 64, 64);
    
    const rightTexture = new THREE.CanvasTexture(rightCanvas);
    const rightMaterial = new THREE.SpriteMaterial({ map: rightTexture });
    const rightSprite = new THREE.Sprite(rightMaterial);
    
    rightSprite.position.set(10, 0.5, z);
    rightSprite.scale.set(2, 2, 1);
    labelGroup.add(rightSprite);
    }
    
    scene.add(labelGroup);
}

// Create coordinate labels
createCoordinateLabels();

// Chess piece symbols mapping
const pieceSymbols = {
    'p': '♟', 'r': '♜', 'n': '♞', 'b': '♝', 'q': '♛', 'k': '♚',
    'P': '♙', 'R': '♖', 'N': '♘', 'B': '♗', 'Q': '♕', 'K': '♔'
};

// Game state
let currentPieceGroup = null;
let gameClient = null;
let localChess = new Chess(); // For visualization
let gameStartTime = null;
let currentGameId = null;

// Initialize chess game client
async function initializeGameClient() {
    try {
    // Initialize game client with dynamic server URL
    const serverUrl = window.location.origin; // Use the same origin as the HTML page
    gameClient = new ChessGameClient(serverUrl);
    await gameClient.connect();
    
    // Set up event handlers
    gameClient.on('move_made', handleMoveMade);
    gameClient.on('game_update', handleGameUpdate);
    gameClient.on('error', handleGameError);
    gameClient.on('disconnect', handleDisconnect);
    
    updateConnectionStatus(true);
    console.log('Connected to chess server');
    } catch (error) {
    console.error('Failed to connect to chess server:', error);
    updateConnectionStatus(false);
    }
}

// Update connection status
function updateConnectionStatus(connected) {
    const statusElement = document.getElementById('connectionStatus');
    const textElement = document.getElementById('connectionText');
    
    if (connected) {
    statusElement.className = 'status-indicator status-connected';
    textElement.textContent = 'Connected';
    } else {
    statusElement.className = 'status-indicator status-disconnected';
    textElement.textContent = 'Disconnected';
    }
}

// Handle move made
function handleMoveMade(data) {
    console.log('Move made:', data);
    
    // Update local chess state
    localChess.load(data.board);
    
    // Update visual board
    updatePiecesFromFEN(data.board);
    
    // Update UI
    updateGameStatus(data);
    
    // Update move history
    updateMoveHistory(data.move_history);
}

// Handle game update
function handleGameUpdate(data) {
    console.log('Game update:', data);
    updateGameStatus(data);
    if (data.move_history) {
    updateMoveHistory(data.move_history);
    }
    
    // Show resignation message if applicable
    if (data.message) {
    alert(data.message);
    }
}

// Handle game error
function handleGameError(data) {
    console.error('Game error:', data);
    alert('Game error: ' + data.message);
}

// Handle disconnect
function handleDisconnect() {
    updateConnectionStatus(false);
}

// Update game status in UI
function updateGameStatus(gameState) {
    document.getElementById('currentTurn').textContent = gameState.current_turn;
    
    let statusText = '';
    if (gameState.game_result && gameState.game_result !== '*') {
    if (gameState.resigned_by) {
        statusText = `Game Over - ${gameState.resigned_by.charAt(0).toUpperCase() + gameState.resigned_by.slice(1)} resigned`;
    } else if (gameState.is_checkmate) {
        const winner = gameState.current_turn === 'white' ? 'Black' : 'White';
        statusText = `Checkmate! ${winner} wins.`;
    } else if (gameState.is_stalemate) {
        statusText = 'Stalemate! Game drawn.';
    } else if (gameState.game_result === '1/2-1/2') {
        statusText = 'Game drawn.';
    } else {
        const winner = gameState.game_result === '1-0' ? 'White' : 'Black';
        statusText = `Game Over - ${winner} wins.`;
    }
    } else if (gameState.is_check) {
    statusText = 'Check!';
    } else {
    statusText = 'Game in progress';
    }
    
    document.getElementById('gameStatus').textContent = statusText;
    
    // Enable/disable move controls based on turn and game status
    const gameEnded = gameState.game_result && gameState.game_result !== '*';
    const isMyTurn = gameClient && gameClient.isMyTurn(gameState);
    document.getElementById('makeMoveBtn').disabled = !isMyTurn || gameEnded;
    document.getElementById('moveInput').disabled = !isMyTurn || gameEnded;
    document.getElementById('resignBtn').disabled = gameEnded;
}

// Create chess pieces using simple geometry with symbols
function createPiecesFromFEN(fen) {
    // Clear existing pieces
    if (currentPieceGroup) {
    scene.remove(currentPieceGroup);
    }
    
    const pieceGroup = new THREE.Group();
    const chess = new Chess(fen);
    const position = chess.board();
    
    for (let rank = 0; rank < boardSize; rank++) {
    for (let file = 0; file < boardSize; file++) {
        const piece = position[rank][file];
        if (piece) {
        // Create piece base
        const baseGeometry = new THREE.CylinderGeometry(0.4, 0.5, 0.8, 12);
        const baseMaterial = new THREE.MeshPhongMaterial({
            color: piece.color === 'w' ? 0xffffff : 0x222222,
        });
        const baseMesh = new THREE.Mesh(baseGeometry, baseMaterial);
        
        // Position on board
        const x = (file - boardSize / 2 + 0.5) * squareSize;
        const z = (rank - boardSize / 2 + 0.5) * squareSize;
        const elevation = squares[file][rank].elevation;
        
        baseMesh.position.set(x, elevation + 0.8, z);
        baseMesh.castShadow = true;
        
        // Store board position for animation updates
        baseMesh.userData = { boardPosition: { i: file, j: rank } };
        
        // Create text sprite for piece symbol
        const canvas = document.createElement('canvas');
        const context = canvas.getContext('2d');
        canvas.width = 128;
        canvas.height = 128;
        context.font = 'Bold 80px Arial';
        context.fillStyle = piece.color === 'w' ? '#000000' : '#ffffff';
        context.textAlign = 'center';
        context.textBaseline = 'middle';
        context.fillText(pieceSymbols[piece.type] || piece.type.toUpperCase(), 64, 64);
        
        const texture = new THREE.CanvasTexture(canvas);
        const spriteMaterial = new THREE.SpriteMaterial({ map: texture, transparent: true });
        const sprite = new THREE.Sprite(spriteMaterial);
        sprite.position.set(x, elevation + 2.2, z);
        sprite.scale.set(1.5, 1.5, 1);
        
        // Store board position for animation updates
        sprite.userData = { boardPosition: { i: file, j: rank } };
        
        pieceGroup.add(baseMesh);
        pieceGroup.add(sprite);
        }
    }
    }
    
    currentPieceGroup = pieceGroup;
    scene.add(pieceGroup);
}

// Update pieces from FEN string
function updatePiecesFromFEN(fen) {
    createPiecesFromFEN(fen);
}

// Update move history display
function updateMoveHistory(moveHistory) {
    const moveList = document.getElementById('moveList');
    
    if (!moveHistory || moveHistory.length === 0) {
    moveList.innerHTML = '<div style="text-align: center; color: #666; font-style: italic;">No moves yet</div>';
    return;
    }
    
    let html = '';
    for (let i = 0; i < moveHistory.length; i += 2) {
    const moveNumber = Math.floor(i / 2) + 1;
    const whiteMove = moveHistory[i];
    const blackMove = moveHistory[i + 1] || '';
    
    html += `
        <div class="move-pair">
        <div class="move-number">${moveNumber}.</div>
        <div class="white-move">${whiteMove}</div>
        <div class="black-move">${blackMove}</div>
        </div>
    `;
    }
    
    moveList.innerHTML = html;
    moveList.scrollTop = moveList.scrollHeight;
}

// Convert move history to PGN format
function generatePGN(gameId, moveHistory, gameResult = '*') {
    const date = new Date();
    const dateStr = date.toISOString().split('T')[0].replace(/-/g, '.');
    
    let pgn = `[Event "3D Chess Game"]
[Site "3D Chess Web Application"]
[Date "${dateStr}"]
[Round "1"]
[White "Player"]
[Black "${gameClient && gameClient.gameType === 'vs_computer' ? 'Computer' : 'Player'}"]
[Result "${gameResult}"]
[GameId "${gameId}"]

`;
    
    // Add moves in PGN format
    if (moveHistory && moveHistory.length > 0) {
    const chess = new Chess();
    for (let i = 0; i < moveHistory.length; i++) {
        const move = moveHistory[i];
        try {
        // Convert UCI to SAN notation
        const moveObj = chess.move(move);
        if (i % 2 === 0) {
            // White move
            pgn += `${Math.floor(i / 2) + 1}. ${moveObj.san} `;
        } else {
            // Black move
            pgn += `${moveObj.san} `;
        }
        } catch (e) {
        console.error('Error converting move to PGN:', move, e);
        }
    }
    }
    
    pgn += gameResult;
    return pgn;
}

// Export PGN file
async function exportPGN() {
    if (!currentGameId) {
    alert('No active game to export');
    return;
    }
    
    try {
    // Get current game state
    const serverUrl = window.location.origin; // Use dynamic server URL
    const response = await fetch(`${serverUrl}/api/game/${currentGameId}/pgn`, {
        method: 'GET'
    });
    
    if (response.ok) {
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `chess_game_${currentGameId.substring(0, 8)}.pgn`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        window.URL.revokeObjectURL(url);
        
        alert('PGN file exported successfully!');
    } else {
        // Fallback: generate PGN on client side
        const gameState = await gameClient.getGameState();
        const gameResult = gameState.is_checkmate ? 
        (gameState.current_turn === 'white' ? '0-1' : '1-0') :
        gameState.is_stalemate ? '1/2-1/2' : '*';
        
        const pgn = generatePGN(currentGameId, gameState.move_history, gameResult);
        
        const blob = new Blob([pgn], { type: 'text/plain' });
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `chess_game_${currentGameId.substring(0, 8)}.pgn`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        window.URL.revokeObjectURL(url);
        
        alert('PGN file exported successfully!');
    }
    } catch (error) {
    console.error('Export failed:', error);
    alert('Failed to export PGN file: ' + error.message);
    }
}

// Resign from current game
async function resignGame() {
    if (!gameClient || !currentGameId) {
    alert('No active game to resign from');
    return;
    }
    
    const confirmed = confirm('Are you sure you want to resign? This will end the game.');
    if (!confirmed) return;
    
    try {
    const serverUrl = window.location.origin; // Use dynamic server URL
    const response = await fetch(`${serverUrl}/api/game/${currentGameId}/resign`, {
        method: 'POST',
        headers: {
        'Content-Type': 'application/json',
        },
        body: JSON.stringify({
        player_id: gameClient.playerId
        }),
    });
    
    const data = await response.json();
    
    if (data.success) {
        alert('You have resigned from the game.');
        updateGameStatus(data.game_state);
    } else {
        alert('Failed to resign: ' + data.error);
    }
    } catch (error) {
    console.error('Resign failed:', error);
    alert('Failed to resign: ' + error.message);
    }
}

// Board animation functions
function animateBoardTransition(toMountainView) {
    if (isAnimating) return;
    
    isAnimating = true;
    const startTime = Date.now();
    
    // Store starting positions
    const startPositions = [];
    for (let i = 0; i < boardSize; i++) {
    startPositions[i] = [];
    for (let j = 0; j < boardSize; j++) {
        startPositions[i][j] = squares[i][j].mesh.position.y;
    }
    }
    
    // Update button text during animation
    const toggleBtn = document.getElementById('toggleBoardBtn');
    toggleBtn.disabled = true;
    toggleBtn.textContent = '🔄 Animating...';
    
    function animateFrame() {
    const elapsed = Date.now() - startTime;
    const progress = Math.min(elapsed / animationDuration, 1);
    
    // Use easeInOutCubic for smooth animation
    const easedProgress = progress < 0.5 
        ? 4 * progress * progress * progress 
        : 1 - Math.pow(-2 * progress + 2, 3) / 2;
    
    // Animate each square
    for (let i = 0; i < boardSize; i++) {
        for (let j = 0; j < boardSize; j++) {
        const startY = startPositions[i][j];
        const targetY = toMountainView ? mountainElevations[i][j] : flatElevations[i][j];
        const currentY = startY + (targetY - startY) * easedProgress;
        
        squares[i][j].mesh.position.y = currentY;
        squares[i][j].elevation = currentY;
        
        // Update pieces on this square if any
        if (currentPieceGroup) {
            currentPieceGroup.children.forEach(piece => {
            if (piece.userData && piece.userData.boardPosition) {
                const boardI = piece.userData.boardPosition.i;
                const boardJ = piece.userData.boardPosition.j;
                if (boardI === i && boardJ === j) {
                // Update both base mesh and sprite positions
                if (piece.geometry && piece.geometry.type === 'CylinderGeometry') {
                    // This is a base mesh
                    piece.position.y = currentY + 0.8;
                } else if (piece.isSprite) {
                    // This is a sprite
                    piece.position.y = currentY + 2.2;
                }
                }
            }
            });
        }
        }
    }
    
    if (progress < 1) {
        requestAnimationFrame(animateFrame);
    } else {
        // Animation complete
        isAnimating = false;
        isMountainView = toMountainView;
        
        // Update button
        toggleBtn.disabled = false;
        if (isMountainView) {
        toggleBtn.innerHTML = '🏔️ Switch to Flat Board';
        } else {
        toggleBtn.innerHTML = '🎯 Switch to Mountain View';
        }
    }
    }
    
    requestAnimationFrame(animateFrame);
}

// Toggle board view function
function toggleBoardView() {
    if (isAnimating) return;
    animateBoardTransition(!isMountainView);
}

// Event handlers for UI buttons
document.getElementById('toggleBoardBtn').addEventListener('click', toggleBoardView);

document.getElementById('createMultiplayerBtn').addEventListener('click', async () => {
    if (!gameClient) return;
    
    try {
    const result = await gameClient.createGame('multiplayer');
    const joinResult = await gameClient.joinGame(result.game_id);
    
    currentGameId = result.game_id;
    gameStartTime = new Date();
    
    document.getElementById('gameIdDisplay').textContent = result.game_id;
    document.getElementById('playerColor').textContent = joinResult.color;
    document.getElementById('gameInfo').style.display = 'block';
    document.getElementById('moveControls').style.display = 'block';
    
    // Update board
    updatePiecesFromFEN(joinResult.game_state.board);
    updateGameStatus(joinResult.game_state);
    updateMoveHistory(joinResult.game_state.move_history);
    
    alert(`Created multiplayer game! Share this Game ID with another player: ${result.game_id}`);
    } catch (error) {
    alert('Failed to create multiplayer game: ' + error.message);
    }
});

document.getElementById('createComputerBtn').addEventListener('click', () => {
    // Show ELO selector
    document.getElementById('eloControls').style.display = 'block';
    document.getElementById('createComputerBtn').style.display = 'none';
    document.getElementById('createMultiplayerBtn').style.display = 'none';
});

// ELO slider functionality
document.getElementById('eloSlider').addEventListener('input', (e) => {
    const elo = parseInt(e.target.value);
    const display = document.getElementById('eloDisplay');
    
    let level;
    if (elo < 1000) level = 'Beginner';
    else if (elo < 1300) level = 'Novice';
    else if (elo < 1700) level = 'Intermediate';
    else if (elo < 2200) level = 'Advanced';
    else if (elo < 2700) level = 'Expert';
    else level = 'Master';
    
    display.textContent = `${elo} ELO (${level})`;
});

document.getElementById('startComputerGameBtn').addEventListener('click', async () => {
    if (!gameClient) return;
    
    const eloRating = parseInt(document.getElementById('eloSlider').value);
    
    try {
    const result = await gameClient.createGame('vs_computer', { elo_rating: eloRating });
    const joinResult = await gameClient.joinGame(result.game_id);
    
    currentGameId = result.game_id;
    gameStartTime = new Date();
    
    document.getElementById('gameIdDisplay').textContent = result.game_id;
    document.getElementById('playerColor').textContent = joinResult.color;
    document.getElementById('gameInfo').style.display = 'block';
    document.getElementById('moveControls').style.display = 'block';
    
    // Hide ELO controls and show main buttons
    document.getElementById('eloControls').style.display = 'none';
    document.getElementById('createComputerBtn').style.display = 'inline-block';
    document.getElementById('createMultiplayerBtn').style.display = 'inline-block';
    
    // Update board
    updatePiecesFromFEN(joinResult.game_state.board);
    updateGameStatus(joinResult.game_state);
    updateMoveHistory(joinResult.game_state.move_history);
    
    alert(`Created game vs computer (${eloRating} ELO)!`);
    } catch (error) {
    alert('Failed to create computer game: ' + error.message);
    }
});

document.getElementById('cancelComputerGameBtn').addEventListener('click', () => {
    // Hide ELO controls and show main buttons
    document.getElementById('eloControls').style.display = 'none';
    document.getElementById('createComputerBtn').style.display = 'inline-block';
    document.getElementById('createMultiplayerBtn').style.display = 'inline-block';
});

document.getElementById('joinGameBtn').addEventListener('click', async () => {
    if (!gameClient) return;
    
    const gameId = document.getElementById('gameIdInput').value.trim();
    if (!gameId) {
    alert('Please enter a Game ID');
    return;
    }
    
    try {
    const result = await gameClient.joinGame(gameId);
    
    currentGameId = gameId;
    gameStartTime = new Date();
    
    document.getElementById('gameIdDisplay').textContent = gameId;
    document.getElementById('playerColor').textContent = result.color;
    document.getElementById('gameInfo').style.display = 'block';
    document.getElementById('moveControls').style.display = 'block';
    
    // Update board
    updatePiecesFromFEN(result.game_state.board);
    updateGameStatus(result.game_state);
    updateMoveHistory(result.game_state.move_history);
    
    alert(`Joined game as ${result.color} player!`);
    } catch (error) {
    alert('Failed to join game: ' + error.message);
    }
});

document.getElementById('makeMoveBtn').addEventListener('click', async () => {
    if (!gameClient) return;
    
    const move = document.getElementById('moveInput').value.trim();
    if (!move) {
    alert('Please enter a move (e.g., e2e4)');
    return;
    }
    
    try {
    await gameClient.makeMove(move);
    document.getElementById('moveInput').value = '';
    } catch (error) {
    alert('Failed to make move: ' + error.message);
    }
});

// Allow Enter key to make moves
document.getElementById('moveInput').addEventListener('keypress', (e) => {
    if (e.key === 'Enter') {
    document.getElementById('makeMoveBtn').click();
    }
});

// Add event listeners for new buttons
document.getElementById('exportPgnBtn').addEventListener('click', exportPGN);
document.getElementById('resignBtn').addEventListener('click', resignGame);

// Initialize the game
createPiecesFromFEN(localChess.fen());
initializeGameClient();

// Handle window resize
window.addEventListener('resize', function () {
    camera.aspect = window.innerWidth / window.innerHeight;
    camera.updateProjectionMatrix();
    renderer.setSize(window.innerWidth, window.innerHeight);
}, false);

// Animation loop
function animate() {
    requestAnimationFrame(animate);
    controls.update();
    renderer.render(scene, camera);
}
animate();