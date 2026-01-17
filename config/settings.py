"""Application configuration using pydantic-settings."""

from functools import lru_cache
from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )
    
    # API
    api_title: str = "AI-Driven Patrolling & Bandobast API"
    api_version: str = "1.0.0"
    debug: bool = False
    
    # Server
    host: str = "127.0.0.1"
    port: int = 8000
    
    # Database
    database_url: str = "sqlite:///./data/patrolling.db"
    
    # CORS
    cors_origins: str = "http://localhost:3000,http://127.0.0.1:3000"
    
    # Security
    api_key: Optional[str] = None
    rate_limit_per_minute: int = 100
    
    # RAG
    vector_store_path: str = "data/vectordb"
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    embedding_dimension: int = 384
    
    # CopMap Integration
    copmap_webhook_url: Optional[str] = None
    copmap_api_key: Optional[str] = None
    
    # Ollama LLM
    ollama_url: str = "http://localhost:11434"
    ollama_model: str = "llama3.1:8b"
    
    @property
    def cors_origins_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",")]


@lru_cache
def get_settings() -> Settings:
    return Settings()
