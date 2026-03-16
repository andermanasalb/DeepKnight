"""
FastAPI dependency injection — database sessions, model predictor, etc.
"""

from collections.abc import AsyncGenerator
from typing import Annotated

from fastapi import Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import AsyncSessionLocal
from app.ml.inference.predictor import ModelPredictor


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Yield an async database session."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


def get_predictor(request: Request) -> ModelPredictor:
    """Return the app-level ModelPredictor instance."""
    return request.app.state.predictor


# Type aliases for cleaner route signatures
DBSession = Annotated[AsyncSession, Depends(get_db)]
Predictor = Annotated[ModelPredictor, Depends(get_predictor)]
