"""
Security utilities — rate limiting, API key validation, etc.
Intentionally minimal for portfolio; extend as needed.
"""

from fastapi import HTTPException, Request, status


async def verify_internal_key(request: Request) -> None:
    """
    Optional internal key check for admin endpoints.
    Not enforced in development mode.
    """
    from app.core.config import settings

    if settings.is_production:
        api_key = request.headers.get("X-Internal-Key")
        if api_key != settings.SECRET_KEY:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Invalid internal key",
            )
