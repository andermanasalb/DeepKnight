"""
ModelPredictor — production inference wrapper for the ValueNet.

Handles:
  - Model loading from checkpoint
  - Thread-safe inference
  - Graceful degradation when model is not available
  - Caching of recent predictions (optional)
"""

import threading
from pathlib import Path

import chess
import torch

from app.core.logging import get_logger
from app.engine.encoding import encode_board_tensor
from app.ml.models.value_net import ValueNet, build_value_net

logger = get_logger(__name__)


class ModelPredictor:
    """
    Thread-safe inference wrapper for the ValueNet model.

    Usage:
        predictor = ModelPredictor()
        predictor.load_model("data/models/value_net.pt")

        score = predictor.predict(board)  # float in [-1, 1]
    """

    def __init__(self, device: str | None = None):
        from app.core.config import settings
        self.device = device or settings.DEVICE
        self.model: ValueNet | None = None
        self._lock = threading.Lock()
        self._is_loaded = False

    @property
    def is_loaded(self) -> bool:
        return self._is_loaded

    def load_model(self, checkpoint_path: str | Path) -> bool:
        """
        Load model weights from a checkpoint file.

        Args:
            checkpoint_path: Path to .pt checkpoint file

        Returns:
            True if loaded successfully, False if not found (graceful degradation)
        """
        checkpoint_path = Path(checkpoint_path)

        if not checkpoint_path.exists():
            logger.warning(
                "Model checkpoint not found — neural evaluation disabled",
                path=str(checkpoint_path),
            )
            return False

        try:
            with self._lock:
                checkpoint = torch.load(
                    checkpoint_path,
                    map_location=self.device,
                    weights_only=True,
                )

                config = checkpoint.get("model_config", {})
                self.model = build_value_net(
                    hidden_dims=config.get("hidden_dims", [256, 128, 64]),
                )
                self.model.load_state_dict(checkpoint["model_state_dict"])
                self.model.to(self.device)
                self.model.eval()
                self._is_loaded = True

            epoch = checkpoint.get("epoch", "?")
            val_loss = checkpoint.get("val_loss", float("nan"))
            logger.info(
                "ValueNet loaded",
                path=str(checkpoint_path),
                epoch=epoch,
                val_loss=f"{val_loss:.5f}",
                device=self.device,
            )
            return True

        except Exception as e:
            logger.error("Failed to load model checkpoint", error=str(e))
            self._is_loaded = False
            return False

    def predict(self, board: chess.Board) -> float:
        """
        Predict position evaluation for a single board.

        Args:
            board: python-chess Board instance

        Returns:
            float in [-1, 1]: positive = White advantage, negative = Black advantage
            Returns 0.0 if model is not loaded.
        """
        if not self._is_loaded or self.model is None:
            return 0.0

        try:
            tensor = encode_board_tensor(board, device=self.device)
            with self._lock:
                with torch.no_grad():
                    output = self.model(tensor)
                    return float(output.item())
        except Exception as e:
            logger.error("Prediction failed", error=str(e))
            return 0.0

    def predict_batch(self, boards: list[chess.Board]) -> list[float]:
        """
        Predict evaluations for multiple boards (more efficient than individual calls).

        Args:
            boards: List of chess.Board instances

        Returns:
            List of floats in [-1, 1]
        """
        if not self._is_loaded or self.model is None:
            return [0.0] * len(boards)

        try:
            from app.engine.encoding import encode_batch

            batch_arr = encode_batch(boards)
            tensor = torch.from_numpy(batch_arr).to(self.device)

            with self._lock:
                with torch.no_grad():
                    outputs = self.model(tensor)
                    return outputs.squeeze().tolist()
        except Exception as e:
            logger.error("Batch prediction failed", error=str(e))
            return [0.0] * len(boards)

    def get_info(self) -> dict:
        """Return model status and info."""
        return {
            "is_loaded": self._is_loaded,
            "device": self.device,
            "model_info": self.model.get_model_info() if self.model else None,
        }
