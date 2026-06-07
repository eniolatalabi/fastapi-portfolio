from typing import Optional

from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings, loaded from environment variables or .env.

    Either DATABASE_URL (typical on Render) or the five discrete
    DATABASE_* variables (typical locally) must be provided.
    """

    database_url: Optional[str] = None
    database_hostname: Optional[str] = None
    database_port: Optional[str] = None
    database_password: Optional[str] = None
    database_name: Optional[str] = None
    database_username: Optional[str] = None

    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    # Comma-separated allowlist of browser origins.
    cors_origins: str = "http://localhost:3000,http://127.0.0.1:3000"

    model_config = SettingsConfigDict(env_file=".env")

    @model_validator(mode="after")
    def require_a_database_source(self):
        discrete = [self.database_hostname, self.database_port,
                    self.database_password, self.database_name,
                    self.database_username]
        if not self.database_url and not all(discrete):
            raise ValueError(
                "Database not configured: set DATABASE_URL or all five "
                "DATABASE_* variables. See .env.example."
            )
        return self

    @property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",")
                if origin.strip()]


settings = Settings()
