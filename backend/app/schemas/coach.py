"""
Pydantic v2 schemas for coaching endpoints.
"""

from pydantic import BaseModel, Field


class HintRequest(BaseModel):
    fen: str = Field(..., description="Current board FEN")
    player_color: str = Field(default="white", description="'white' or 'black'")
    move_history: list[str] = Field(default_factory=list, description="UCI move history")
    difficulty: str = Field(default="medium")


class HintResponse(BaseModel):
    hint: str
    suggested_concept: str
    suggested_move_uci: str | None = None
    tokens_used: int


class ExplainMoveRequest(BaseModel):
    fen: str = Field(..., description="Board FEN after AI's move")
    ai_move: str = Field(..., description="AI's move in UCI format")
    ai_move_san: str = Field(..., description="AI's move in SAN format")
    move_history: list[str] = Field(default_factory=list)
    difficulty: str = Field(default="medium")


class ExplainMoveResponse(BaseModel):
    explanation: str
    themes: list[str]
    tokens_used: int


class MistakeInfo(BaseModel):
    move_number: int
    move: str
    issue: str
    severity: str  # "blunder", "mistake", "inaccuracy"


class PostGameRequest(BaseModel):
    pgn: str = Field(..., description="Full game PGN")
    difficulty: str = Field(default="medium")
    player_color: str = Field(default="white")
    result: str = Field(default="unknown", description="'white_wins', 'black_wins', 'draw'")


class PostGameResponse(BaseModel):
    summary: str
    mistakes: list[MistakeInfo]
    key_moments: list[str]
    improvement_areas: list[str]
    opening_name: str
    tokens_used: int


class ChatRequest(BaseModel):
    message: str = Field(..., description="User's free-form message to the coach")
    fen: str = Field(default="", description="Current board FEN (optional)")
    move_history: list[str] = Field(default_factory=list)
    context: str = Field(default="", description="Additional context for the coach")


class ChatResponse(BaseModel):
    response: str
    tokens_used: int
