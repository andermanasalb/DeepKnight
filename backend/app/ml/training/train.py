"""
ValueNet Training Script.

Features:
  - Train/val loop with early stopping
  - MLflow experiment tracking (hyperparameters, metrics, artifacts)
  - Checkpoint saving (best model and latest)
  - Configurable hyperparameters via params.yaml or CLI

Usage:
  python -m app.ml.training.train
  python -m app.ml.training.train --epochs 50 --lr 0.001
"""

import argparse
import os
from pathlib import Path

import mlflow
import mlflow.pytorch
import numpy as np
import torch
import torch.nn as nn
from torch.utils.data import DataLoader

from app.core.config import settings
from app.ml.models.value_net import build_value_net
from app.ml.training.dataset import ChessPositionDataset

DATA_DIR = Path("data/processed")
MODEL_DIR = Path("data/models")
MODEL_DIR.mkdir(parents=True, exist_ok=True)


def train_epoch(
    model: nn.Module,
    loader: DataLoader,
    optimizer: torch.optim.Optimizer,
    criterion: nn.Module,
    device: str,
) -> float:
    model.train()
    total_loss = 0.0

    for X_batch, y_batch in loader:
        X_batch = X_batch.to(device)
        y_batch = y_batch.to(device).unsqueeze(1)  # (batch, 1)

        optimizer.zero_grad()
        predictions = model(X_batch)
        loss = criterion(predictions, y_batch)
        loss.backward()

        # Gradient clipping for training stability
        torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)

        optimizer.step()
        total_loss += loss.item() * len(X_batch)

    return total_loss / len(loader.dataset)


@torch.no_grad()
def validate_epoch(
    model: nn.Module,
    loader: DataLoader,
    criterion: nn.Module,
    device: str,
) -> float:
    model.eval()
    total_loss = 0.0

    for X_batch, y_batch in loader:
        X_batch = X_batch.to(device)
        y_batch = y_batch.to(device).unsqueeze(1)

        predictions = model(X_batch)
        loss = criterion(predictions, y_batch)
        total_loss += loss.item() * len(X_batch)

    return total_loss / len(loader.dataset)


