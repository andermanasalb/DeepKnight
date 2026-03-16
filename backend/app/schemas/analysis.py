"""
Pydantic v2 schemas for analysis endpoints.
"""

from pydantic import BaseModel, Field


class EvaluateRequest(BaseModel):
    fen: str = Field(..., description="Board position in FEN notation")


class EvaluateResponse(BaseModel):
    classical_score: float = Field(..., description="Classical engine score (centipawns / 100)")
    pytorch_score: float = Field(..., description="Neural network score in [-1, 1]")
    turn: str = Field(..., description="'white' or 'black'")
    material_balance: float = Field(..., description="Raw material balance (centipawns / 100)")
    phase: str = Field(..., description="'opening', 'middlegame', or 'endgame'")
    is_check: bool
    legal_move_count: int
