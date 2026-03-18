"""
Post-game summarizer utility.

Preprocesses game data before sending to the LLM:
  - Converts UCI move list to annotated SAN
  - Identifies blunders using classical evaluation
  - Structures context for the coach prompt
"""

import chess

from app.engine.evaluation import ClassicalEvaluator

evaluator = ClassicalEvaluator()

BLUNDER_THRESHOLD = 150   # centipawns — score swing indicating a blunder
MISTAKE_THRESHOLD = 75    # centipawns — score swing indicating a mistake
INACCURACY_THRESHOLD = 30  # centipawns — score swing indicating an inaccuracy


def analyze_game_moves(moves_uci: list[str]) -> list[dict]:
    """
    Analyze each move in the game for evaluation swings.

    Returns:
        List of move analysis dicts with fields:
          - move_number, uci, san, score_before, score_after,
            delta, severity, player
    """
    board = chess.Board()
    analysis = []
    move_number = 1

    for i, uci in enumerate(moves_uci):
        try:
            move = chess.Move.from_uci(uci)
            if move not in board.legal_moves:
                break

            player = "white" if board.turn == chess.WHITE else "black"
            score_before = evaluator.evaluate(board)
            san = board.san(move)
            board.push(move)
            score_after = evaluator.evaluate(board)

            # From the perspective of the player who just moved
            delta = (score_before - score_after) if player == "white" else (score_after - score_before)
            delta = abs(delta)

            severity = _classify_severity(delta, player, score_before, score_after)

            analysis.append({
                "move_number": move_number,
                "ply": i + 1,
                "uci": uci,
                "san": san,
                "player": player,
                "score_before": round(score_before / 100.0, 2),
                "score_after": round(score_after / 100.0, 2),
                "delta": round(delta / 100.0, 2),
                "severity": severity,
            })

            if player == "black":
                move_number += 1

        except (ValueError, AssertionError):
            break

    return analysis


def _classify_severity(
    delta: float,
    player: str,
    score_before: float,
    score_after: float,
) -> str:
    """Classify the severity of a move based on evaluation swing."""
    if delta >= BLUNDER_THRESHOLD:
        return "blunder"
    elif delta >= MISTAKE_THRESHOLD:
        return "mistake"
    elif delta >= INACCURACY_THRESHOLD:
        return "inaccuracy"
    return "good"


def get_player_mistakes(analysis: list[dict], player: str) -> list[dict]:
    """Filter move analysis to only include player mistakes/blunders."""
    return [
        move for move in analysis
        if move["player"] == player
        and move["severity"] in ("blunder", "mistake", "inaccuracy")
    ]
