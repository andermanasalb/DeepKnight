"""
Tests for the Analysis API endpoint.
"""

import pytest_asyncio
from httpx import ASGITransport, AsyncClient

from app.main import app


@pytest_asyncio.fixture
async def client():
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as c:
        yield c


class TestAnalysisEvaluate:
    async def test_evaluate_starting_position(self, client: AsyncClient):
        response = await client.post(
            "/api/v1/analysis/evaluate",
            json={"fen": "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"},
        )
        assert response.status_code == 200
        data = response.json()
        assert "classical_score" in data
        assert "pytorch_score" in data
        assert "turn" in data
        assert data["turn"] == "white"
        assert "phase" in data
        assert data["phase"] == "opening"

    async def test_evaluate_returns_phase(self, client: AsyncClient):
        # Starting position should be "opening"
        response = await client.post(
            "/api/v1/analysis/evaluate",
            json={"fen": "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"},
        )
        data = response.json()
        assert data["phase"] in ("opening", "middlegame", "endgame")

    async def test_evaluate_score_types(self, client: AsyncClient):
        response = await client.post(
            "/api/v1/analysis/evaluate",
            json={"fen": "rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq e3 0 1"},
        )
        data = response.json()
        assert isinstance(data["classical_score"], float)
        assert isinstance(data["pytorch_score"], float)

    async def test_evaluate_invalid_fen(self, client: AsyncClient):
        response = await client.post(
            "/api/v1/analysis/evaluate",
            json={"fen": "not-valid-fen"},
        )
        assert response.status_code == 400

    async def test_evaluate_check_detection(self, client: AsyncClient):
        # Position where White is in check
        response = await client.post(
            "/api/v1/analysis/evaluate",
            json={"fen": "4k3/8/8/8/8/8/8/4K2r w - - 0 1"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["is_check"] is True

    async def test_evaluate_not_in_check(self, client: AsyncClient):
        response = await client.post(
            "/api/v1/analysis/evaluate",
            json={"fen": "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"},
        )
        data = response.json()
        assert data["is_check"] is False

    async def test_evaluate_legal_move_count(self, client: AsyncClient):
        response = await client.post(
            "/api/v1/analysis/evaluate",
            json={"fen": "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"},
        )
        data = response.json()
        assert data["legal_move_count"] == 20  # Starting position
