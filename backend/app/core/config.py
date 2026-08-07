import os

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    PROJECT_NAME: str = "ResearchMind AI"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"

    # LLM Settings
    OPENAI_API_KEY: str | None = None
    GROQ_API_KEY: str | None = None
    GEMINI_API_KEY: str | None = None

    # Search & Tool APIs
    TAVILY_API_KEY: str | None = None
    GITHUB_TOKEN: str | None = None

    # Storage Settings
    CHROMA_PERSIST_DIR: str = os.path.join(os.getcwd(), "data", "chroma")
    QDRANT_HOST: str = "localhost"
    QDRANT_PORT: int = 6333
    REDIS_URL: str = "redis://localhost:6379/0"

    # Runtime Defaults
    ENVIRONMENT: str = "development"
    LOG_LEVEL: str = "INFO"
    DEFAULT_MODEL_PROVIDER: str = "openai"
    DEFAULT_MODEL_NAME: str = "gpt-4o-mini"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )


settings = Settings()
