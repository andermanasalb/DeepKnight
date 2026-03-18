"""
SQLAlchemy ORM models for persisting game data.
"""

import uuid
from datetime import UTC, datetime

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


def _uuid() -> str:
    return str(uuid.uuid4())


def _now() -> datetime:
    return datetime.now(UTC)


class Game(Base):
    """Stores chess game metadata and final state."""

    __tablename__ = "games"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    difficulty: Mapped[str] = mapped_column(String(10), nullable=False)
    player_color: Mapped[str] = mapped_column(String(5), default="white")
    status: Mapped[str] = mapped_column(String(20), default="in_progress")

    # Board state
    initial_fen: Mapped[str] = mapped_column(
        Text,
        default="rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1",
    )
    current_fen: Mapped[str] = mapped_column(Text, nullable=True)
    pgn: Mapped[str] = mapped_column(Text, nullable=True)

    # Analysis scores at game end
    final_classical_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    final_pytorch_score: Mapped[float | None] = mapped_column(Float, nullable=True)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_now
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_now, onupdate=_now
    )

    # Relationships
    moves: Mapped[list["Move"]] = relationship(
        "Move", back_populates="game", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Game {self.id[:8]} difficulty={self.difficulty} status={self.status}>"


class Move(Base):
    """Individual moves within a game."""

    __tablename__ = "moves"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    game_id: Mapped[str] = mapped_column(ForeignKey("games.id"), nullable=False)

    move_number: Mapped[int] = mapped_column(Integer, nullable=False)
    ply: Mapped[int] = mapped_column(Integer, nullable=False)  # half-moves from start
    uci: Mapped[str] = mapped_column(String(10), nullable=False)
    san: Mapped[str] = mapped_column(String(10), nullable=False)
    player: Mapped[str] = mapped_column(String(5), nullable=False)  # "white" | "black"

    # Position after this move
    fen_after: Mapped[str] = mapped_column(Text, nullable=True)

    # Evaluation after this move
    classical_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    pytorch_score: Mapped[float | None] = mapped_column(Float, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)

    # Relationships
    game: Mapped["Game"] = relationship("Game", back_populates="moves")

    def __repr__(self) -> str:
        return f"<Move {self.move_number}{'.' if self.player == 'white' else '...'}{self.san}>"
