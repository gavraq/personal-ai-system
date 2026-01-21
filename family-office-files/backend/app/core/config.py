"""
Application configuration settings
"""
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""

    # Database
    database_url: str = "postgresql://fop_user:fop_password@db:5432/fop_db"

    # JWT
    jwt_secret: str = "your-super-secret-jwt-key-change-in-production"
    jwt_expiry_minutes: int = 15
    refresh_token_expiry_days: int = 7

    # Redis
    redis_url: str = "redis://redis:6379/0"

    # Google Cloud
    gcs_bucket: str = "fop-files"
    google_client_id: str = ""
    google_client_secret: str = ""
    google_redirect_uri: str = "http://localhost:8000/api/integrations/google/callback"

    # AI
    anthropic_api_key: str = ""

    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()
