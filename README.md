# ♟️ DeepKnight

A full-stack chess app I built to practice combining classical AI algorithms, a custom-trained neural network, and an LLM coaching layer — all packaged in a playable web interface.

[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?logo=fastapi)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-18-61DAFB?logo=react)](https://react.dev/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.x-3178C6?logo=typescript)](https://www.typescriptlang.org/)
[![PyTorch](https://img.shields.io/badge/PyTorch-2.x-EE4C2C?logo=pytorch)](https://pytorch.org/)

---

## What it does

You play chess against an engine that I built from scratch. There are three difficulty levels — easy, medium, and hard — each using a different search strategy and evaluation method.

On the right side there's a coach panel powered by Google Gemini. You can ask for hints, get the engine's last move explained, or do a full post-game review.

The evaluation bar shows two scores in real time: the classical engine score (material + piece placement) and a neural network score from a PyTorch model I trained on randomly-generated board positions.

---

## How I built it

### Step 1 — The chess engine

The core of the project is the chess engine, which lives in `backend/app/engine/`. I used the `python-chess` library as the source of truth for legal move generation and game state. The engine itself is mine.

**Easy mode** uses a basic minimax search at depth 2. It evaluates positions by counting material (how many pawns, knights, etc. each side has) and occasionally picks a random legal move to make it beatable.

**Medium mode** adds alpha-beta pruning, which lets you search much deeper without exploring every possible move sequence. It prunes branches that can't possibly improve the result, reducing the search space significantly. It also uses piece-square tables — lookup tables that reward pieces for being on strong squares (e.g. a knight is worth more in the center than on the edge). Runs at depth 3.

**Hard mode** runs depth 4 with move ordering (tries captures and checks first, which makes alpha-beta more effective) and blends the classical score with the neural network score.

### Step 2 — The neural network

The neural network (`backend/app/ml/`) is a small MLP (multi-layer perceptron) that takes a board position encoded as a 768-dimensional vector and outputs a score between -1 and +1.

The encoding works by treating the board as 12 binary planes (one per piece type per color), each with 64 squares. Flattening that gives 768 features.

I generated 150,000 training positions by playing out random games and scoring each position with the classical engine. Then I trained the network for 30 epochs using MLflow to track the run.

In hard mode the final score is `0.7 × classical + 0.3 × neural`.

### Step 3 — The API

The backend is a FastAPI app (`backend/app/`) with three route groups:

- `/api/v1/game` — start games, make moves, track state in PostgreSQL
- `/api/v1/analysis` — evaluate a position on demand
- `/api/v1/coach` — hint, move explanation, post-game summary, free chat

Game state is stored in PostgreSQL with SQLAlchemy 2.0 (async). Each move is logged with the position, both evaluation scores, and the SAN notation.

### Step 4 — The coach

The coach (`backend/app/genai/`) uses the Google Gemini API. I wrote structured prompt templates for each coaching action — hints avoid giving the exact best move and focus on strategic themes, the explanation prompt asks for tactical and strategic reasoning, and the post-game prompt summarizes the whole game from the PGN.

### Step 5 — The frontend

The frontend (`frontend/`) is React + Vite + TypeScript + Tailwind. The chess board comes from `react-chessboard`. I built a `useGame` hook that owns all game state and communicates with the backend, and a `useCoach` hook that manages the chat message history.

---

## Project structure

```
deepknight/
├── frontend/                  # React + Vite + TypeScript
│   └── src/
│       ├── components/        # ChessBoard, CoachChat, AnalysisPanel, etc.
│       ├── hooks/             # useGame, useCoach, useAnalysis
│       ├── pages/             # ChessGame main page
│       └── services/          # API client (axios)
│
├── backend/                   # FastAPI + Python 3.11
│   └── app/
│       ├── engine/            # Alpha-beta, minimax, evaluation, move ordering
│       ├── ml/                # ValueNet model, training scripts, inference
│       ├── genai/             # Gemini coach service + prompt templates
│       ├── chess/             # python-chess utilities (FEN, PGN)
│       ├── api/               # REST route handlers
│       └── db/                # SQLAlchemy models + Alembic migrations
│
├── data/
│   ├── models/                # Trained model checkpoints
│   └── processed/             # Generated training data (numpy arrays)
│
├── mlops/                     # DVC pipeline config + MLflow notes
└── docker-compose.yml
```

---

## Running locally

The easiest way is Docker Compose. You need Docker Desktop installed and a Google AI Studio API key.

**1. Get a Google AI Studio API key**

Go to [aistudio.google.com/apikey](https://aistudio.google.com/apikey) and create a free API key. The free tier is enough for personal use.

**2. Set up the environment file**

```bash
cp .env.example .env
```

Open `.env` and replace `your-google-ai-studio-api-key-here` with your actual key:

```
GOOGLE_API_KEY=AIza...
```

**3. Start everything**

```bash
docker compose up --build
```

This starts four containers: the React frontend, the FastAPI backend, PostgreSQL, and MLflow. The first build takes a few minutes because it installs PyTorch.

- Frontend → http://localhost:5173
- Backend API → http://localhost:8000
- API docs → http://localhost:8000/docs
- MLflow UI → http://localhost:5000

**4. Train the neural network (optional)**

The app works fine without the trained model — it just uses classical evaluation. To enable neural blending in hard mode:

```bash
# Generate 150k training positions (takes a few minutes)
docker compose exec backend python -m app.ml.training.dummy_data

# Train for 30 epochs (runs on CPU, ~10-20 minutes)
docker compose exec backend python -m app.ml.training.train
```

Once trained, restart the backend so it picks up the checkpoint:

```bash
docker compose restart backend
```

---

## Environment variables

| Variable | What it's for | Required |
|----------|--------------|----------|
| `GOOGLE_API_KEY` | Gemini API key for the coach | Yes (for coaching) |
| `DATABASE_URL` | PostgreSQL URL — defaults to `sqlite:///./chess.db` | Yes |
| `SECRET_KEY` | Random string used for signing | Yes |
| `GEMINI_MODEL` | Which Gemini model to use — defaults to `gemini-2.0-flash` | No |
| `MODEL_CHECKPOINT_PATH` | Path to trained `.pt` file | No |
| `DEFAULT_DIFFICULTY` | Starting difficulty — `easy`, `medium`, or `hard` | No |
| `ENGINE_TIMEOUT_SECONDS` | Max seconds per engine move | No |

---

## Running tests

```bash
cd backend
pip install -r requirements.txt
pytest app/tests/ -v
```

---

## Things I'd add with more time

- Stockfish-generated training data (much stronger positions than random play)
- WebSocket support for streaming the engine's thinking in real time
- Opening book integration (Polyglot format)
- User accounts with game history and a rough ELO rating
- A proper endgame tablebase (Syzygy) for perfect late-game play

---

## Tech stack

| Layer | Tools |
|-------|-------|
| Frontend | React 18, Vite, TypeScript, Tailwind CSS, react-chessboard |
| Backend | FastAPI, Pydantic v2, python-chess, Uvicorn |
| Database | PostgreSQL, SQLAlchemy 2.0 async, Alembic |
| Chess engine | Custom alpha-beta negamax, piece-square tables |
| Neural network | PyTorch MLP, numpy, MLflow |
| AI coach | Google Gemini (gemini-2.0-flash), structured prompts |
| MLOps | MLflow experiment tracking, DVC |
| Infrastructure | Docker Compose |
