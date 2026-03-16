"""
GameManager — higher-level game state management.

Wraps python-chess Board with additional bookkeeping:
- game metadata (difficulty, timestamps, player colors)
- move history tracking
- game state serialization
"""

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional

import chess
import chess.pgn


@dataclass
class GameState:
    game_id: str
    board: chess.Board
    difficulty: str
    player_color: chess.Color
    move_history_uci: list[str]
    created_at: datetime
    updated_at: datetime
    status: str  # "in_progress", "white_wins", "black_wins", "draw"

    @property
    def fen(self) -> str:
        return self.board.fen()

    @property
    def pgn(self) -> str:
        return _board_to_pgn(self.board, self.move_history_uci, self.difficulty)

    @property
    def legal_moves(self) -> list[str]:
        return [m.uci() for m in self.board.legal_moves]

    @property
    def turn(self) -> str:
        return "white" if self.board.turn == chess.WHITE else "black"


class GameManager:
    """
    Manages the creation and state of chess games.
    In-memory for development; integrate with DB for production.
    """

    def __init__(self):
        self._games: dict[str, GameState] = {}

    def new_game(
        self,
        difficulty: str = "medium",
        player_color: str = "white",
    ) -> GameState:
        """Create and store a new game."""
        game_id = str(uuid.uuid4())
        now = datetime.now(timezone.utc)

        color = chess.WHITE if player_color.lower() == "white" else chess.BLACK

        state = GameState(
            game_id=game_id,
            board=chess.Board(),
            difficulty=difficulty,
            player_color=color,
            move_history_uci=[],
            created_at=now,
            updated_at=now,
            status="in_progress",
        )
        self._games[game_id] = state
        return state

    def get_game(self, game_id: str) -> Optional[GameState]:
        return self._games.get(game_id)

    def apply_move(self, game_id: str, move_uci: str) -> Optional[GameState]:
        """
        Apply a move to a game. Returns updated state or None if game not found.
        Raises ValueError for illegal moves.
        """
        state = self._games.get(game_id)
        if state is None:
            return None

        move = chess.Move.from_uci(move_uci)
        if move not in state.board.legal_moves:
            raise ValueError(f"Illegal move: {move_uci}")

        state.board.push(move)
        state.move_history_uci.append(move_uci)
        state.updated_at = datetime.now(timezone.utc)

        # Update status
        if state.board.is_game_over():
            state.status = _determine_outcome(state.board)

        return state


def _determine_outcome(board: chess.Board) -> str:
    if board.is_checkmate():
        return "black_wins" if board.turn == chess.WHITE else "white_wins"
    return "draw"


def _board_to_pgn(board: chess.Board, move_history: list[str], difficulty: str) -> str:
    """Reconstruct PGN from move history."""
    try:
        replay = chess.Board()
        game = chess.pgn.Game()
        game.headers["White"] = "Human"
        game.headers["Black"] = f"DeepKnight ({difficulty.title()})"

        node = game
        for uci in move_history:
            move = chess.Move.from_uci(uci)
            if move in replay.legal_moves:
                node = node.add_variation(move)
                replay.push(move)

        import io
        output = io.StringIO()
        exporter = chess.pgn.FileExporter(output)
        game.accept(exporter)
        return output.getvalue()
    except Exception:
        return ""
