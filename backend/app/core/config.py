import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    app_name: str = os.getenv("APP_NAME", "Tech-Law RAG API")
    app_version: str = os.getenv("APP_VERSION", "0.1.0")
    environment: str = os.getenv("ENVIRONMENT", "development")
    database_url: str | None = os.getenv("DATABASE_URL")
    openai_api_key: str | None = os.getenv("OPENAI_API_KEY")
    openai_embedding_model: str = os.getenv(
        "OPENAI_EMBEDDING_MODEL",
        "text-embedding-3-small",
    )
    openai_embedding_dimensions: int | None = (
        int(os.environ["OPENAI_EMBEDDING_DIMENSIONS"])
        if os.getenv("OPENAI_EMBEDDING_DIMENSIONS")
        else None
    )


settings = Settings()
