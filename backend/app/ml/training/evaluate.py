"""
Model evaluation script.

Loads a trained ValueNet checkpoint and evaluates it on the
validation set. Reports MSE, MAE, and correlation metrics.

Usage:
  python -m app.ml.training.evaluate
  python -m app.ml.training.evaluate --checkpoint data/models/value_net_best.pt
"""

import argparse
from pathlib import Path

import numpy as np
import torch
import torch.nn as nn
from torch.utils.data import DataLoader

from app.ml.models.value_net import ValueNet, build_value_net
from app.ml.training.dataset import ChessPositionDataset

DATA_DIR = Path("data/processed")


def evaluate_model(checkpoint_path: str | Path) -> dict:
    """
    Load a checkpoint and evaluate on the validation set.

    Returns:
        dict with evaluation metrics
    """
    checkpoint_path = Path(checkpoint_path)
    if not checkpoint_path.exists():
        raise FileNotFoundError(f"Checkpoint not found: {checkpoint_path}")

    # Load checkpoint
    checkpoint = torch.load(checkpoint_path, map_location="cpu")
    config = checkpoint.get("model_config", {})

    model = build_value_net(
        hidden_dims=config.get("hidden_dims", [256, 128, 64]),
    )
    model.load_state_dict(checkpoint["model_state_dict"])
    model.eval()

    print(f"Loaded model from epoch {checkpoint.get('epoch', '?')}")
    print(f"Checkpoint val_loss: {checkpoint.get('val_loss', 'N/A'):.5f}")
    print()

    # Load validation data
    val_dataset = ChessPositionDataset(DATA_DIR, split="val")
    val_loader = DataLoader(val_dataset, batch_size=1024, shuffle=False)

    all_preds = []
    all_targets = []

    with torch.no_grad():
        for X_batch, y_batch in val_loader:
            preds = model(X_batch).squeeze()
            all_preds.append(preds.numpy())
            all_targets.append(y_batch.numpy())

    predictions = np.concatenate(all_preds)
    targets = np.concatenate(all_targets)

    # Compute metrics
    mse = float(np.mean((predictions - targets) ** 2))
    mae = float(np.mean(np.abs(predictions - targets)))
    rmse = float(np.sqrt(mse))

    # Pearson correlation
    correlation = float(np.corrcoef(predictions, targets)[0, 1])

    # Sign accuracy (does the model agree on who is winning?)
    sign_correct = np.sum(np.sign(predictions) == np.sign(targets))
    sign_accuracy = float(sign_correct) / len(predictions)

    metrics = {
        "mse": mse,
        "rmse": rmse,
        "mae": mae,
        "pearson_correlation": correlation,
        "sign_accuracy": sign_accuracy,
        "n_samples": len(predictions),
    }

    print("Evaluation Results:")
    print(f"  Samples:          {metrics['n_samples']:,}")
    print(f"  MSE:              {metrics['mse']:.5f}")
    print(f"  RMSE:             {metrics['rmse']:.5f}")
    print(f"  MAE:              {metrics['mae']:.5f}")
    print(f"  Pearson r:        {metrics['pearson_correlation']:.4f}")
    print(f"  Sign accuracy:    {metrics['sign_accuracy']:.2%}")

    return metrics


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Evaluate ValueNet checkpoint")
    parser.add_argument(
        "--checkpoint",
        type=str,
        default="data/models/value_net_best.pt",
        help="Path to model checkpoint",
    )
    args = parser.parse_args()

    evaluate_model(args.checkpoint)
