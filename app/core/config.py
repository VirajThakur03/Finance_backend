import os
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List, Optional

class Settings(BaseSettings):
    """
    Global application configuration.
    Initializes from environment variables with sensible defaults for development.
    """
    # Application Info
    PROJECT_NAME: str = "Personal Finance Management API"
    API_V1_STR: str = "/api/v1"
    
    # Security Configuration
    # IMPORTANT: Override SECRET_KEY in production via environment variable
    SECRET_KEY: str = os.getenv("APP_SECRET_KEY", "dev-secret-unsafe-1234567890")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7 # 7 Days

    # Database Connection
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres"
    POSTGRES_SERVER: str = "localhost" # Default to localhost for local dev
    POSTGRES_PORT: str = "5432"
    POSTGRES_DB: str = "finance_db"
    
    @property
    def DATABASE_URL(self) -> str:
        """
        Dynamically constructs the database connection string.
        Falls back to local SQLite if POSTGRES_SERVER is not explicitly provided.
        """
        if not self.POSTGRES_SERVER or self.POSTGRES_SERVER == "localhost":
            return "sqlite+aiosqlite:///./finance.db"
            
        return f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"

    # Access Control Roles
    USER_ROLES: List[str] = ["admin", "analyst", "viewer"]

    model_config = SettingsConfigDict(
        case_sensitive=True, 
        env_file=".env",
        env_file_encoding="utf-8"
    )

# Singleton instance of settings
settings = Settings()
