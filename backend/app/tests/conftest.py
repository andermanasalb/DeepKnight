"""
Shared test fixtures.

Sets up app.state.predictor before tests run so that the lifespan event
(which loads the real model file) is not required in CI.
"""

import pytest

from app.main import app
from app.ml.inference.predictor import ModelPredictor


@pytest.fixture(autouse=True)
def inject_predictor():
    """Inject an unloaded ModelPredictor into app state for all tests.

    ModelPredictor.predict() returns 0.0 when no model is loaded,
    so tests get valid (neutral) scores without needing the .pt file.
    """
    predictor = ModelPredictor()
    app.state.predictor = predictor
    yield
    # Clean up
    if hasattr(app.state, "predictor"):
        del app.state.predictor
