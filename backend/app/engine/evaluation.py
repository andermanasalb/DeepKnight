"""
Classical chess position evaluation.

Evaluates positions using:
  1. Material counting with standard piece values
  2. Piece-square tables (PST) for positional bonuses
  3. Mobility (number of legal moves)
  4. King safety heuristic
  5. Phase-aware blended evaluation

Score convention:
  Positive = White is better
  Negative = Black is better
  Units: centipawns (100 = 1 pawn)
"""

import chess

# ─────────────────────────────────────────────────────────────
# Material values (centipawns)
# ─────────────────────────────────────────────────────────────
PIECE_VALUES = {
    chess.PAWN: 100,
    chess.KNIGHT: 320,
    chess.BISHOP: 330,
    chess.ROOK: 500,
    chess.QUEEN: 900,
    chess.KING: 20000,
}

# ─────────────────────────────────────────────────────────────
# Piece-square tables (from White's perspective, a1=index 0)
# Indexed as PST[rank][file] where rank 0 = rank 1 (White's back rank)
# ─────────────────────────────────────────────────────────────

PAWN_TABLE = [
     0,  0,  0,  0,  0,  0,  0,  0,
    50, 50, 50, 50, 50, 50, 50, 50,
    10, 10, 20, 30, 30, 20, 10, 10,
     5,  5, 10, 25, 25, 10,  5,  5,
     0,  0,  0, 20, 20,  0,  0,  0,
     5, -5,-10,  0,  0,-10, -5,  5,
     5, 10, 10,-20,-20, 10, 10,  5,
     0,  0,  0,  0,  0,  0,  0,  0,
]

KNIGHT_TABLE = [
   -50,-40,-30,-30,-30,-30,-40,-50,
   -40,-20,  0,  0,  0,  0,-20,-40,
   -30,  0, 10, 15, 15, 10,  0,-30,
   -30,  5, 15, 20, 20, 15,  5,-30,
   -30,  0, 15, 20, 20, 15,  0,-30,
   -30,  5, 10, 15, 15, 10,  5,-30,
   -40,-20,  0,  5,  5,  0,-20,-40,
   -50,-40,-30,-30,-30,-30,-40,-50,
]

BISHOP_TABLE = [
   -20,-10,-10,-10,-10,-10,-10,-20,
   -10,  0,  0,  0,  0,  0,  0,-10,
   -10,  0,  5, 10, 10,  5,  0,-10,
   -10,  5,  5, 10, 10,  5,  5,-10,
   -10,  0, 10, 10, 10, 10,  0,-10,
   -10, 10, 10, 10, 10, 10, 10,-10,
   -10,  5,  0,  0,  0,  0,  5,-10,
   -20,-10,-10,-10,-10,-10,-10,-20,
]

ROOK_TABLE = [
     0,  0,  0,  0,  0,  0,  0,  0,
     5, 10, 10, 10, 10, 10, 10,  5,
    -5,  0,  0,  0,  0,  0,  0, -5,
    -5,  0,  0,  0,  0,  0,  0, -5,
    -5,  0,  0,  0,  0,  0,  0, -5,
    -5,  0,  0,  0,  0,  0,  0, -5,
    -5,  0,  0,  0,  0,  0,  0, -5,
     0,  0,  0,  5,  5,  0,  0,  0,
]

QUEEN_TABLE = [
   -20,-10,-10, -5, -5,-10,-10,-20,
   -10,  0,  0,  0,  0,  0,  0,-10,
   -10,  0,  5,  5,  5,  5,  0,-10,
    -5,  0,  5,  5,  5,  5,  0, -5,
     0,  0,  5,  5,  5,  5,  0, -5,
   -10,  5,  5,  5,  5,  5,  0,-10,
   -10,  0,  5,  0,  0,  0,  0,-10,
   -20,-10,-10, -5, -5,-10,-10,-20,
]

KING_MIDDLEGAME_TABLE = [
   -30,-40,-40,-50,-50,-40,-40,-30,
   -30,-40,-40,-50,-50,-40,-40,-30,
   -30,-40,-40,-50,-50,-40,-40,-30,
   -30,-40,-40,-50,-50,-40,-40,-30,
   -20,-30,-30,-40,-40,-30,-30,-20,
   -10,-20,-20,-20,-20,-20,-20,-10,
    20, 20,  0,  0,  0,  0, 20, 20,
    20, 30, 10,  0,  0, 10, 30, 20,
]

KING_ENDGAME_TABLE = [
   -50,-40,-30,-20,-20,-30,-40,-50,
   -30,-20,-10,  0,  0,-10,-20,-30,
   -30,-10, 20, 30, 30, 20,-10,-30,
   -30,-10, 30, 40, 40, 30,-10,-30,
   -30,-10, 30, 40, 40, 30,-10,-30,
   -30,-10, 20, 30, 30, 20,-10,-30,
   -30,-30,  0,  0,  0,  0,-30,-30,
   -50,-30,-30,-30,-30,-30,-30,-50,
]

