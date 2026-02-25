"""Configuration management for NotebookLM API and Telegram Bot."""

import os
from pathlib import Path
from typing import Optional, Union

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Application
    app_name: str = "NotebookLM API"
    app_version: str = "1.0.0"
    debug: bool = Field(default=False, alias="DEBUG")
    
    # API Settings
    api_host: str = Field(default="0.0.0.0", alias="API_HOST")
    api_port: int = Field(default=8000, alias="API_PORT")
    api_key: Optional[str] = Field(default=None, alias="API_KEY")
    api_rate_limit: int = Field(default=100, alias="API_RATE_LIMIT")  # requests per minute
    
    # Telegram Bot Settings
    telegram_bot_token: Optional[str] = Field(default=None, alias="TELEGRAM_BOT_TOKEN")
    telegram_rate_limit: int = Field(default=30, alias="TELEGRAM_RATE_LIMIT")  # messages per minute
    telegram_admin_users: list[int] = Field(default_factory=list, alias="TELEGRAM_ADMIN_USERS")
    telegram_allowed_users: list[int] = Field(default_factory=list, alias="TELEGRAM_ALLOWED_USERS")
    
    @field_validator("telegram_admin_users", "telegram_allowed_users", mode="before")
    @classmethod
    def parse_user_list(cls, v: Union[int, str, list, None]) -> list[int]:
        """Parse user list from various formats: int, str, or list."""
        if v is None:
            return []
        if isinstance(v, int):
            return [v]
        if isinstance(v, str):
            # Handle comma-separated string
            if not v.strip():
                return []
            try:
                return [int(x.strip()) for x in v.split(",") if x.strip()]
            except ValueError:
                return []
        if isinstance(v, list):
            return [int(x) if isinstance(x, (int, str)) else x for x in v]
        return []
    
    # NotebookLM Settings
    notebooklm_profile: str = Field(default="default", alias="NOTEBOOKLM_PROFILE")
    notebooklm_data_dir: Path = Field(
        default=Path.home() / ".notebooklm-mcp-cli",
        alias="NOTEBOOKLM_DATA_DIR"
    )
    notebooklm_query_timeout: float = Field(default=120.0, alias="NOTEBOOKLM_QUERY_TIMEOUT")
    notebooklm_language: str = Field(default="en", alias="NOTEBOOKLM_HL")
    
    # Studio Settings
    studio_poll_interval: int = Field(default=10, alias="STUDIO_POLL_INTERVAL")  # seconds
    studio_max_wait: int = Field(default=600, alias="STUDIO_MAX_WAIT")  # seconds
    
    # Redis (optional, for rate limiting and caching)
    redis_url: Optional[str] = Field(default=None, alias="REDIS_URL")
    
    # Logging
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"
    
    @property
    def auth_file(self) -> Path:
        """Path to the authentication file."""
        return self.notebooklm_data_dir / "auth.json"
    
    @property
    def cookies_file(self) -> Path:
        """Path to the cookies file."""
        return self.notebooklm_data_dir / f"cookies_{self.notebooklm_profile}.json"


# Global settings instance
settings = Settings()


def get_settings() -> Settings:
    """Get the settings instance."""
    return settings
