from collections.abc import Sequence
from dataclasses import dataclass
from hashlib import sha256
from typing import Protocol

from google import genai

from app.core.config import Settings, settings


class EmbeddingProviderError(Exception):
    """Raised when embeddings cannot be generated."""


class EmbeddingProvider(Protocol):
    async def embed_texts(self, texts: Sequence[str]) -> list[list[float]]:
        """Return one embedding vector for each input text."""


@dataclass(frozen=True)
class MockEmbeddingProvider:
    dimension: int = 768

    def __post_init__(self) -> None:
        if self.dimension <= 0:
            raise EmbeddingProviderError("Embedding dimension must be greater than zero.")

    async def embed_texts(self, texts: Sequence[str]) -> list[list[float]]:
        if any(not text.strip() for text in texts):
            raise EmbeddingProviderError("Cannot embed empty text.")

        return [_build_deterministic_vector(text, self.dimension) for text in texts]


@dataclass(frozen=True)
class GeminiEmbeddingProvider:
    api_key: str
    model: str = "gemini-embedding-2"
    dimensions: int | None = 768

    def __post_init__(self) -> None:
        if not self.api_key:
            raise EmbeddingProviderError("GEMINI_API_KEY is required.")
        if self.dimensions is not None and self.dimensions <= 0:
            raise EmbeddingProviderError("Embedding dimensions must be greater than zero.")

    async def embed_texts(self, texts: Sequence[str]) -> list[list[float]]:
        if any(not text.strip() for text in texts):
            raise EmbeddingProviderError("Cannot embed empty text.")

        client = genai.Client(api_key=self.api_key)
        from google.genai import types

        try:
            config = {}
            if self.dimensions is not None:
                config["output_dimensionality"] = self.dimensions

            formatted_contents = [
                types.Content(parts=[types.Part.from_text(text=s)]) for s in texts
            ]

            result = client.models.embed_content(
                model=self.model,
                contents=formatted_contents,
                config=config if config else None,
            )
        except Exception as exc:
            raise EmbeddingProviderError(
                f"Gemini embedding request failed: {exc}"
            ) from exc

        return [list(emb.values) for emb in result.embeddings]


def create_embedding_provider(config: Settings = settings) -> EmbeddingProvider:
    if config.gemini_api_key:
        return GeminiEmbeddingProvider(
            api_key=config.gemini_api_key,
            model=config.gemini_embedding_model,
            dimensions=config.gemini_embedding_dimensions,
        )

    return MockEmbeddingProvider()


def _build_deterministic_vector(text: str, dimension: int) -> list[float]:
    values: list[float] = []
    seed = text.encode("utf-8")
    counter = 0

    while len(values) < dimension:
        digest = sha256(seed + counter.to_bytes(4, byteorder="big")).digest()

        for byte in digest:
            # Map bytes from [0, 255] into roughly [-1.0, 1.0].
            values.append(round((byte / 127.5) - 1.0, 6))
            if len(values) == dimension:
                break

        counter += 1

    return values