def train(
    epochs: int = 30,
    batch_size: int = 512,
    learning_rate: float = 3e-4,
    weight_decay: float = 1e-4,
    hidden_dims: list[int] | None = None,
    dropout_rate: float = 0.3,
    patience: int = 7,
    device: str | None = None,
) -> dict:
    """
    Main training function.

    Returns:
        dict with final training metrics
    """
    if device is None:
        device = settings.DEVICE

    if hidden_dims is None:
        hidden_dims = [256, 128, 64]

    print("DeepKnight — Training ValueNet")
    print(f"  Device: {device}")
    print(f"  Epochs: {epochs}")
    print(f"  Batch size: {batch_size}")
    print(f"  Learning rate: {learning_rate}")
    print()

    # ─── Dataset ─────────────────────────────────────────
    train_dataset = ChessPositionDataset(DATA_DIR, split="train")
    val_dataset = ChessPositionDataset(DATA_DIR, split="val")

    train_loader = DataLoader(
        train_dataset,
        batch_size=batch_size,
        shuffle=True,
        num_workers=0,
    )
    val_loader = DataLoader(
        val_dataset,
        batch_size=batch_size * 2,
        shuffle=False,
        num_workers=0,
    )

    print(f"  Train samples: {len(train_dataset):,}")
    print(f"  Val samples:   {len(val_dataset):,}")

    # ─── Model ───────────────────────────────────────────
    model = build_value_net(hidden_dims=hidden_dims, dropout_rate=dropout_rate).to(device)
    info = model.get_model_info()
    print(f"  Model parameters: {info['trainable_parameters']:,}")

    # ─── Optimizer & scheduler ───────────────────────────
    optimizer = torch.optim.AdamW(
        model.parameters(),
        lr=learning_rate,
        weight_decay=weight_decay,
    )
    scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(
        optimizer, mode="min", factor=0.5, patience=3
    )
    criterion = nn.MSELoss()

    # ─── MLflow tracking ─────────────────────────────────
    mlflow.set_tracking_uri(settings.MLFLOW_TRACKING_URI)
    mlflow.set_experiment(settings.MLFLOW_EXPERIMENT_NAME)

    with mlflow.start_run() as run:
        # Log hyperparameters
        mlflow.log_params({
            "epochs": epochs,
            "batch_size": batch_size,
            "learning_rate": learning_rate,
            "weight_decay": weight_decay,
            "hidden_dims": str(hidden_dims),
            "dropout_rate": dropout_rate,
            "device": device,
            "train_samples": len(train_dataset),
            "val_samples": len(val_dataset),
            "model_parameters": info["trainable_parameters"],
        })

        # ─── Training loop ────────────────────────────────
        best_val_loss = float("inf")
        patience_counter = 0
        best_model_path = MODEL_DIR / "value_net_best.pt"
        latest_model_path = MODEL_DIR / "value_net.pt"

        for epoch in range(1, epochs + 1):
            train_loss = train_epoch(model, train_loader, optimizer, criterion, device)
            val_loss = validate_epoch(model, val_loader, criterion, device)

            scheduler.step(val_loss)

            # Log metrics
            mlflow.log_metrics(
                {"train_loss": train_loss, "val_loss": val_loss},
                step=epoch,
            )

            # Print progress
            if epoch % 5 == 0 or epoch == 1:
                print(f"  Epoch {epoch:3d}/{epochs} | "
                      f"train_loss={train_loss:.5f} | val_loss={val_loss:.5f}")

            # Checkpoint best model
            if val_loss < best_val_loss:
                best_val_loss = val_loss
                patience_counter = 0
                _save_checkpoint(model, optimizer, epoch, val_loss, best_model_path)
            else:
                patience_counter += 1

            # Save latest checkpoint
            _save_checkpoint(model, optimizer, epoch, val_loss, latest_model_path)

            # Early stopping
            if patience_counter >= patience:
                print(f"\n  Early stopping triggered after {epoch} epochs")
                break

        # Log final model artifact
        mlflow.pytorch.log_model(model, "value_net_model")
        mlflow.log_artifact(str(best_model_path), "checkpoints")

        run_id = run.info.run_id
        print(f"\n  Training complete!")
        print(f"  Best val loss: {best_val_loss:.5f}")
        print(f"  MLflow run ID: {run_id}")
        print(f"  Model saved to: {best_model_path}")

        return {
            "best_val_loss": best_val_loss,
            "run_id": run_id,
            "model_path": str(best_model_path),
        }


def _save_checkpoint(
    model: nn.Module,
    optimizer: torch.optim.Optimizer,
    epoch: int,
    val_loss: float,
    path: Path,
) -> None:
    torch.save(
        {
            "epoch": epoch,
            "model_state_dict": model.state_dict(),
            "optimizer_state_dict": optimizer.state_dict(),
            "val_loss": val_loss,
            "model_config": model.get_model_info(),
        },
        path,
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Train Chess ValueNet")
    parser.add_argument("--epochs", type=int, default=30)
    parser.add_argument("--batch-size", type=int, default=512)
    parser.add_argument("--lr", type=float, default=3e-4)
    parser.add_argument("--weight-decay", type=float, default=1e-4)
    parser.add_argument("--dropout", type=float, default=0.3)
    parser.add_argument("--patience", type=int, default=7)
    parser.add_argument("--device", type=str, default=None)
    args = parser.parse_args()

    train(
        epochs=args.epochs,
        batch_size=args.batch_size,
        learning_rate=args.lr,
        weight_decay=args.weight_decay,
        dropout_rate=args.dropout,
        patience=args.patience,
        device=args.device,
    )
