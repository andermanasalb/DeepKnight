"""
Gemini-powered chess coaching. Handles prompts, API calls, and response parsing.
The client is lazy-loaded so the app starts fine even without an API key set.
"""


import chess

from app.core.config import settings
from app.core.logging import get_logger
from app.genai.prompts import (
    SYSTEM_PROMPT,
    chat_prompt,
    explain_last_move_prompt,
    hint_prompt,
    postgame_summary_prompt,
)

logger = get_logger(__name__)


class CoachService:
    """
    Generative AI coaching service backed by Google Gemini.
    """

    def __init__(self):
        self._model = None
        self._initialized = False

    @property
    def is_available(self) -> bool:
        """Check if the coaching service is configured and available."""
        return bool(settings.GOOGLE_API_KEY)

    def _get_model(self):
        """Lazily initialize the Gemini model."""
        if not self._model:
            if not settings.GOOGLE_API_KEY:
                raise RuntimeError("GOOGLE_API_KEY is not configured")
            try:
                import google.generativeai as genai
                genai.configure(api_key=settings.GOOGLE_API_KEY)
                self._model = genai.GenerativeModel(
                    model_name=settings.GEMINI_MODEL,
                    system_instruction=SYSTEM_PROMPT,
                )
                self._initialized = True
            except ImportError:
                raise RuntimeError("google-generativeai package not installed")
        return self._model

    async def _call_gemini(self, user_prompt: str) -> tuple[str, int]:
        """Single Gemini call, returns (response_text, tokens_used)."""
        model = self._get_model()

        try:
            response = await model.generate_content_async(
                user_prompt,
                generation_config={
                    "max_output_tokens": settings.GEMINI_MAX_TOKENS,
                    "temperature": 0.7,
                },
            )

            response_text = response.text
            tokens_used = response.usage_metadata.total_token_count if response.usage_metadata else 0

            logger.debug(
                "Gemini API call successful",
                tokens=tokens_used,
                model=settings.GEMINI_MODEL,
            )

            return response_text, tokens_used

        except Exception as e:
            logger.error("Gemini API call failed", error=str(e))
            raise

    async def get_hint(
        self,
        board: chess.Board,
        player_color: str,
        move_history: list[str],
        difficulty: str,
    ) -> dict:
        """Get a strategic hint for the current position."""
        legal_moves_san = [board.san(m) for m in board.legal_moves]

        prompt = hint_prompt(
            fen=board.fen(),
            player_color=player_color,
            move_history=move_history,
            difficulty=difficulty,
            legal_moves_san=legal_moves_san,
        )

        response, tokens = await self._call_gemini(prompt)

        concept = _extract_concept(response)
        suggested_move_uci = _extract_suggested_move(response, board)

        return {
            "hint": response,
            "suggested_concept": concept,
            "suggested_move_uci": suggested_move_uci,
            "tokens_used": tokens,
        }

    async def explain_last_move(
        self,
        board: chess.Board,
        ai_move: str,
        ai_move_san: str,
        move_history: list[str],
        difficulty: str,
    ) -> dict:
        """Explain the AI's last move."""
        prompt = explain_last_move_prompt(
            fen=board.fen(),
            ai_move=ai_move,
            ai_move_san=ai_move_san,
            move_history=move_history,
            difficulty=difficulty,
        )

        response, tokens = await self._call_gemini(prompt)
        themes = _extract_themes(response)

        return {
            "explanation": response,
            "themes": themes,
            "tokens_used": tokens,
        }

    async def postgame_summary(
        self,
        pgn: str,
        difficulty: str,
        player_color: str,
        result: str,
    ) -> dict:
        """Full game recap — what went well, what didn't."""
        prompt = postgame_summary_prompt(
            pgn=pgn,
            difficulty=difficulty,
            player_color=player_color,
            result=result,
        )

        response, tokens = await self._call_gemini(prompt)

        return {
            "summary": response,
            "mistakes": [],
            "key_moments": [],
            "improvement_areas": [],
            "opening_name": _extract_opening_name(response),
            "tokens_used": tokens,
        }

    async def chat(
        self,
        message: str,
        fen: str,
        move_history: list[str],
        context: str,
    ) -> dict:
        """Free-form coaching chat."""
        prompt = chat_prompt(
            message=message,
            fen=fen,
            move_history=move_history,
            context=context,
        )

        response, tokens = await self._call_gemini(prompt)

        return {
            "response": response,
            "tokens_used": tokens,
        }


# ─────────────────────────────────────────────────────────────
# Response parsing helpers
# ─────────────────────────────────────────────────────────────

_CHESS_CONCEPTS = [
    "development", "center control", "king safety", "pawn structure",
    "piece activity", "open file", "outpost", "pin", "fork", "skewer",
    "discovered attack", "zwischenzug", "tempo", "initiative", "zugzwang",
    "endgame technique", "promotion", "exchange", "sacrifice",
]

_OPENING_KEYWORDS = {
    "Italian Game": ["italian", "giuoco piano", "bc4"],
    "Ruy López": ["ruy lopez", "spanish", "bb5"],
    "Sicilian Defense": ["sicilian"],
    "French Defense": ["french"],
    "Caro-Kann": ["caro-kann", "caro kann"],
    "King's Indian Defense": ["king's indian", "kings indian"],
    "Queen's Gambit": ["queen's gambit"],
    "English Opening": ["english opening"],
    "Nimzo-Indian": ["nimzo-indian", "nimzo indian"],
    "Pirc Defense": ["pirc"],
}


def _extract_concept(text: str) -> str:
    text_lower = text.lower()
    for concept in _CHESS_CONCEPTS:
        if concept in text_lower:
            return concept.title()
    return "Positional Play"


def _extract_themes(text: str) -> list[str]:
    text_lower = text.lower()
    found = []
    for concept in _CHESS_CONCEPTS:
        if concept in text_lower:
            found.append(concept.title())
        if len(found) >= 3:
            break
    return found or ["Strategy"]


def _extract_opening_name(text: str) -> str:
    text_lower = text.lower()
    for opening_name, keywords in _OPENING_KEYWORDS.items():
        if any(kw in text_lower for kw in keywords):
            return opening_name
    return "Unknown Opening"


def _extract_suggested_move(text: str, board: chess.Board) -> str | None:
    """Parse the MOVE: field from a hint response and validate it is legal."""
    for line in text.split("\n"):
        stripped = line.strip()
        if stripped.upper().startswith("MOVE:"):
            move_text = stripped.split(":", 1)[1].strip().split()[0].rstrip(".,;")  # strip trailing punctuation
            # Try SAN
            try:
                move = board.parse_san(move_text)
                return move.uci()
            except Exception:
                pass
            # Try UCI
            try:
                move = chess.Move.from_uci(move_text)
                if move in board.legal_moves:
                    return move_text
            except Exception:
                pass
    return None
