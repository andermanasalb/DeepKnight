"""
Coach API routes — generative AI coaching powered by Google Gemini.
"""

import chess
from fastapi import APIRouter, HTTPException, status

from app.genai.coach_service import CoachService
from app.schemas.coach import (
    ChatRequest,
    ChatResponse,
    ExplainMoveRequest,
    ExplainMoveResponse,
    HintRequest,
    HintResponse,
    PostGameRequest,
    PostGameResponse,
)

router = APIRouter()
coach_service = CoachService()


@router.post("/hint", response_model=HintResponse)
async def get_hint(request: HintRequest) -> HintResponse:
    """
    Get a strategic hint for the current position from the AI coach.
    The hint explains concepts without giving the exact move.
    """
    try:
        board = chess.Board(request.fen)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid FEN: {e}",
        )

    if not coach_service.is_available:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Coaching service unavailable — GOOGLE_API_KEY not configured",
        )

    result = await coach_service.get_hint(
        board=board,
        player_color=request.player_color,
        move_history=request.move_history,
        difficulty=request.difficulty,
    )

    return HintResponse(
        hint=result["hint"],
        suggested_concept=result.get("suggested_concept", ""),
        suggested_move_uci=result.get("suggested_move_uci"),
        tokens_used=result.get("tokens_used", 0),
    )


@router.post("/explain", response_model=ExplainMoveResponse)
async def explain_move(request: ExplainMoveRequest) -> ExplainMoveResponse:
    """
    Explain the AI's last move in plain English.
    Helps the user understand the engine's strategy.
    """
    try:
        board = chess.Board(request.fen)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid FEN: {e}",
        )

    if not coach_service.is_available:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Coaching service unavailable — GOOGLE_API_KEY not configured",
        )

    result = await coach_service.explain_last_move(
        board=board,
        ai_move=request.ai_move,
        ai_move_san=request.ai_move_san,
        move_history=request.move_history,
        difficulty=request.difficulty,
    )

    return ExplainMoveResponse(
        explanation=result["explanation"],
        themes=result.get("themes", []),
        tokens_used=result.get("tokens_used", 0),
    )


@router.post("/postgame", response_model=PostGameResponse)
async def postgame_analysis(request: PostGameRequest) -> PostGameResponse:
    """
    Generate a comprehensive post-game analysis with mistake identification.
    """
    if not coach_service.is_available:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Coaching service unavailable — GOOGLE_API_KEY not configured",
        )

    result = await coach_service.postgame_summary(
        pgn=request.pgn,
        difficulty=request.difficulty,
        player_color=request.player_color,
        result=request.result,
    )

    return PostGameResponse(
        summary=result["summary"],
        mistakes=result.get("mistakes", []),
        key_moments=result.get("key_moments", []),
        improvement_areas=result.get("improvement_areas", []),
        opening_name=result.get("opening_name", "Unknown Opening"),
        tokens_used=result.get("tokens_used", 0),
    )


@router.post("/chat", response_model=ChatResponse)
async def coach_chat(request: ChatRequest) -> ChatResponse:
    """
    Free-form coaching chat about the current game or chess in general.
    """
    if not coach_service.is_available:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Coaching service unavailable — GOOGLE_API_KEY not configured",
        )

    result = await coach_service.chat(
        message=request.message,
        fen=request.fen,
        move_history=request.move_history,
        context=request.context,
    )

    return ChatResponse(
        response=result["response"],
        tokens_used=result.get("tokens_used", 0),
    )
