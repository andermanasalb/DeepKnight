"""
Application configuration via environment variables.
Uses Pydantic Settings for type-safe config with .env file support.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    # Application
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    SECRET_KEY: str = "dev-secret-key-change-in-production"
    VERSION: str = "1.0.0"

    # Database
    DATABASE_URL: str = "sqlite:///./chess.db"

    # CORS
    CORS_ORIGINS: str = "http://localhost:5173,http://localhost:3000"

    # Generative AI
    GOOGLE_API_KEY: str = ""
    GEMINI_MODEL: str = "gemini-2.0-flash"
    GEMINI_MAX_TOKENS: int = 1024

    # ML / PyTorch
    MODEL_CHECKPOINT_PATH: str = "data/models/value_net.pt"
    DEVICE: str = "cpu"

    # MLflow
    MLFLOW_TRACKING_URI: str = "./mlruns"
    MLFLOW_EXPERIMENT_NAME: str = "chess-value-net"

    # Engine
    DEFAULT_DIFFICULTY: str = "medium"
    ENGINE_TIMEOUT_SECONDS: int = 10

    @property
    def cors_origins_list(self) -> list[str]:
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]

    @property
    def is_production(self) -> bool:
        return self.ENVIRONMENT == "production"

    @property
    def is_sqlite(self) -> bool:
        return self.DATABASE_URL.startswith("sqlite")


settings = Settings()
