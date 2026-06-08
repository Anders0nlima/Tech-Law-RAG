import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class Settings:
    app_name: str = os.getenv("APP_NAME", "Tech-Law RAG API")
    app_version: str = os.getenv("APP_VERSION", "0.1.0")
    environment: str = os.getenv("ENVIRONMENT", "development")
    frontend_url: str = os.getenv("FRONTEND_URL", "http://localhost:5173")
    database_url: str | None = os.getenv("DATABASE_URL")
    # Google Gemini
    gemini_api_key: str | None = os.getenv("GEMINI_API_KEY")
    gemini_embedding_model: str = os.getenv(
        "GEMINI_EMBEDDING_MODEL",
        "gemini-embedding-2",
    )
    gemini_embedding_dimensions: int | None = (
        int(os.environ["GEMINI_EMBEDDING_DIMENSIONS"])
        if os.getenv("GEMINI_EMBEDDING_DIMENSIONS")
        else 768
    )
    gemini_llm_model: str = os.getenv("GEMINI_LLM_MODEL", "gemini-2.5-flash")
    # Langfuse
    langfuse_public_key: str | None = os.getenv("LANGFUSE_PUBLIC_KEY")
    langfuse_secret_key: str | None = os.getenv("LANGFUSE_SECRET_KEY")
    langfuse_host: str = os.getenv("LANGFUSE_HOST", "https://cloud.langfuse.com")


settings = Settings()
