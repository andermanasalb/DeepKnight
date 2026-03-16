"""
Game routes: start a game, play a move, ask for the best move.
"""

import uuid

import chess
from fastapi import APIRouter, HTTPException, Query, status

from app.api.deps import DBSession, Predictor
from app.chess.game_manager import GameManager
from app.engine.engine_service import EngineService
from app.engine.evaluation import ClassicalEvaluator
from app.schemas.game import (
    BestMoveResponse,
    MakeMoveRequest,
    MakeMoveResponse,
    NewGameRequest,
    NewGameResponse,
)

router = APIRouter()
game_manager = GameManager()
evaluator = ClassicalEvaluator()


@router.post("/new_game", response_model=NewGameResponse, status_code=status.HTTP_201_CREATED)
async def new_game(
    request: NewGameRequest,
    db: DBSession,
) -> NewGameResponse:
    """Start a new game. Player is White."""
    game_id = str(uuid.uuid4())
    board = chess.Board()

    legal_moves = [move.uci() for move in board.legal_moves]

    return NewGameResponse(
        game_id=game_id,
        fen=board.fen(),
        turn="white",
        difficulty=request.difficulty,
        legal_moves=legal_moves,
    )


@router.post("/make_move", response_model=MakeMoveResponse)
async def make_move(
    request: MakeMoveRequest,
    predictor: Predictor,
) -> MakeMoveResponse:
    """Play your move, wait for the engine to respond, get the new board state."""
    # Parse board from FEN
    try:
        board = chess.Board(request.fen)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid FEN: {e}",
        )

    if board.is_game_over():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Game is already over",
        )

    # Validate and apply human move
    try:
        player_move = chess.Move.from_uci(request.move_uci)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid move format: {request.move_uci}",
        )

    if player_move not in board.legal_moves:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Illegal move: {request.move_uci}",
        )

    player_move_san = board.san(player_move)
    board.push(player_move)

    # Check game state after human move
    if board.is_game_over():
        return _build_response(
            board=board,
            player_move=request.move_uci,
            player_move_san=player_move_san,
            ai_move=None,
            ai_move_san=None,
            move_history=request.move_history,
            predictor=predictor,
            difficulty=request.difficulty,
        )

    # Compute AI response
    engine = EngineService(difficulty=request.difficulty, predictor=predictor)
    ai_move_obj, depth_searched = engine.get_best_move(board)

    ai_move_san = board.san(ai_move_obj)
    ai_move_uci = ai_move_obj.uci()
    board.push(ai_move_obj)

    return _build_response(
        board=board,
        player_move=request.move_uci,
        player_move_san=player_move_san,
        ai_move=ai_move_uci,
        ai_move_san=ai_move_san,
        move_history=request.move_history,
        predictor=predictor,
        difficulty=request.difficulty,
        depth_searched=depth_searched,
    )


@router.get("/best_move", response_model=BestMoveResponse)
async def best_move(
    predictor: Predictor,
    fen: str = Query(..., description="FEN string of current position"),
    difficulty: str = Query("medium", description="Engine difficulty"),
) -> BestMoveResponse:
    """Return the engine's best move for a given position (read-only, doesn't change game state)."""
    try:
        board = chess.Board(fen)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid FEN: {e}",
        )

    if board.is_game_over():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Game is already over — no best move",
        )

    engine = EngineService(difficulty=difficulty, predictor=predictor)
    move_obj, depth_searched = engine.get_best_move(board)

    move_san = board.san(move_obj)
    classical_score = evaluator.evaluate(board) / 100.0

    return BestMoveResponse(
        best_move=move_obj.uci(),
        best_move_san=move_san,
        score=classical_score,
        depth=depth_searched,
        nodes_searched=0,  # TODO: instrument node count in engine
    )


# ─────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────


def _game_over_reason(board: chess.Board) -> str | None:
    if board.is_checkmate():
        return "checkmate"
    if board.is_stalemate():
        return "stalemate"
    if board.is_insufficient_material():
        return "insufficient_material"
    if board.is_seventyfive_moves():
        return "seventy_five_moves"
    if board.is_fivefold_repetition():
        return "fivefold_repetition"
    return None


def _build_pgn(move_history: list[str], board_after: chess.Board) -> str:
    """Reconstruct a simple PGN from move history."""
    try:
        replay = chess.Board()
        game_board = chess.pgn.Game()
        node = game_board
        for uci in move_history:
            move = chess.Move.from_uci(uci)
            if move in replay.legal_moves:
                node = node.add_variation(move)
                replay.push(move)
        # Include the current board moves too
        import io
        return str(game_board)
    except Exception:
        return ""


def _build_response(
    board: chess.Board,
    player_move: str,
    player_move_san: str,
    ai_move: str | None,
    ai_move_san: str | None,
    move_history: list[str],
    predictor,
    difficulty: str,
    depth_searched: int = 0,
) -> MakeMoveResponse:
    from app.engine.evaluation import ClassicalEvaluator

    eval_obj = ClassicalEvaluator()
    classical_score = eval_obj.evaluate(board) / 100.0

    pytorch_score = 0.0
    if predictor.is_loaded:
        pytorch_score = predictor.predict(board)

    legal_moves = [m.uci() for m in board.legal_moves]

    # Build updated move history
    updated_history = list(move_history) if move_history else []
    updated_history.append(player_move)
    if ai_move:
        updated_history.append(ai_move)

    return MakeMoveResponse(
        player_move=player_move,
        player_move_san=player_move_san,
        ai_move=ai_move,
        ai_move_san=ai_move_san,
        fen=board.fen(),
        turn="white" if board.turn == chess.WHITE else "black",
        is_check=board.is_check(),
        is_checkmate=board.is_checkmate(),
        is_stalemate=board.is_stalemate(),
        is_game_over=board.is_game_over(),
        game_over_reason=_game_over_reason(board),
        pgn=_build_pgn(updated_history, board),
        legal_moves=legal_moves,
        analysis={
            "classical_score": round(classical_score, 4),
            "pytorch_score": round(pytorch_score, 4),
            "depth_searched": depth_searched,
        },
    )
