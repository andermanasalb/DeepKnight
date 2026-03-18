"""
Dataset for ValueNet training.

Data format: list of (FEN string, evaluation score) pairs.
Score is normalized to [-1, 1]:
  - Classical centipawn score / 1000 (clipped to [-1, 1])
  - Or from labeled game outcome (1 = White win, -1 = Black win, 0 = draw)

For production:
  - Parse Stockfish-annotated PGN files
  - Use python-chess to replay games and encode each position
  - Label with Stockfish evaluation or game outcome

For this scaffold:
  - dummy_data.py generates synthetic training data
  - dataset.py handles loading and preprocessing
"""

from pathlib import Path

import chess
import numpy as np
import torch
from torch.utils.data import Dataset

from app.engine.encoding import encode_board


class ChessPositionDataset(Dataset):
    """
    PyTorch Dataset for board position → evaluation pairs.

    Expects a numpy file with:
      - X.npy: array of shape (N, 768) — encoded board positions
      - y.npy: array of shape (N,) — evaluation labels in [-1, 1]
    """

    def __init__(self, data_dir: str | Path, split: str = "train"):
        """
        Args:
            data_dir: Directory containing X.npy and y.npy
            split: 'train' or 'val' — loads from {data_dir}/{split}/
        """
        self.data_dir = Path(data_dir) / split

        x_path = self.data_dir / "X.npy"
        y_path = self.data_dir / "y.npy"

        if not x_path.exists() or not y_path.exists():
            raise FileNotFoundError(
                f"Dataset not found at {self.data_dir}. "
                "Run `python -m app.ml.training.dummy_data` to generate training data."
            )

        self.X = np.load(x_path, mmap_mode="r").astype(np.float32)
        self.y = np.load(y_path, mmap_mode="r").astype(np.float32)

        assert len(self.X) == len(self.y), "X and y must have the same number of samples"

    def __len__(self) -> int:
        return len(self.X)

    def __getitem__(self, idx: int) -> tuple[torch.Tensor, torch.Tensor]:
        x = torch.from_numpy(self.X[idx].copy())
        y = torch.tensor(self.y[idx], dtype=torch.float32)
        return x, y


class FenDataset(Dataset):
    """
    Dataset constructed directly from a list of (FEN, score) pairs.
    Useful for quick experiments without saving to disk.
    """

    def __init__(self, fen_score_pairs: list[tuple[str, float]]):
        self.data = []
        for fen, score in fen_score_pairs:
            try:
                board = chess.Board(fen)
                encoded = encode_board(board)
                # Clip and normalize score
                label = float(np.clip(score, -1.0, 1.0))
                self.data.append((encoded, label))
            except ValueError:
                continue  # Skip invalid FENs

    def __len__(self) -> int:
        return len(self.data)

    def __getitem__(self, idx: int) -> tuple[torch.Tensor, torch.Tensor]:
        x_arr, y_val = self.data[idx]
        x = torch.from_numpy(x_arr.copy())
        y = torch.tensor(y_val, dtype=torch.float32)
        return x, y
