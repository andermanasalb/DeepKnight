"""
Move ordering for alpha-beta pruning efficiency.

Better move ordering = more cutoffs = faster search.

Ordering priority:
  1. Captures (MVV-LVA: Most Valuable Victim, Least Valuable Attacker)
  2. Promotions
  3. Checks
  4. Killer moves (moves that caused beta cutoffs at the same depth)
  5. Remaining moves by PST change
"""

import chess

from app.engine.evaluation import PIECE_VALUES

# Sentinel value for moves not yet scored
_UNSCORED = -9999999

# Weights for move ordering categories
CAPTURE_BASE = 10000
PROMOTION_BONUS = 9000
CHECK_BONUS = 5000


def mvv_lva_score(board: chess.Board, move: chess.Move) -> int:
    """
    Most Valuable Victim – Least Valuable Attacker score.
    Higher = search this capture first.
    """
    if not board.is_capture(move):
        return 0

    victim_square = move.to_square
    attacker_square = move.from_square

    victim = board.piece_at(victim_square)
    attacker = board.piece_at(attacker_square)

    if victim is None:
        # En passant capture — victim is a pawn
        victim_value = PIECE_VALUES[chess.PAWN]
    else:
        victim_value = PIECE_VALUES.get(victim.piece_type, 0)

    attacker_value = PIECE_VALUES.get(attacker.piece_type if attacker else chess.PAWN, 100)

    # High victim value, low attacker value → better move
    return CAPTURE_BASE + victim_value * 10 - attacker_value


def score_move(board: chess.Board, move: chess.Move, killer_moves: set | None = None) -> int:
    """
    Score a single move for ordering purposes.
    Higher score = search earlier.
    """
    score = 0

    # 1. Captures (MVV-LVA)
    if board.is_capture(move):
        score += mvv_lva_score(board, move)

    # 2. Promotions
    if move.promotion is not None:
        promo_value = PIECE_VALUES.get(move.promotion, 0)
        score += PROMOTION_BONUS + promo_value

    # 3. Killer moves (non-captures that caused cutoffs at this depth)
    if killer_moves and move in killer_moves:
        score += CHECK_BONUS

    # 4. Check bonus
    board.push(move)
    if board.is_check():
        score += CHECK_BONUS // 2
    board.pop()

    return score


def order_moves(
    board: chess.Board,
    moves: list[chess.Move],
    killer_moves: set | None = None,
) -> list[chess.Move]:
    """
    Sort moves by heuristic score (descending — best first).

    Args:
        board: Current board state
        moves: List of legal moves to order
        killer_moves: Set of killer moves at this depth

    Returns:
        Sorted list of moves
    """
    return sorted(
        moves,
        key=lambda m: score_move(board, m, killer_moves),
        reverse=True,
    )
