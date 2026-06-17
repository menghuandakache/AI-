"""Application configuration from environment variables."""
import os
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Database
    DATABASE_URL: str = "postgresql://knowledge_user:knowledge_pass@localhost:5432/ai_knowledge_platform"
    DATABASE_URL_ASYNC: str = "postgresql+asyncpg://knowledge_user:knowledge_pass@localhost:5432/ai_knowledge_platform"

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"

    # JWT
    JWT_SECRET_KEY: str = "change-me-to-a-random-secret-key-in-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_MINUTES: int = 1440

    # Upload
    UPLOAD_DIR: str = "./uploads"
    MAX_UPLOAD_SIZE_MB: int = 50

    # BGE-M3 Embedding Model
    BGE_M3_MODEL_PATH: str = "BAAI/bge-m3"
    EMBEDDING_DEVICE: str = "cpu"
    EMBEDDING_BATCH_SIZE: int = 32

    # LLM Configuration
    LLM_BASE_URL: str = "https://api.openai.com/v1"
    LLM_API_KEY: str = "your-api-key-here"
    LLM_MODEL_NAME: str = "gpt-3.5-turbo"
    LLM_MAX_TOKENS: int = 2048
    LLM_TEMPERATURE: float = 0.1

    # Chunk Configuration
    CHUNK_SIZE: int = 800
    CHUNK_OVERLAP: int = 100

    # Retrieval Configuration
    RETRIEVAL_TOP_K: int = 5
    SIMILARITY_THRESHOLD: float = 0.5

    # CORS
    CORS_ORIGINS: str = "http://localhost:5173,http://localhost:3000"

    # Admin
    DEFAULT_ADMIN_USERNAME: str = "admin"
    DEFAULT_ADMIN_PASSWORD: str = "admin123"
    DEFAULT_ADMIN_EMAIL: str = "admin@example.com"

    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """Return cached settings instance."""
    return Settings()
