# Architecture Overview

## System Design Philosophy

This project follows a **layered, polyglot architecture** where each layer has a single responsibility and communicates through well-defined interfaces. The design prioritizes:

- **Separation of concerns**: Frontend, backend, engine, ML, and GenAI are independent modules
- **Reliability**: python-chess is the source of truth for all game logic — no LLM or model generates moves
- **Extensibility**: Each layer can be upgraded independently
- **Portfolio signal**: Architecture decisions reflect production engineering judgment

---

## Layer Overview

```
┌────────────────────────────────────────────┐
│            React Frontend (Vite)           │
│  TypeScript · Tailwind · react-chessboard  │
└────────────────┬───────────────────────────┘
                 │  REST / JSON
┌────────────────▼───────────────────────────┐
│           FastAPI Backend                  │
│  Pydantic v2 · Uvicorn · Python 3.11       │
├────────────────┬───────────────────────────┤
│  Game Manager  │  Engine Service            │
│  python-chess  │  Minimax + Alpha-Beta      │
├────────────────┼───────────────────────────┤
│  ML Predictor  │  GenAI Coach               │
│  PyTorch CNN   │  Anthropic Claude API      │
├────────────────┴───────────────────────────┤
│           Database Layer                   │
│  SQLAlchemy 2.0 · Alembic · PostgreSQL     │
└────────────────────────────────────────────┘
```

---

## Component Breakdown

### Frontend (`frontend/`)

Built with React 18 + Vite + TypeScript + Tailwind CSS.

**Key decisions:**
- `react-chessboard` for drag-and-drop board rendering
- `chess.js` used **only** for frontend UI helpers (move highlighting) — the backend is authoritative
- API calls centralized in `services/api.ts` using `axios`
- Stateful logic encapsulated in custom hooks (`useGame`, `useAnalysis`, `useCoach`)
- All API response shapes are strictly typed via `types/`

**Component tree:**
```
App
└── ChessGame (page)
    ├── Header
    ├── ChessBoard          ← react-chessboard wrapper
    ├── DifficultySelector
    ├── AnalysisPanel       ← classical + neural scores
    ├── CoachChat           ← GenAI coaching interface
    ├── MoveHistory
    └── NewGameButton
```

---

### Backend API (`backend/app/api/`)

FastAPI application with versioned routes.

**Route groups:**
- `/api/v1/game/*` — game lifecycle (new game, make move, best move)
- `/api/v1/analysis/*` — position evaluation
- `/api/v1/coach/*` — generative AI coaching

**Middleware:**
- CORS configuration
- Request logging
- Error handling with structured responses

---

### Chess Engine (`backend/app/engine/`)

A classical chess engine built on `python-chess` with custom evaluation.

**Algorithm stack:**
1. **Move generation**: delegated entirely to `python-chess` (100% legal move compliance)
2. **Move ordering**: captures first, then killer moves, then positional heuristics
3. **Search**: Negamax with Alpha-Beta pruning
4. **Evaluation**: Material + PST (piece-square tables) + mobility + king safety

**Difficulty levels:**

| Level  | Search Depth | Evaluation | Notes |
|--------|-------------|------------|-------|
| Easy   | 2           | Material only | Occasionally picks suboptimal moves |
| Medium | 4           | Material + PST | Full alpha-beta, move ordering |
| Hard   | 6           | Classical + PyTorch hybrid | Neural evaluation blended in |

---

### ML Module (`backend/app/ml/`)

PyTorch-based position evaluator (ValueNet).

**Board encoding:**
```
Board → 12 planes × 8×8 grid = 768 features
  Planes: WP WN WB WR WQ WK BP BN BB BR BQ BK
  Each plane: 1 where piece exists, 0 elsewhere
  Flattened to 1D tensor of 768 floats
```

**ValueNet architecture:**
```
Input(768) → Linear(256) → ReLU → Dropout(0.3)
           → Linear(128) → ReLU → Dropout(0.2)
           → Linear(64)  → ReLU
           → Linear(1)   → Tanh
Output: scalar in [-1.0, 1.0] (negative = Black advantage)
```

**Hard mode integration:**
```python
final_score = 0.7 * classical_score + 0.3 * neural_score
```

---

### Generative AI Layer (`backend/app/genai/`)

Claude API integration for coaching — **never used for move generation**.

**Prompt structure:**
```
System: You are a chess coach. You are analyzing a game.
Context: FEN, move history, difficulty, last AI move
Task: [hint | explain_move | post_game_summary]
```

**Coach flows:**
1. `hint` — suggests a candidate move concept (not the exact move)
2. `explain_last_move` — explains the AI's strategic/tactical intention
3. `postgame_summary` — full game retrospective with mistake identification

---

### Database Layer (`backend/app/db/`)

SQLAlchemy 2.0 with Alembic migrations.

**Models:**
- `Game` — stores FEN, PGN, difficulty, status, timestamps
- `Move` — stores individual moves with metadata

**Migration strategy:**
- Alembic handles all schema changes
- Never modify schema without a migration
- Supports both PostgreSQL (production) and SQLite (development)

---

## Data Flow: Make Move

```
Human clicks piece → frontend validates dragged move shape
    → POST /api/v1/game/make_move {fen, move_uci, difficulty}
    → Backend: python-chess validates move is legal
    → Backend: push human move to board
    → Engine: search best AI response (depth based on difficulty)
    → Hard mode: ValueNet evaluates candidate positions
    → Backend: push AI move to board
    → Backend: compute analysis scores (classical + neural)
    → Response: {ai_move, fen, is_checkmate, pgn, analysis}
    → Frontend: update board state, move history, analysis panel
```

---

## Data Flow: Get Coach Hint

```
User clicks "Give me a hint"
    → POST /api/v1/coach/hint {fen, player_color, move_history}
    → Backend: gather game context (FEN, history, turn)
    → Backend: compute top candidate moves (classical engine)
    → GenAI: build prompt with context + candidate ideas
    → Claude API: generate coaching response
    → Response: {message, suggested_concept}
    → Frontend: display in CoachChat panel
```

---

## Key Design Decisions

### 1. python-chess as ground truth
All move validation, FEN parsing, and game state transitions happen through `python-chess`. No frontend library or LLM output ever directly modifies game state.

### 2. Stateless API (mostly)
Game state is represented as FEN strings passed with each request. This enables easy horizontal scaling and simplifies frontend state management. Full game history (PGN) is also passed/stored for coaching.

### 3. Classical engine + Neural hybrid
Rather than either pure classical or pure neural, Hard mode blends both: 70% classical score + 30% neural score. This provides stability (classical) with learned positional understanding (neural).

### 4. GenAI isolation
The Claude API is behind a service abstraction (`coach_service.py`). Prompts are templates in `prompts.py`. The LLM never touches game logic — it only receives context and produces text.

### 5. MLflow for reproducibility
Every training run is tracked in MLflow: hyperparameters, loss curves, model artifacts. This makes the ML pipeline reproducible and demonstrates MLOps awareness.
