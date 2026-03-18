"""
Dummy data generator for ValueNet training.

Generates synthetic (FEN, evaluation) pairs by:
  1. Playing random games using python-chess
  2. Evaluating each position with the classical evaluator
  3. Normalizing scores and saving to disk

This provides a realistic training signal for the neural network,
though for best results you'd use Stockfish-annotated data.

Usage:
  python -m app.ml.training.dummy_data
"""

import random
from pathlib import Path

import chess
import numpy as np

from app.engine.encoding import encode_board
from app.engine.evaluation import ClassicalEvaluator

evaluator = ClassicalEvaluator()

DATA_DIR = Path("data/processed")
TOTAL_POSITIONS = 150_000
TRAIN_RATIO = 0.85
RANDOM_SEED = 42


def generate_random_game_positions(max_moves: int = 80) -> list[tuple[str, float]]:
    """
    Play a random game and record all positions with their evaluations.

    Returns:
        List of (FEN, normalized_score) pairs
    """
    board = chess.Board()
    positions = []

    for _ in range(max_moves):
        if board.is_game_over():
            break

        legal = list(board.legal_moves)
        if not legal:
            break

        # Play a random move
        move = random.choice(legal)
        board.push(move)

        # Evaluate and normalize to [-1, 1]
        raw_score = evaluator.evaluate(board)
        normalized = float(np.clip(raw_score / 1000.0, -1.0, 1.0))

        positions.append((board.fen(), normalized))

    return positions


def generate_dataset(
    n_positions: int = TOTAL_POSITIONS,
    seed: int = RANDOM_SEED,
) -> tuple[np.ndarray, np.ndarray]:
    """
    Generate a dataset of encoded board positions with evaluation labels.

    Returns:
        X: ndarray of shape (n_positions, 768)
        y: ndarray of shape (n_positions,)
    """
    random.seed(seed)
    np.random.seed(seed)

    X_list = []
    y_list = []
    collected = 0

    print(f"Generating {n_positions:,} chess positions...")

    while collected < n_positions:
        positions = generate_random_game_positions()
        for fen, score in positions:
            if collected >= n_positions:
                break
            try:
                board = chess.Board(fen)
                encoded = encode_board(board)
                X_list.append(encoded)
                y_list.append(score)
                collected += 1
            except ValueError:
                continue

        if collected % 5000 == 0:
            print(f"  Collected {collected:,}/{n_positions:,} positions...")

    X = np.array(X_list, dtype=np.float32)
    y = np.array(y_list, dtype=np.float32)

    return X, y


def save_dataset(X: np.ndarray, y: np.ndarray, data_dir: Path = DATA_DIR) -> None:
    """Split and save dataset to train/val directories."""
    n = len(X)
    split_idx = int(n * TRAIN_RATIO)

    # Shuffle before splitting
    perm = np.random.permutation(n)
    X, y = X[perm], y[perm]

    X_train, X_val = X[:split_idx], X[split_idx:]
    y_train, y_val = y[:split_idx], y[split_idx:]

    for split_name, X_split, y_split in [
        ("train", X_train, y_train),
        ("val", X_val, y_val),
    ]:
        split_dir = data_dir / split_name
        split_dir.mkdir(parents=True, exist_ok=True)

        np.save(split_dir / "X.npy", X_split)
        np.save(split_dir / "y.npy", y_split)
        print(f"Saved {len(X_split):,} {split_name} samples to {split_dir}")


if __name__ == "__main__":
    print("DeepKnight — Generating training data")
    print(f"Target: {TOTAL_POSITIONS:,} positions")
    print()

    X, y = generate_dataset(n_positions=TOTAL_POSITIONS)

    print("\nDataset statistics:")
    print(f"  Total samples: {len(X):,}")
    print(f"  X shape: {X.shape}")
    print(f"  y range: [{y.min():.3f}, {y.max():.3f}]")
    print(f"  y mean: {y.mean():.3f} (0 = balanced)")
    print()

    save_dataset(X, y)
    print("\nDone! Run `python -m app.ml.training.train` to train the model.")
