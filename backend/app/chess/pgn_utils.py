"""
PGN (Portable Game Notation) utilities.
"""

import io

import chess
import chess.pgn


def pgn_from_moves(
    moves_uci: list[str],
    white_name: str = "Human",
    black_name: str = "DeepKnight",
    event: str = "DeepKnight",
) -> str:
    """
    Build a PGN string from a list of UCI moves.

    Args:
        moves_uci: List of moves in UCI format
        white_name: Name for White player
        black_name: Name for Black player
        event: Event name for PGN header

    Returns:
        PGN string
    """
    board = chess.Board()
    game = chess.pgn.Game()
    game.headers["Event"] = event
    game.headers["White"] = white_name
    game.headers["Black"] = black_name

    node = game
    for uci in moves_uci:
        try:
            move = chess.Move.from_uci(uci)
            if move in board.legal_moves:
                node = node.add_variation(move)
                board.push(move)
        except ValueError:
            break

    # Set result
    if board.is_checkmate():
        game.headers["Result"] = "0-1" if board.turn == chess.WHITE else "1-0"
    elif board.is_game_over():
        game.headers["Result"] = "1/2-1/2"
    else:
        game.headers["Result"] = "*"

    output = io.StringIO()
    exporter = chess.pgn.FileExporter(output)
    game.accept(exporter)
    return output.getvalue()


def parse_pgn(pgn_text: str) -> list[str]:
    """
    Parse a PGN string and return the list of moves in UCI format.
    """
    game = chess.pgn.read_game(io.StringIO(pgn_text))
    if game is None:
        return []

    moves = []
    board = game.board()
    for move in game.mainline_moves():
        moves.append(move.uci())
        board.push(move)

    return moves


def pgn_to_san_list(pgn_text: str) -> list[str]:
    """
    Parse PGN and return moves in SAN notation.
    """
    game = chess.pgn.read_game(io.StringIO(pgn_text))
    if game is None:
        return []

    moves = []
    board = game.board()
    for move in game.mainline_moves():
        moves.append(board.san(move))
        board.push(move)

    return moves
