"""
Integration tests for the Game API endpoints.

Uses httpx AsyncClient for async test support with FastAPI.
"""

import pytest_asyncio
from httpx import ASGITransport, AsyncClient

from app.main import app


@pytest_asyncio.fixture
async def client():
    """Create an async test client."""
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as c:
        yield c


class TestNewGame:
    async def test_new_game_default_difficulty(self, client: AsyncClient):
        response = await client.post("/api/v1/game/new_game", json={})
        assert response.status_code == 201
        data = response.json()
        assert "game_id" in data
        assert "fen" in data
        assert data["turn"] == "white"
        assert data["difficulty"] == "medium"
        assert len(data["legal_moves"]) == 20  # 20 legal moves in starting position

    async def test_new_game_easy_difficulty(self, client: AsyncClient):
        response = await client.post(
            "/api/v1/game/new_game", json={"difficulty": "easy"}
        )
        assert response.status_code == 201
        assert response.json()["difficulty"] == "easy"

    async def test_new_game_hard_difficulty(self, client: AsyncClient):
        response = await client.post(
            "/api/v1/game/new_game", json={"difficulty": "hard"}
        )
        assert response.status_code == 201
        assert response.json()["difficulty"] == "hard"

    async def test_new_game_invalid_difficulty(self, client: AsyncClient):
        response = await client.post(
            "/api/v1/game/new_game", json={"difficulty": "grandmaster"}
        )
        assert response.status_code == 422

    async def test_new_game_fen_is_starting_position(self, client: AsyncClient):
        response = await client.post("/api/v1/game/new_game", json={})
        fen = response.json()["fen"]
        assert "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR" in fen


class TestMakeMove:
    async def test_valid_move(self, client: AsyncClient):
        """A legal move should succeed and return AI response."""
        response = await client.post(
            "/api/v1/game/make_move",
            json={
                "fen": "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1",
                "move_uci": "e2e4",
                "difficulty": "easy",
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert data["player_move"] == "e2e4"
        assert data["player_move_san"] == "e4"
        assert data["ai_move"] is not None
        assert "fen" in data
        assert "analysis" in data
        assert not data["is_checkmate"]

    async def test_illegal_move_rejected(self, client: AsyncClient):
        """An illegal move should return 400."""
        response = await client.post(
            "/api/v1/game/make_move",
            json={
                "fen": "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1",
                "move_uci": "e2e5",  # Illegal: pawn can't jump 3 squares
                "difficulty": "easy",
            },
        )
        assert response.status_code == 400
        assert "Illegal move" in response.json()["detail"]

    async def test_invalid_move_format(self, client: AsyncClient):
        """Malformed move UCI should return 400."""
        response = await client.post(
            "/api/v1/game/make_move",
            json={
                "fen": "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1",
                "move_uci": "not-a-move",
                "difficulty": "easy",
            },
        )
        assert response.status_code == 400

    async def test_invalid_fen(self, client: AsyncClient):
        """Invalid FEN string should return 400."""
        response = await client.post(
            "/api/v1/game/make_move",
            json={
                "fen": "not-a-valid-fen",
                "move_uci": "e2e4",
                "difficulty": "easy",
            },
        )
        assert response.status_code == 400

    async def test_move_returns_legal_moves(self, client: AsyncClient):
        """Response should include legal moves for the next position."""
        response = await client.post(
            "/api/v1/game/make_move",
            json={
                "fen": "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1",
                "move_uci": "e2e4",
                "difficulty": "easy",
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data["legal_moves"], list)
        assert len(data["legal_moves"]) > 0

    async def test_analysis_in_response(self, client: AsyncClient):
        """Response should include classical and pytorch scores."""
        response = await client.post(
            "/api/v1/game/make_move",
            json={
                "fen": "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1",
                "move_uci": "e2e4",
                "difficulty": "medium",
            },
        )
        data = response.json()
        analysis = data["analysis"]
        assert "classical_score" in analysis
        assert "pytorch_score" in analysis
        assert "depth_searched" in analysis


class TestBestMove:
    async def test_best_move_returns_valid_uci(self, client: AsyncClient):
        """Best move endpoint should return a valid UCI move."""
        import chess
        fen = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
        response = await client.get(
            "/api/v1/game/best_move",
            params={"fen": fen, "difficulty": "easy"},
        )
        assert response.status_code == 200
        data = response.json()
        assert "best_move" in data
        # Verify it's a valid UCI move
        board = chess.Board(fen)
        move = chess.Move.from_uci(data["best_move"])
        assert move in board.legal_moves

    async def test_best_move_invalid_fen(self, client: AsyncClient):
        response = await client.get(
            "/api/v1/game/best_move",
            params={"fen": "invalid", "difficulty": "easy"},
        )
        assert response.status_code == 400


class TestHealthEndpoints:
    async def test_health(self, client: AsyncClient):
        response = await client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "ok"

    async def test_health_detailed(self, client: AsyncClient):
        response = await client.get("/health/detailed")
        assert response.status_code == 200
        data = response.json()
        assert "database" in data
        assert "pytorch_model" in data
