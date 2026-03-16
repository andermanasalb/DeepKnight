"""
Board encoding for PyTorch model input.

Converts a python-chess Board into a fixed-size tensor representation.
Uses 12 binary planes (6 piece types × 2 colors) over an 8×8 grid,
yielding a 768-dimensional input vector.

Plane ordering:
  0: White Pawn    1: White Knight  2: White Bishop
  3: White Rook    4: White Queen   5: White King
  6: Black Pawn    7: Black Knight  8: Black Bishop
  9: Black Rook   10: Black Queen  11: Black King
"""

import chess
import numpy as np
import torch

# Piece type → plane offset (0 for White, 6 for Black)
PIECE_PLANE_MAP = {
    (chess.PAWN, chess.WHITE): 0,
    (chess.KNIGHT, chess.WHITE): 1,
    (chess.BISHOP, chess.WHITE): 2,
    (chess.ROOK, chess.WHITE): 3,
    (chess.QUEEN, chess.WHITE): 4,
    (chess.KING, chess.WHITE): 5,
    (chess.PAWN, chess.BLACK): 6,
    (chess.KNIGHT, chess.BLACK): 7,
    (chess.BISHOP, chess.BLACK): 8,
    (chess.ROOK, chess.BLACK): 9,
    (chess.QUEEN, chess.BLACK): 10,
    (chess.KING, chess.BLACK): 11,
}

INPUT_DIM = 768  # 12 planes × 64 squares


def encode_board(board: chess.Board) -> np.ndarray:
    """
    Encode a chess board as a 768-dim float32 numpy array.

    Args:
        board: python-chess Board instance

    Returns:
        np.ndarray of shape (768,) with values in {0, 1}
    """
    planes = np.zeros((12, 8, 8), dtype=np.float32)

    for square in chess.SQUARES:
        piece = board.piece_at(square)
        if piece is not None:
            plane_idx = PIECE_PLANE_MAP[(piece.piece_type, piece.color)]
            rank = square >> 3   # square // 8
            file = square & 7   # square % 8
            planes[plane_idx, rank, file] = 1.0

    return planes.flatten()  # (768,)


def encode_board_tensor(board: chess.Board, device: str = "cpu") -> torch.Tensor:
    """
    Encode a board and return a PyTorch tensor ready for model inference.

    Args:
        board: python-chess Board instance
        device: torch device string ("cpu" or "cuda")

    Returns:
        Tensor of shape (1, 768) on the specified device
    """
    arr = encode_board(board)
    tensor = torch.from_numpy(arr).unsqueeze(0)  # (1, 768)
    return tensor.to(device)


def encode_batch(boards: list[chess.Board]) -> np.ndarray:
    """
    Encode multiple boards as a batch.

    Args:
        boards: List of python-chess Board instances

    Returns:
        np.ndarray of shape (N, 768)
    """
    return np.stack([encode_board(b) for b in boards], axis=0)
