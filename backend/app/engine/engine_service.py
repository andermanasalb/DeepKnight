"""
Engine service — the main interface for computing AI moves.

Selects the appropriate search algorithm and depth based on
difficulty, integrates the PyTorch predictor for Hard mode,
and applies optional randomness for Easy mode.
"""

import random
from typing import Optional

import chess

from app.engine.alphabeta import AlphaBetaEngine
from app.engine.levels import DifficultyLevel, get_level
from app.engine.minimax import minimax_best_move
from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


class EngineService:
    """
    High-level chess engine interface.

    Instantiate with a difficulty string and optional model predictor,
    then call `get_best_move(board)` to get the engine's response.
    """

    def __init__(self, difficulty: str = "medium", predictor=None):
        self.level: DifficultyLevel = get_level(difficulty)
        self.predictor = predictor
        logger.debug(
            "EngineService initialized",
            difficulty=difficulty,
            depth=self.level.depth,
            use_neural=self.level.use_neural,
        )

    def get_best_move(self, board: chess.Board) -> tuple[Optional[chess.Move], int]:
        """
        Compute the best move for the current side to move.

        Returns:
            Tuple of (best_move, depth_used)
        """
        if board.is_game_over():
            return None, 0

        # Easy mode: use lightweight minimax, possibly pick a suboptimal move
        if self.level.name == "easy":
            return self._easy_move(board)

        # Medium / Hard: use alpha-beta with optional neural blending
        return self._alpha_beta_move(board)

    def _easy_move(self, board: chess.Board) -> tuple[Optional[chess.Move], int]:
        """
        Easy mode: shallow minimax with occasional random move selection.
        """
        best_move, _ = minimax_best_move(board, depth=self.level.depth)

        # Occasionally pick a random legal move (makes Easy beatable)
        if random.random() < self.level.random_factor:
            legal = list(board.legal_moves)
            if legal:
                best_move = random.choice(legal)

        return best_move, self.level.depth

    def _alpha_beta_move(self, board: chess.Board) -> tuple[Optional[chess.Move], int]:
        """
        Medium/Hard mode: alpha-beta negamax with move ordering
        and optional PyTorch neural evaluation blending.
        """
        neural_fn = None
        neural_weight = 0.0

        if self.level.use_neural and self.predictor is not None and self.predictor.is_loaded:
            neural_fn = self.predictor.predict
            neural_weight = self.level.neural_weight

        engine = AlphaBetaEngine(
            depth=self.level.depth,
            use_ordering=self.level.use_move_ordering,
            neural_fn=neural_fn,
            neural_weight=neural_weight,
            timeout=float(settings.ENGINE_TIMEOUT_SECONDS),
        )

        best_move, score = engine.search(board)

        logger.debug(
            "Engine search complete",
            move=best_move.uci() if best_move else None,
            score=score,
            nodes=engine.nodes_searched,
            depth=self.level.depth,
        )

        return best_move, self.level.depth
