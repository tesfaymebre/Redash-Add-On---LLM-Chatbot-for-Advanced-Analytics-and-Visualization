"""Application configuration from environment variables."""

from __future__ import annotations

import os

from dotenv import load_dotenv

load_dotenv()


class Settings:
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "postgresql://postgres:postgres@localhost:5433/youtube_analytics",
    )
    CORS_ORIGINS: str = os.getenv("CORS_ORIGINS", "*")
    APP_ENV: str = os.getenv("APP_ENV", "development")


settings = Settings()
