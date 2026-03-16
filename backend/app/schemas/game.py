"""
Pydantic v2 schemas for game-related API endpoints.
"""

from pydantic import BaseModel, Field, field_validator


class NewGameRequest(BaseModel):
    difficulty: str = Field(default="medium", description="Engine difficulty level")

    @field_validator("difficulty")
    @classmethod
    def validate_difficulty(cls, v: str) -> str:
        allowed = {"easy", "medium", "hard"}
        if v.lower() not in allowed:
            raise ValueError(f"difficulty must be one of {allowed}")
        return v.lower()


class NewGameResponse(BaseModel):
    game_id: str
    fen: str
    turn: str
    difficulty: str
    legal_moves: list[str]


class MakeMoveRequest(BaseModel):
    fen: str = Field(..., description="Current board FEN")
    move_uci: str = Field(..., description="Human move in UCI format, e.g. 'e2e4'")
    difficulty: str = Field(default="medium", description="Engine difficulty level")
    move_history: list[str] = Field(default_factory=list, description="Previous moves in UCI")

    @field_validator("difficulty")
    @classmethod
    def validate_difficulty(cls, v: str) -> str:
        allowed = {"easy", "medium", "hard"}
        if v.lower() not in allowed:
            raise ValueError(f"difficulty must be one of {allowed}")
        return v.lower()


class AnalysisInfo(BaseModel):
    classical_score: float
    pytorch_score: float
    depth_searched: int


class MakeMoveResponse(BaseModel):
    player_move: str
    player_move_san: str
    ai_move: str | None
    ai_move_san: str | None
    fen: str
    turn: str
    is_check: bool
    is_checkmate: bool
    is_stalemate: bool
    is_game_over: bool
    game_over_reason: str | None
    pgn: str
    legal_moves: list[str]
    analysis: dict


class BestMoveResponse(BaseModel):
    best_move: str
    best_move_san: str
    score: float
    depth: int
    nodes_searched: int
