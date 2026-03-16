"""
DeepKnight — FastAPI backend entry point
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.v1 import analysis, coach, game
from app.core.config import settings
from app.core.logging import setup_logging
from app.db.session import init_db
from app.ml.inference.predictor import ModelPredictor

logger = setup_logging()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events — startup and shutdown."""
    logger.info("Starting DeepKnight API", environment=settings.ENVIRONMENT)

    # Initialize database
    await init_db()
    logger.info("Database initialized")

    # Load PyTorch model
    predictor = ModelPredictor()
    predictor.load_model(settings.MODEL_CHECKPOINT_PATH)
    app.state.predictor = predictor
    logger.info("ML model loaded", path=settings.MODEL_CHECKPOINT_PATH)

    logger.info("Application ready", version="1.0.0")
    yield

    logger.info("Shutting down DeepKnight API")


def create_app() -> FastAPI:
    app = FastAPI(
        title="DeepKnight API",
        description=(
            "Chess engine API with alpha-beta search, "
            "PyTorch position evaluation, and Gemini-powered coaching."
        ),
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc",
        lifespan=lifespan,
    )

    # CORS — allow configured origins
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Mount API routers
    app.include_router(game.router, prefix="/api/v1/game", tags=["game"])
    app.include_router(analysis.router, prefix="/api/v1/analysis", tags=["analysis"])
    app.include_router(coach.router, prefix="/api/v1/coach", tags=["coach"])

    # Health check endpoints
    @app.get("/health", tags=["health"])
    async def health():
        return JSONResponse(
            {
                "status": "ok",
                "version": "1.0.0",
                "environment": settings.ENVIRONMENT,
            }
        )

    @app.get("/health/detailed", tags=["health"])
    async def health_detailed():
        predictor: ModelPredictor = app.state.predictor
        return JSONResponse(
            {
                "status": "ok",
                "database": "connected",
                "pytorch_model": "loaded" if predictor.is_loaded else "not_loaded",
                "gemini_configured": bool(settings.GOOGLE_API_KEY),
                "version": "1.0.0",
            }
        )

    return app


app = create_app()
