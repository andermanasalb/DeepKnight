"""
Tests for the Coach API endpoints.

Note: Most tests mock the Anthropic API to avoid requiring
a real API key in CI/CD. Integration tests that hit the real
API can be run with INTEGRATION=true environment variable.
"""

import os
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
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


@pytest.fixture
def mock_coach_response():
    """Mock a successful Claude API response."""
    mock_message = MagicMock()
    mock_message.content = [MagicMock(text="This is a test coaching response.")]
    mock_message.usage = MagicMock(input_tokens=50, output_tokens=30)
    return mock_message


class TestCoachUnavailable:
    """Tests for when the coach service is not configured."""

    async def test_hint_without_api_key(self, client: AsyncClient):
        """Coach endpoint should return 503 if API key not set."""
        with patch("app.genai.coach_service.settings") as mock_settings:
            mock_settings.ANTHROPIC_API_KEY = ""
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
    """Tests using mocked Claude API."""

    async def test_hint_returns_response(self, client: AsyncClient, mock_coach_response):
        """Hint endpoint should return coaching text."""
        with patch("app.core.config.settings") as mock_settings:
            mock_settings.ANTHROPIC_API_KEY = "test-key"
            mock_settings.CLAUDE_MODEL = "claude-opus-4-6"
            mock_settings.CLAUDE_MAX_TOKENS = 1024

        with patch("anthropic.AsyncAnthropic") as mock_anthropic:
            mock_client = AsyncMock()
            mock_anthropic.return_value = mock_client
            mock_client.messages.create = AsyncMock(return_value=mock_coach_response)

            # Directly test the coach service
            from app.genai.coach_service import CoachService
            import chess

            service = CoachService()
            service._client = mock_client

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

    async def test_explain_move_returns_themes(self, mock_coach_response):
        """Explain move should parse themes from response."""
        with patch("anthropic.AsyncAnthropic") as mock_anthropic:
            mock_client = AsyncMock()
            mock_anthropic.return_value = mock_client

            # Mock response with known chess concepts
            mock_message = MagicMock()
            mock_message.content = [
                MagicMock(text="This move focuses on center control and piece development.")
            ]
            mock_message.usage = MagicMock(input_tokens=50, output_tokens=30)
            mock_client.messages.create = AsyncMock(return_value=mock_message)

            from app.genai.coach_service import CoachService
            import chess

            service = CoachService()
            service._client = mock_client

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
