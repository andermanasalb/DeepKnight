"""
ValueNet — PyTorch model for chess position evaluation.

Architecture:
  Input: 768-dimensional board encoding (12 piece planes × 64 squares)
  Hidden: MLP with batch normalization and dropout
  Output: scalar in [-1, 1] (positive = White advantage)

Design notes:
  - Simple MLP is a solid baseline for position evaluation
  - Can be upgraded to CNN or Transformer for better performance
  - Tanh output naturally bounds the score to [-1, 1]
  - Batch normalization stabilizes training on sparse binary inputs
"""

import torch
import torch.nn as nn
import torch.nn.functional as F

INPUT_DIM = 768  # 12 planes × 64 squares


class ValueNet(nn.Module):
    """
    Multi-layer perceptron for board position evaluation.

    Input: encoded board tensor of shape (batch, 768)
    Output: scalar evaluation of shape (batch, 1) in [-1, 1]
    """

    def __init__(
        self,
        input_dim: int = INPUT_DIM,
        hidden_dims: list[int] | None = None,
        dropout_rate: float = 0.3,
    ):
        super().__init__()

        if hidden_dims is None:
            hidden_dims = [256, 128, 64]

        self.input_dim = input_dim
        self.hidden_dims = hidden_dims
        self.dropout_rate = dropout_rate

        # Build network layers dynamically
        layers = []
        prev_dim = input_dim

        for i, hidden_dim in enumerate(hidden_dims):
            layers.append(nn.Linear(prev_dim, hidden_dim))
            layers.append(nn.BatchNorm1d(hidden_dim))
            layers.append(nn.ReLU())
            if i < len(hidden_dims) - 1:
                layers.append(nn.Dropout(dropout_rate))
            prev_dim = hidden_dim

        # Output layer
        layers.append(nn.Linear(prev_dim, 1))
        layers.append(nn.Tanh())

        self.network = nn.Sequential(*layers)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """
        Forward pass.

        Args:
            x: Tensor of shape (batch_size, 768)

        Returns:
            Tensor of shape (batch_size, 1) with values in [-1, 1]
        """
        return self.network(x)

    def predict_scalar(self, x: torch.Tensor) -> float:
        """
        Single-position inference returning a Python float.

        Args:
            x: Tensor of shape (1, 768)

        Returns:
            float in [-1, 1]
        """
        self.eval()
        with torch.no_grad():
            output = self.forward(x)
            return output.item()

    def get_model_info(self) -> dict:
        """Return model architecture information."""
        total_params = sum(p.numel() for p in self.parameters())
        trainable_params = sum(p.numel() for p in self.parameters() if p.requires_grad)
        return {
            "input_dim": self.input_dim,
            "hidden_dims": self.hidden_dims,
            "total_parameters": total_params,
            "trainable_parameters": trainable_params,
            "architecture": "MLP",
        }


def build_value_net(
    input_dim: int = INPUT_DIM,
    hidden_dims: list[int] | None = None,
    dropout_rate: float = 0.3,
) -> ValueNet:
    """Factory function for ValueNet with default hyperparameters."""
    return ValueNet(
        input_dim=input_dim,
        hidden_dims=hidden_dims or [256, 128, 64],
        dropout_rate=dropout_rate,
    )
