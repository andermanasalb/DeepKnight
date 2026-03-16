# API Reference

Base URL: `http://localhost:8000/api/v1`

Interactive docs: `http://localhost:8000/docs` (Swagger UI)

---

## Game Endpoints

### POST `/game/new_game`

Create a new game session.

**Request:**
```json
{
  "difficulty": "medium"
}
```

| Field | Type | Values | Default |
|-------|------|--------|---------|
| `difficulty` | string | `"easy"`, `"medium"`, `"hard"` | `"medium"` |

**Response:**
```json
{
  "game_id": "uuid-string",
  "fen": "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1",
  "turn": "white",
  "difficulty": "medium",
  "legal_moves": ["e2e4", "d2d4", "g1f3", "..."]
}
```

---

### POST `/game/make_move`

Submit a human move and receive the AI's response move.

**Request:**
```json
{
  "fen": "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1",
  "move_uci": "e2e4",
  "difficulty": "medium",
  "move_history": ["e2e4"]
}
```

| Field | Type | Description |
|-------|------|-------------|
| `fen` | string | Current board position in FEN notation |
| `move_uci` | string | Human's move in UCI format (e.g., `e2e4`, `e1g1` for castling) |
| `difficulty` | string | Engine difficulty level |
| `move_history` | string[] | Optional list of previous moves in UCI format |

**Response:**
```json
{
  "player_move": "e2e4",
  "player_move_san": "e4",
  "ai_move": "e7e5",
  "ai_move_san": "e5",
  "fen": "rnbqkbnr/pppp1ppp/8/4p3/4P3/8/PPPP1PPP/RNBQKBNR w KQkq e6 0 2",
  "turn": "white",
  "is_check": false,
  "is_checkmate": false,
  "is_stalemate": false,
  "is_game_over": false,
  "game_over_reason": null,
  "pgn": "1. e4 e5",
  "legal_moves": ["f1c4", "g1f3", "..."],
  "analysis": {
    "classical_score": 0.15,
    "pytorch_score": 0.08,
    "depth_searched": 4
  }
}
```

**Error responses:**
- `400 Bad Request` — Illegal move
- `422 Unprocessable Entity` — Invalid FEN or move format

---

### GET `/game/best_move`

Get the best move for a given position without making it.

**Query params:**
```
GET /game/best_move?fen=<FEN>&difficulty=hard
```

**Response:**
```json
{
  "best_move": "g1f3",
  "best_move_san": "Nf3",
  "score": 0.25,
  "depth": 6,
  "nodes_searched": 42819
}
```

---

### GET `/game/{game_id}`

Retrieve a stored game by ID.

**Response:**
```json
{
  "game_id": "uuid-string",
  "fen": "...",
  "pgn": "...",
  "difficulty": "hard",
  "status": "in_progress",
  "created_at": "2024-01-01T12:00:00Z",
  "updated_at": "2024-01-01T12:05:00Z"
}
```

---

## Analysis Endpoints

### POST `/analysis/evaluate`

Evaluate a board position using both classical engine and PyTorch model.

**Request:**
```json
{
  "fen": "rnbqkbnr/pppp1ppp/8/4p3/4P3/8/PPPP1PPP/RNBQKBNR w KQkq e6 0 2"
}
```

**Response:**
```json
{
  "classical_score": 0.15,
  "pytorch_score": 0.08,
  "turn": "white",
  "material_balance": 0,
  "phase": "opening",
  "is_check": false,
  "legal_move_count": 29
}
```

**Score conventions:**
- Positive = White advantage
- Negative = Black advantage
- Classical score in centipawns divided by 100 (so 0.25 = White up ~1/4 pawn)
- PyTorch score normalized to [-1.0, 1.0]

---

## Coach Endpoints

All coach endpoints call the Anthropic Claude API. Requires `ANTHROPIC_API_KEY` to be set.

### POST `/coach/hint`

