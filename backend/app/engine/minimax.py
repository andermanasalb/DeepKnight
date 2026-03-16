"""
Pure Minimax search (without alpha-beta pruning).

Used for very shallow depths (Easy mode with depth=2) where the
overhead of alpha-beta is minimal and code clarity matters more.
"""

from typing import Optional

import chess

from app.engine.evaluation import ClassicalEvaluator

INF = float("inf")
NEG_INF = float("-inf")

evaluator = ClassicalEvaluator()


def minimax(
    board: chess.Board,
    depth: int,
    maximizing: bool,
) -> float:
    """
    Classic minimax algorithm without pruning.

    Args:
        board: Current board position
        depth: Remaining search depth
        maximizing: True if current player is White (maximizer)

    Returns:
        float: Best achievable score from this position
    """
    if board.is_game_over() or depth == 0:
        score = evaluator.evaluate(board)
        return score

    if maximizing:
        best = NEG_INF
        for move in board.legal_moves:
            board.push(move)
            score = minimax(board, depth - 1, False)
            board.pop()
            best = max(best, score)
        return best
    else:
        best = INF
        for move in board.legal_moves:
            board.push(move)
            score = minimax(board, depth - 1, True)
            board.pop()
            best = min(best, score)
        return best


def minimax_best_move(board: chess.Board, depth: int) -> tuple[Optional[chess.Move], float]:
    """
    Find the best move using minimax.

    Returns:
        Tuple of (best_move, best_score)
    """
    if board.is_game_over():
        return None, 0.0

    is_maximizing = board.turn == chess.WHITE
    best_score = NEG_INF if is_maximizing else INF
    best_move = None

    for move in board.legal_moves:
        board.push(move)
        score = minimax(board, depth - 1, not is_maximizing)
        board.pop()

        if is_maximizing:
            if score > best_score:
                best_score = score
                best_move = move
        else:
            if score < best_score:
                best_score = score
                best_move = move

    return best_move, best_score
