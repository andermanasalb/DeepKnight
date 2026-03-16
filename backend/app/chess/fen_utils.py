"""
FEN string utilities built on top of python-chess.
"""

import chess


def parse_fen(fen: str) -> chess.Board:
    """Parse a FEN string into a chess.Board. Raises ValueError on invalid FEN."""
    try:
        board = chess.Board(fen)
        return board
    except ValueError as e:
        raise ValueError(f"Invalid FEN '{fen}': {e}")


def get_legal_moves(fen: str) -> list[str]:
    """Return all legal moves in UCI format for the given position."""
    board = parse_fen(fen)
    return [move.uci() for move in board.legal_moves]


def get_piece_map(fen: str) -> dict[str, str]:
    """
    Return a mapping of square name → piece symbol.
    Useful for frontend visualization.
    """
    board = parse_fen(fen)
    result = {}
    for square, piece in board.piece_map().items():
        square_name = chess.square_name(square)
        result[square_name] = piece.symbol()
    return result


def is_legal_move(fen: str, move_uci: str) -> bool:
    """Check if a move is legal in the given position."""
    try:
        board = parse_fen(fen)
        move = chess.Move.from_uci(move_uci)
        return move in board.legal_moves
    except ValueError:
        return False


def uci_to_san(fen: str, move_uci: str) -> str:
    """Convert a UCI move to SAN notation for the given position."""
    board = parse_fen(fen)
    move = chess.Move.from_uci(move_uci)
    return board.san(move)


def starting_fen() -> str:
    """Return the standard starting position FEN."""
    return chess.STARTING_FEN
