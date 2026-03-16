"""
Analysis API routes — position evaluation (classical + neural).
"""

import chess
from fastapi import APIRouter, HTTPException, status

from app.api.deps import Predictor
from app.engine.evaluation import ClassicalEvaluator
from app.schemas.analysis import EvaluateRequest, EvaluateResponse

router = APIRouter()
evaluator = ClassicalEvaluator()


@router.post("/evaluate", response_model=EvaluateResponse)
async def evaluate_position(
    request: EvaluateRequest,
    predictor: Predictor,
) -> EvaluateResponse:
    """
    Evaluate a board position using both the classical engine
    and the PyTorch ValueNet model.
    """
    try:
        board = chess.Board(request.fen)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid FEN: {e}",
        )

    classical_score = evaluator.evaluate(board) / 100.0
    material_balance = evaluator.material_balance(board) / 100.0

    pytorch_score = 0.0
    if predictor.is_loaded:
        pytorch_score = predictor.predict(board)

    # Detect game phase
    phase = _detect_phase(board)

    return EvaluateResponse(
        classical_score=round(classical_score, 4),
        pytorch_score=round(pytorch_score, 4),
        turn="white" if board.turn == chess.WHITE else "black",
        material_balance=round(material_balance, 4),
        phase=phase,
        is_check=board.is_check(),
        legal_move_count=len(list(board.legal_moves)),
    )


def _detect_phase(board: chess.Board) -> str:
    """Simple phase detection based on material remaining."""
    queens = len(board.pieces(chess.QUEEN, chess.WHITE)) + len(
        board.pieces(chess.QUEEN, chess.BLACK)
    )
    minor_pieces = (
        len(board.pieces(chess.KNIGHT, chess.WHITE))
        + len(board.pieces(chess.BISHOP, chess.WHITE))
        + len(board.pieces(chess.KNIGHT, chess.BLACK))
        + len(board.pieces(chess.BISHOP, chess.BLACK))
    )
    rooks = (
        len(board.pieces(chess.ROOK, chess.WHITE))
        + len(board.pieces(chess.ROOK, chess.BLACK))
    )

    total_material = queens * 9 + minor_pieces * 3 + rooks * 5

    if board.fullmove_number <= 10:
        return "opening"
    elif total_material <= 15:
        return "endgame"
    else:
        return "middlegame"
