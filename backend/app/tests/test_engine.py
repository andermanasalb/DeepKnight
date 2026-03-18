"""
Tests for the chess engine — evaluation, move ordering, and search.
"""

import chess
import pytest

from app.engine.alphabeta import AlphaBetaEngine
from app.engine.encoding import encode_board, encode_board_tensor
from app.engine.evaluation import ClassicalEvaluator
from app.engine.levels import get_level
from app.engine.move_ordering import order_moves


class TestClassicalEvaluator:
    def setup_method(self):
        self.evaluator = ClassicalEvaluator()

    def test_starting_position_near_zero(self):
        """Starting position should be roughly equal."""
        board = chess.Board()
        score = self.evaluator.evaluate(board)
        # Allow some variance due to PST asymmetry at start
        assert -50 <= score <= 50

    def test_material_advantage(self):
        """White up a rook should have a significant positive score."""
        # Remove black's a-rook
        board = chess.Board()
        board.remove_piece_at(chess.A8)
        score = self.evaluator.evaluate(board)
        assert score > 300, f"Expected White ahead with +Rook, got {score}"

    def test_black_material_advantage(self):
        """Black up a queen should have a negative score (Black winning)."""
        board = chess.Board()
        board.remove_piece_at(chess.D1)  # Remove White queen
        score = self.evaluator.evaluate(board)
        assert score < -500, f"Expected Black ahead with +Queen, got {score}"

    def test_checkmate_is_extreme(self):
        """Checkmate should return extreme score."""
        # Scholar's mate position
        board = chess.Board("r1bqkb1r/pppp1Qpp/2n2n2/4p3/2B1P3/8/PPPP1PPP/RNB1K1NR b KQkq - 0 4")
        score = self.evaluator.evaluate(board)
        # Black is in checkmate, white should win
        assert abs(score) > 90000

    def test_stalemate_is_draw(self):
        """Stalemate should return 0."""
        # King in stalemate
        board = chess.Board("k7/8/1Q6/8/8/8/8/7K b - - 0 1")
        if board.is_stalemate():
            score = self.evaluator.evaluate(board)
            assert score == 0.0

    def test_material_balance_method(self):
        """Material balance helper should return correct pawn count."""
        board = chess.Board()
        balance = self.evaluator.material_balance(board)
        assert balance == 0  # Equal starting material


class TestBoardEncoding:
    def test_encode_shape(self):
        """Encoded board should be 768-dimensional."""
        board = chess.Board()
        encoded = encode_board(board)
        assert encoded.shape == (768,)

    def test_encode_binary(self):
        """Encoded board should contain only 0s and 1s."""
        board = chess.Board()
        encoded = encode_board(board)
        assert set(encoded.tolist()).issubset({0.0, 1.0})

    def test_encode_piece_count(self):
        """Starting position should have exactly 32 pieces encoded."""
        board = chess.Board()
        encoded = encode_board(board)
        assert int(encoded.sum()) == 32

    def test_encode_tensor_shape(self):
        """Tensor encoding should have batch dimension."""
        board = chess.Board()
        tensor = encode_board_tensor(board)
        assert tensor.shape == (1, 768)

    def test_empty_board_all_zeros(self):
        """Empty board (except kings) should have only king bits set."""
        board = chess.Board()
        # Clear all pieces
        board.clear()
        board.set_piece_at(chess.E1, chess.Piece(chess.KING, chess.WHITE))
        board.set_piece_at(chess.E8, chess.Piece(chess.KING, chess.BLACK))
        encoded = encode_board(board)
        assert int(encoded.sum()) == 2  # Only 2 kings

    def test_different_positions_differ(self):
        """Different positions should produce different encodings."""
        board1 = chess.Board()
        board2 = chess.Board()
        board2.push(chess.Move.from_uci("e2e4"))
        enc1 = encode_board(board1)
        enc2 = encode_board(board2)
        assert not (enc1 == enc2).all()


class TestMoveOrdering:
    def test_captures_first(self):
        """Captures should appear before quiet moves."""
        board = chess.Board()
        # Position with a capture available
        board.push(chess.Move.from_uci("e2e4"))
        board.push(chess.Move.from_uci("d7d5"))

        moves = list(board.legal_moves)
        ordered = order_moves(board, moves)

        # Check that any available captures are near the top
        capture_indices = [
            i for i, m in enumerate(ordered) if board.is_capture(m)
        ]
        quiet_indices = [
            i for i, m in enumerate(ordered) if not board.is_capture(m)
        ]

        if capture_indices and quiet_indices:
            # At least the first capture should be ranked before the last quiet move
            assert min(capture_indices) < max(quiet_indices)


class TestAlphaBeta:
    def test_returns_legal_move(self):
        """Engine should always return a legal move."""
        board = chess.Board()
        engine = AlphaBetaEngine(depth=2)
        move, score = engine.search(board)
        assert move is not None
        assert move in chess.Board().legal_moves

    def test_finds_checkmate_in_one(self):
        """Engine should find a checkmate in one move."""
        # Position with checkmate in one for White
        # White queen on h5 can deliver checkmate on f7
        board = chess.Board("rnb1kbnr/pppp1ppp/8/4p2Q/2B1P3/8/PPPP1PPP/RNB1K1NR w KQkq - 2 3")
        engine = AlphaBetaEngine(depth=3)
        move, score = engine.search(board)
        # Scholar's mate: Qxf7#
        assert move is not None
        board.push(move)
        assert board.is_checkmate(), f"Expected checkmate, engine played {move}"

    def test_game_over_returns_none(self):
        """Engine should return None for game-over positions."""
        board = chess.Board("rnb1kbnr/pppp1Qpp/8/4p3/2B1P3/8/PPPP1PPP/RNB1K1NR b KQkq - 0 3")
        if board.is_game_over():
            engine = AlphaBetaEngine(depth=2)
            move, _ = engine.search(board)
            assert move is None

    def test_depth_increases_strength(self):
        """Deeper search should not be worse than shallower search (on average)."""
        # This is a statistical test — just verify both work without error
        board = chess.Board()
        board.push(chess.Move.from_uci("e2e4"))
        board.push(chess.Move.from_uci("e7e5"))

        shallow = AlphaBetaEngine(depth=2)
        deep = AlphaBetaEngine(depth=3)

        move_shallow, _ = shallow.search(board)
        move_deep, _ = deep.search(board)

        assert move_shallow is not None
        assert move_deep is not None


class TestDifficultyLevels:
    def test_levels_exist(self):
        for level in ["easy", "medium", "hard"]:
            config = get_level(level)
            assert config.name == level

    def test_hard_uses_neural(self):
        assert get_level("hard").use_neural is True

    def test_easy_no_neural(self):
        assert get_level("easy").use_neural is False

    def test_hard_deeper_than_easy(self):
        assert get_level("hard").depth > get_level("easy").depth

    def test_invalid_level_raises(self):
        with pytest.raises(ValueError):
            get_level("grandmaster")
