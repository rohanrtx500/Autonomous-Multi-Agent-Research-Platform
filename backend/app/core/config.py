import os
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

# Base directories computed relative to this file
_CURRENT_DIR = Path(__file__).resolve().parent
_BACKEND_DIR = _CURRENT_DIR.parent.parent
_REPO_ROOT = _BACKEND_DIR.parent
_DEFAULT_DATA_DIR = str(_BACKEND_DIR / "data")
_DEFAULT_UPLOAD_DIR = str(_BACKEND_DIR / "data" / "uploads")
_DEFAULT_CHROMA_DIR = str(_BACKEND_DIR / "data" / "chroma")
_DEFAULT_DB_PATH = str(_BACKEND_DIR / "data" / "researchmind.db")


class Settings(BaseSettings):
    PROJECT_NAME: str = "ResearchMind AI"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    PROJECT_ROOT: str = str(_REPO_ROOT)
    BACKEND_ROOT: str = str(_BACKEND_DIR)

    # LLM Settings
    OPENAI_API_KEY: str | None = None
    GROQ_API_KEY: str | None = None
    GEMINI_API_KEY: str | None = None

    # Search & Tool APIs
    TAVILY_API_KEY: str | None = None
    GITHUB_TOKEN: str | None = None

    # Storage & Upload Settings
    DATA_DIR: str = _DEFAULT_DATA_DIR
    UPLOAD_DIR: str = _DEFAULT_UPLOAD_DIR
    CHROMA_PERSIST_DIR: str = _DEFAULT_CHROMA_DIR
    MAX_UPLOAD_SIZE_BYTES: int = 15 * 1024 * 1024  # 15 MB limit
    ALLOWED_EXTENSIONS: list[str] = [".pdf", ".docx", ".pptx", ".txt", ".md"]

    # Database Persistence (PostgreSQL with SQLite local fallback)
    DATABASE_URL: str = f"sqlite:///{_DEFAULT_DB_PATH}"

    # Distributed / Optional Infra settings
    QDRANT_HOST: str = "localhost"
    QDRANT_PORT: int = 6333
    REDIS_URL: str = "redis://localhost:6379/0"

    # Runtime Defaults & Policies
    ENVIRONMENT: str = "development"
    LOG_LEVEL: str = "INFO"
    DEFAULT_MODEL_PROVIDER: str = "gemini"
    DEFAULT_MODEL_NAME: str = "gemini-3.5-flash-lite"
    CORS_ORIGINS: list[str] = ["http://localhost:3000", "http://127.0.0.1:3000"]
    JOB_TIMEOUT_SECONDS: int = 300
    JOB_RETENTION_DAYS: int = 30

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )


settings = Settings()

# Ensure standard storage directories exist
os.makedirs(settings.DATA_DIR, exist_ok=True)
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
os.makedirs(settings.CHROMA_PERSIST_DIR, exist_ok=True)
