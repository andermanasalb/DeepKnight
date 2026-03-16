"""
Difficulty level definitions for the chess engine.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class DifficultyLevel:
    name: str
    depth: int
    use_neural: bool
    neural_weight: float  # weight for PyTorch score vs classical (0.0 = classical only)
    use_move_ordering: bool
    random_factor: float  # small randomness to make Easy less predictable


DIFFICULTY_LEVELS: dict[str, DifficultyLevel] = {
    "easy": DifficultyLevel(
        name="easy",
        depth=2,
        use_neural=False,
        neural_weight=0.0,
        use_move_ordering=False,
        random_factor=0.15,  # 15% chance to pick a suboptimal move
    ),
    "medium": DifficultyLevel(
        name="medium",
        depth=3,
        use_neural=False,
        neural_weight=0.0,
        use_move_ordering=True,
        random_factor=0.0,
    ),
    "hard": DifficultyLevel(
        name="hard",
        depth=4,
        use_neural=True,
        neural_weight=0.3,  # 30% neural, 70% classical
        use_move_ordering=True,
        random_factor=0.0,
    ),
}


def get_level(difficulty: str) -> DifficultyLevel:
    level = DIFFICULTY_LEVELS.get(difficulty.lower())
    if level is None:
        raise ValueError(f"Unknown difficulty: {difficulty}. Must be one of {list(DIFFICULTY_LEVELS)}")
    return level
