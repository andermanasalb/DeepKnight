"""
Database session management.

Supports both PostgreSQL (production) and SQLite (development).
Uses SQLAlchemy 2.0 async API with asyncpg / aiosqlite.
"""

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.config import settings
from app.db.base import Base


def _build_async_url(url: str) -> str:
    """Convert sync DB URL to async driver URL."""
    if url.startswith("sqlite:///"):
        return url.replace("sqlite:///", "sqlite+aiosqlite:///")
    if url.startswith("postgresql://"):
        return url.replace("postgresql://", "postgresql+asyncpg://")
    if url.startswith("postgres://"):
        return url.replace("postgres://", "postgresql+asyncpg://")
    return url


ASYNC_DATABASE_URL = _build_async_url(settings.DATABASE_URL)

engine = create_async_engine(
    ASYNC_DATABASE_URL,
    echo=settings.DEBUG,
    pool_pre_ping=True,
)

AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def init_db() -> None:
    """Create all tables if they don't exist (dev only — use Alembic for production)."""
    from app.db import models  # noqa: F401 — ensure models are registered

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all, checkfirst=True)