Get a strategic hint for the current position.

**Request:**
```json
{
  "fen": "rnbqkbnr/pppp1ppp/8/4p3/4P3/8/PPPP1PPP/RNBQKBNR w KQkq e6 0 2",
  "player_color": "white",
  "move_history": ["e2e4", "e7e5"],
  "difficulty": "medium"
}
```

**Response:**
```json
{
  "hint": "Look at developing your knights and bishops toward the center. The f3 square for your knight and c4 for your bishop could both be strong choices here.",
  "suggested_concept": "piece development",
  "tokens_used": 142
}
```

---

### POST `/coach/explain`

Explain the AI's last move in plain English.

**Request:**
```json
{
  "fen": "rnbqkbnr/pppp1ppp/8/4p3/4P3/8/PPPP1PPP/RNBQKBNR w KQkq e6 0 2",
  "ai_move": "e7e5",
  "ai_move_san": "e5",
  "move_history": ["e2e4", "e7e5"],
  "difficulty": "medium"
}
```

**Response:**
```json
{
  "explanation": "The AI played e5 to immediately contest the center. By advancing the e-pawn to match yours, Black stakes out equal central space and prepares to develop pieces naturally. This is the most direct response to 1. e4, leading to open game positions where both sides fight for the center.",
  "themes": ["center control", "symmetry", "open game"],
  "tokens_used": 198
}
```

---

### POST `/coach/postgame`

Get a comprehensive post-game analysis.

**Request:**
```json
{
  "pgn": "1. e4 e5 2. Nf3 Nc6 3. Bc4 Bc5 4. O-O d6 5. d3 Nf6",
  "difficulty": "medium",
  "player_color": "white",
  "result": "black_wins"
}
```

**Response:**
```json
{
  "summary": "You played the Italian Game opening correctly with e4, Nf3, and Bc4...",
  "mistakes": [
    {
      "move_number": 5,
      "move": "d3",
      "issue": "A passive move. d4 would fight for the center more aggressively.",
      "severity": "inaccuracy"
    }
  ],
  "key_moments": ["Move 3: Bc4 enters the Giuoco Piano", "Move 5: Passive d3 cedes initiative"],
  "improvement_areas": ["Center control", "King safety"],
  "opening_name": "Italian Game / Giuoco Piano",
  "tokens_used": 512
}
```

---

### POST `/coach/chat`

Free-form coaching chat about the current game.

**Request:**
```json
{
  "message": "Why is castling important?",
  "fen": "...",
  "move_history": ["e2e4", "e7e5"],
  "context": "The player just moved their king."
}
```

**Response:**
```json
{
  "response": "Castling serves two critical purposes...",
  "tokens_used": 231
}
```

---

## Health Endpoints

### GET `/health`

Basic health check.

**Response:**
```json
{
  "status": "ok",
  "version": "1.0.0",
  "environment": "development"
}
```

### GET `/health/detailed`

Detailed health check including database and model status.

**Response:**
```json
{
  "status": "ok",
  "database": "connected",
  "pytorch_model": "loaded",
  "anthropic_configured": true,
  "version": "1.0.0"
}
```

---

## Error Format

All errors follow this structure:

```json
{
  "detail": "Human-readable error message",
  "error_code": "ILLEGAL_MOVE",
  "context": {
    "move": "e2e9",
    "fen": "..."
  }
}
```

**Common error codes:**

| Code | HTTP | Description |
|------|------|-------------|
| `ILLEGAL_MOVE` | 400 | Move is not legal in the given position |
| `INVALID_FEN` | 400 | FEN string could not be parsed |
| `GAME_OVER` | 400 | Move submitted but game is already over |
| `ENGINE_TIMEOUT` | 504 | Engine exceeded time limit |
| `COACH_UNAVAILABLE` | 503 | Anthropic API key not configured |
| `MODEL_NOT_LOADED` | 503 | PyTorch model checkpoint not found |
