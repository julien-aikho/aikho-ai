"""Application settings."""

from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    """Application settings."""
    GROQ_API_KEY: str = ""
    DATABASE_URL: str = ""
    LOGFIRE_API_KEY: str = ""
    
    model_config = SettingsConfigDict(
        env_file='.env',
        env_file_encoding='utf-8'
    )
    
    @classmethod
    def parse_env_var(cls, field_name: str, raw_val: str) -> str:
        return raw_val or ""

@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