PIECE_SQUARE_TABLES = {
    chess.PAWN: PAWN_TABLE,
    chess.KNIGHT: KNIGHT_TABLE,
    chess.BISHOP: BISHOP_TABLE,
    chess.ROOK: ROOK_TABLE,
    chess.QUEEN: QUEEN_TABLE,
    chess.KING: KING_MIDDLEGAME_TABLE,  # switched to endgame dynamically
}


def _pst_score(piece_type: int, square: int, color: chess.Color, is_endgame: bool) -> int:
    """
    Look up piece-square table bonus for a given piece on a given square.
    White's tables are defined from White's perspective (rank 1 at index 0).
    Black's tables mirror them vertically.
    """
    if piece_type == chess.KING and is_endgame:
        table = KING_ENDGAME_TABLE
    else:
        table = PIECE_SQUARE_TABLES[piece_type]

    if color == chess.WHITE:
        # White: a1=0, h8=63 — table is already from White's perspective
        idx = square
    else:
        # Black: mirror vertically (flip rank)
        rank = square >> 3
        file = square & 7
        mirrored_rank = 7 - rank
        idx = mirrored_rank * 8 + file

    return table[idx]


def _is_endgame(board: chess.Board) -> bool:
    """Simple endgame detection: no queens, or both sides down to <= 1 minor piece."""
    queens = board.pieces(chess.QUEEN, chess.WHITE) | board.pieces(chess.QUEEN, chess.BLACK)
    if not queens:
        return True
    # Both sides have ≤ 1 minor piece in addition to queens → endgame
    white_minors = len(board.pieces(chess.KNIGHT, chess.WHITE)) + len(
        board.pieces(chess.BISHOP, chess.WHITE)
    )
    black_minors = len(board.pieces(chess.KNIGHT, chess.BLACK)) + len(
        board.pieces(chess.BISHOP, chess.BLACK)
    )
    return white_minors <= 1 and black_minors <= 1


class ClassicalEvaluator:
    """
    Classical positional evaluation function.

    Combines material, piece-square tables, mobility, and king safety
    into a single centipawn score.
    """

    def evaluate(self, board: chess.Board) -> float:
        """
        Evaluate the position from White's perspective.

        Returns:
            float: score in centipawns. Positive = White better, Negative = Black better.
        """
        if board.is_checkmate():
            # The side to move is in checkmate, so they lost
            return -99999 if board.turn == chess.WHITE else 99999

        if board.is_stalemate() or board.is_insufficient_material():
            return 0.0

        is_endgame = _is_endgame(board)

        score = 0.0
        score += self._material_and_pst(board, is_endgame)
        score += self._mobility(board) * 5         # 5 cp per legal move advantage
        score += self._king_safety(board, is_endgame)

        return score

    def material_balance(self, board: chess.Board) -> float:
        """Raw material balance in centipawns (positive = White ahead)."""
        score = 0
        for piece_type in [chess.PAWN, chess.KNIGHT, chess.BISHOP, chess.ROOK, chess.QUEEN]:
            score += len(board.pieces(piece_type, chess.WHITE)) * PIECE_VALUES[piece_type]
            score -= len(board.pieces(piece_type, chess.BLACK)) * PIECE_VALUES[piece_type]
        return score

    def _material_and_pst(self, board: chess.Board, is_endgame: bool) -> float:
        score = 0
        for square in chess.SQUARES:
            piece = board.piece_at(square)
            if piece is None:
                continue
            value = PIECE_VALUES[piece.piece_type]
            pst_bonus = _pst_score(piece.piece_type, square, piece.color, is_endgame)
            if piece.color == chess.WHITE:
                score += value + pst_bonus
            else:
                score -= value + pst_bonus
        return score

    def _mobility(self, board: chess.Board) -> float:
        """Mobility advantage: number of legal moves White - Black."""
        if board.turn == chess.WHITE:
            white_mobility = len(list(board.legal_moves))
            board.push(chess.Move.null())
            black_mobility = len(list(board.legal_moves))
            board.pop()
        else:
            black_mobility = len(list(board.legal_moves))
            board.push(chess.Move.null())
            white_mobility = len(list(board.legal_moves))
            board.pop()
        return white_mobility - black_mobility

    def _king_safety(self, board: chess.Board, is_endgame: bool) -> float:
        """
        Penalize exposed kings in middlegame.
        In endgame, king activity is actually positive.
        """
        if is_endgame:
            return 0.0

        score = 0.0

        for color in [chess.WHITE, chess.BLACK]:
            king_square = board.king(color)
            if king_square is None:
                continue

            # Count pawns shielding the king (within 1 rank)
            king_rank = king_square >> 3
            king_file = king_square & 7

            shield_count = 0
            for f in range(max(0, king_file - 1), min(7, king_file + 1) + 1):
                shield_rank = king_rank + (1 if color == chess.WHITE else -1)
                if 0 <= shield_rank <= 7:
                    shield_square = shield_rank * 8 + f
                    piece = board.piece_at(shield_square)
                    if piece and piece.piece_type == chess.PAWN and piece.color == color:
                        shield_count += 1

            penalty = (3 - shield_count) * 10  # up to 30 cp penalty
            if color == chess.WHITE:
                score -= penalty
            else:
                score += penalty

        return score
