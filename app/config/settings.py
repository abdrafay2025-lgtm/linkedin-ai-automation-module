"""
Settings Configuration Module.
Loads and validates environment variables using Pydantic Settings.
Strictly disallows hard-coded credentials.
"""

from typing import Literal
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application configuration schema.
    Reads values from environment variables or a local .env file.
    """

    # Application settings
    APP_ENV: Literal["development", "staging", "production"] = Field(
        default="development",
        description="Current runtime environment"
    )
    APP_NAME: str = Field(
        default="LinkedIn AI & Automation Module",
        description="Public service identifier"
    )
    APP_PORT: int = Field(
        default=8000,
        description="HTTP port for the FastAPI server"
    )
    LOG_LEVEL: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = Field(
        default="INFO",
        description="System logging threshold"
    )

    # Google Gemini settings
    GEMINI_API_KEY: str = Field(
        default="",
        description="Google Gemini API secret key"
    )
    GEMINI_MODEL: str = Field(
        default="gemini-flash-latest",
        description="Default Gemini model identifier for intelligence pipelines"
    )

    # Deterministic Boundary Limits
    MAX_KEYWORD_LENGTH: int = Field(
        default=200,
        description="Maximum permissible characters for raw search query strings"
    )
    MAX_NORMALIZED_TERMS: int = Field(
        default=15,
        description="Maximum count of allowed distinct search tokens per run"
    )

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )


# Instantiate a singleton settings instance for module-wide reuse
settings = Settings()
