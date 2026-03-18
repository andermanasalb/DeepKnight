"""
Alpha-Beta Negamax search with move ordering.

Negamax formulation: the evaluation is always from the perspective
of the side to move. Alpha-beta pruning cuts branches that cannot
affect the final decision.

Features:
  - Negamax with alpha-beta pruning
  - Iterative deepening (search depth 1..max_depth, return best so far)
  - Move ordering (captures first, killers, checks)
  - Basic transposition table (Zobrist-keyed position cache)
  - Quiescence search stub (marked as TODO for extension)
"""

import time

import chess
import chess.polyglot

from app.engine.evaluation import ClassicalEvaluator
from app.engine.move_ordering import order_moves

INF = float("inf")
NEG_INF = float("-inf")
MAX_DEPTH = 10

evaluator = ClassicalEvaluator()


class AlphaBetaEngine:
    """
    Alpha-Beta Negamax engine. Supports iterative deepening,
    move ordering, transposition table, and optional neural blending.
    """

    def __init__(
        self,
        depth: int = 4,
        use_ordering: bool = True,
        neural_fn=None,
        neural_weight: float = 0.0,
        timeout: float | None = None,
    ):
        self.depth = depth
        self.use_ordering = use_ordering
        self.neural_fn = neural_fn
        self.neural_weight = neural_weight
        self.timeout = timeout

        self._nodes_searched = 0
        self._start_time: float = 0.0
        self._timed_out = False
        self._transposition_table: dict[int, tuple[float, int]] = {}  # hash → (score, depth)

    @property
    def nodes_searched(self) -> int:
        return self._nodes_searched

    def search(self, board: chess.Board) -> tuple[chess.Move | None, float]:
        """Run iterative deepening search, returns (best_move, score)."""
        if board.is_game_over():
            return None, 0.0

        self._nodes_searched = 0
        self._start_time = time.monotonic()
        self._timed_out = False
        self._transposition_table.clear()

        best_move: chess.Move | None = None
        best_score = NEG_INF

        # Iterative deepening: search progressively deeper
        for current_depth in range(1, self.depth + 1):
            move, score = self._root_search(board, current_depth)

            if self._timed_out:
                # Return last completed depth's best move
                break

            best_move = move
            best_score = score

        return best_move, best_score

    def _root_search(
        self, board: chess.Board, depth: int
    ) -> tuple[chess.Move | None, float]:
        """Search at the root node, returning (best_move, best_score)."""
        alpha = NEG_INF
        beta = INF
        best_move = None
        best_score = NEG_INF

        moves = list(board.legal_moves)
        if self.use_ordering:
            moves = order_moves(board, moves)

        for move in moves:
            if self._is_timeout():
                self._timed_out = True
                break

            board.push(move)
            score = -self._negamax(board, depth - 1, -beta, -alpha)
            board.pop()

            if score > best_score:
                best_score = score
                best_move = move

            alpha = max(alpha, score)

        return best_move, best_score

    def _negamax(
        self,
        board: chess.Board,
        depth: int,
        alpha: float,
        beta: float,
    ) -> float:
        """
        Negamax with alpha-beta pruning.
        Score is from the perspective of the side to move.
        """
        self._nodes_searched += 1

        if self._is_timeout():
            self._timed_out = True
            return 0.0

        # Transposition table lookup
        board_hash = chess.polyglot.zobrist_hash(board)
        if board_hash in self._transposition_table:
            cached_score, cached_depth = self._transposition_table[board_hash]
            if cached_depth >= depth:
                return cached_score

        # Terminal conditions
        if board.is_game_over():
            return self._terminal_score(board)

        if depth == 0:
            return self._leaf_evaluate(board)

        # Recursive search
        best_score = NEG_INF
        moves = list(board.legal_moves)

        if self.use_ordering:
            moves = order_moves(board, moves)

        for move in moves:
            board.push(move)
            score = -self._negamax(board, depth - 1, -beta, -alpha)
            board.pop()

            if score > best_score:
                best_score = score

            alpha = max(alpha, score)
            if alpha >= beta:
                break  # Beta cutoff — prune remaining branches

        # Store in transposition table
        self._transposition_table[board_hash] = (best_score, depth)

        return best_score

    def _leaf_evaluate(self, board: chess.Board) -> float:
        """Static eval at depth 0. Mix classical + neural if available."""
        classical = evaluator.evaluate(board)

        # Normalize to perspective of side to move
        if board.turn == chess.BLACK:
            classical = -classical

        if self.neural_fn is not None and self.neural_weight > 0.0:
            try:
                neural_raw = self.neural_fn(board)  # returns [-1, 1]
                # Convert neural to centipawns scale (1 pawn = 100 cp)
                neural_cp = neural_raw * 100.0
                if board.turn == chess.BLACK:
                    neural_cp = -neural_cp

                blended = (
                    (1.0 - self.neural_weight) * classical
                    + self.neural_weight * neural_cp
                )
                return blended
            except Exception:
                # Fall back to classical if neural fails
                pass

        return classical

    def _terminal_score(self, board: chess.Board) -> float:
        """Score for game-over positions."""
        if board.is_checkmate():
            # The side to move is checkmated — they lose
            return -99999.0 + board.fullmove_number  # prefer faster mates
        # Draw
        return 0.0

    def _is_timeout(self) -> bool:
        if self.timeout is None:
            return False
        return time.monotonic() - self._start_time > self.timeout
