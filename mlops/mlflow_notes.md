# MLflow Notes

## Overview

This project uses MLflow for experiment tracking during ValueNet training.

## Starting the MLflow UI

```bash
# From the project root
mlflow ui --backend-store-uri ./backend/mlruns

# Or with Docker Compose
docker-compose up mlflow
# → http://localhost:5000
```

## What is Tracked

Every training run logs:

**Parameters:**
- `epochs`, `batch_size`, `learning_rate`, `weight_decay`
- `hidden_dims`, `dropout_rate`
- `train_samples`, `val_samples`
- `model_parameters` (total trainable parameters)

**Metrics (per epoch):**
- `train_loss` — MSE loss on training set
- `val_loss` — MSE loss on validation set

**Artifacts:**
- `value_net_model/` — logged PyTorch model
- `checkpoints/value_net_best.pt` — best checkpoint by val_loss

## Experiment Organization

Experiment name: `chess-value-net` (configurable via `MLFLOW_EXPERIMENT_NAME`)

Each run corresponds to one training session. Use the MLflow UI to:
1. Compare hyperparameter effects on validation loss
2. Download the best model checkpoint
3. Reproduce any previous training run

## Running Multiple Experiments

```bash
# Experiment 1: Baseline
python -m app.ml.training.train --epochs 20 --lr 3e-4

# Experiment 2: Higher dropout
python -m app.ml.training.train --epochs 20 --lr 3e-4 --dropout 0.5

# Experiment 3: More epochs
python -m app.ml.training.train --epochs 50 --lr 1e-4

# Compare in MLflow UI
mlflow ui
```

## Integrating DVC + MLflow

Run the full pipeline with DVC (which calls MLflow internally):
```bash
cd backend
dvc repro  # from project root with dvc.yaml
```

DVC tracks data/model versioning while MLflow tracks training metrics.
This combination is the industry standard for ML reproducibility.

## Production Notes

For production, point `MLFLOW_TRACKING_URI` to a hosted MLflow server:
- MLflow on a VM with PostgreSQL backend
- Databricks Managed MLflow
- AWS SageMaker Experiments
