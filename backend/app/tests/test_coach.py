"""
Tests for the Coach API endpoints.

Note: Most tests mock the Anthropic API to avoid requiring
a real API key in CI/CD. Integration tests that hit the real
API can be run with INTEGRATION=true environment variable.
"""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest_asyncio
from httpx import ASGITransport, AsyncClient

from app.main import app

STARTING_FEN = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
AFTER_E4_FEN = "rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq e3 0 1"


@pytest_asyncio.fixture
async def client():
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as c:
        yield c


class TestCoachUnavailable:
    """Tests for when the coach service is not configured."""

    async def test_hint_without_api_key(self, client: AsyncClient):
        """Coach endpoint should return 503 if API key not set."""
        with patch("app.genai.coach_service.settings") as mock_settings:
            mock_settings.GOOGLE_API_KEY = ""
            response = await client.post(
                "/api/v1/coach/hint",
                json={
                    "fen": STARTING_FEN,
                    "player_color": "white",
                    "move_history": [],
                },
            )
        assert response.status_code == 503


class TestCoachWithMock:
    """Tests using mocked Gemini API."""

    async def test_hint_returns_response(self, client: AsyncClient):
        """Hint endpoint should return coaching text."""
        import chess

        from app.genai.coach_service import CoachService

        mock_response = MagicMock()
        mock_response.text = "This is a test coaching response."
        mock_response.usage_metadata = MagicMock(total_token_count=80)

        mock_model = MagicMock()
        mock_model.generate_content_async = AsyncMock(return_value=mock_response)

        service = CoachService()
        service._model = mock_model
        service._initialized = True

        board = chess.Board()
        result = await service.get_hint(
            board=board,
            player_color="white",
            move_history=[],
            difficulty="medium",
        )

        assert "hint" in result
        assert result["hint"] == "This is a test coaching response."
        assert "tokens_used" in result
        assert result["tokens_used"] == 80

    async def test_explain_move_returns_themes(self):
        """Explain move should parse themes from response."""
        import chess

        from app.genai.coach_service import CoachService

        mock_response = MagicMock()
        mock_response.text = "This move focuses on center control and piece development."
        mock_response.usage_metadata = MagicMock(total_token_count=80)

        mock_model = MagicMock()
        mock_model.generate_content_async = AsyncMock(return_value=mock_response)

        service = CoachService()
        service._model = mock_model
        service._initialized = True

        board = chess.Board()
        board.push(chess.Move.from_uci("e2e4"))
        board.push(chess.Move.from_uci("e7e5"))

        result = await service.explain_last_move(
            board=board,
            ai_move="e7e5",
            ai_move_san="e5",
            move_history=["e2e4", "e7e5"],
            difficulty="medium",
        )

        assert "explanation" in result
        assert "themes" in result
        assert isinstance(result["themes"], list)


class TestPromptBuilding:
    """Unit tests for prompt template functions."""

    def test_hint_prompt_contains_fen(self):
        from app.genai.prompts import hint_prompt
        fen = STARTING_FEN
        prompt = hint_prompt(
            fen=fen,
            player_color="white",
            move_history=[],
            difficulty="medium",
        )
        assert fen in prompt

    def test_hint_prompt_contains_color(self):
        from app.genai.prompts import hint_prompt
        prompt = hint_prompt(
            fen=STARTING_FEN,
            player_color="white",
            move_history=["e2e4"],
            difficulty="medium",
        )
        assert "white" in prompt.lower()

    def test_explain_prompt_contains_move(self):
        from app.genai.prompts import explain_last_move_prompt
        prompt = explain_last_move_prompt(
            fen=AFTER_E4_FEN,
            ai_move="e7e5",
            ai_move_san="e5",
            move_history=["e2e4", "e7e5"],
            difficulty="medium",
        )
        assert "e5" in prompt

    def test_postgame_prompt_contains_pgn(self):
        from app.genai.prompts import postgame_summary_prompt
        pgn = "1. e4 e5 2. Nf3 Nc6"
        prompt = postgame_summary_prompt(
            pgn=pgn,
            difficulty="medium",
            player_color="white",
            result="black_wins",
        )
        assert pgn in prompt
