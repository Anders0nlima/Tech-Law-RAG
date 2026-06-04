from collections.abc import Sequence
from dataclasses import dataclass
from hashlib import sha256
from typing import Any, Protocol

from openai import APIError, APIStatusError, AsyncOpenAI

from app.core.config import Settings, settings


class EmbeddingProviderError(Exception):
    """Raised when embeddings cannot be generated."""


class EmbeddingProvider(Protocol):
    async def embed_texts(self, texts: Sequence[str]) -> list[list[float]]:
        """Return one embedding vector for each input text."""


@dataclass(frozen=True)
class MockEmbeddingProvider:
    dimension: int = 1536

    def __post_init__(self) -> None:
        if self.dimension <= 0:
            raise EmbeddingProviderError("Embedding dimension must be greater than zero.")

    async def embed_texts(self, texts: Sequence[str]) -> list[list[float]]:
        if any(not text.strip() for text in texts):
            raise EmbeddingProviderError("Cannot embed empty text.")

        return [_build_deterministic_vector(text, self.dimension) for text in texts]


@dataclass(frozen=True)
class OpenAIEmbeddingProvider:
    api_key: str
    model: str = "text-embedding-3-small"
    dimensions: int | None = 1536
    client: Any | None = None

    def __post_init__(self) -> None:
        if not self.api_key:
            raise EmbeddingProviderError("OPENAI_API_KEY is required.")
        if self.dimensions is not None and self.dimensions <= 0:
            raise EmbeddingProviderError("Embedding dimensions must be greater than zero.")

    async def embed_texts(self, texts: Sequence[str]) -> list[list[float]]:
        if any(not text.strip() for text in texts):
            raise EmbeddingProviderError("Cannot embed empty text.")

        client = self.client or AsyncOpenAI(api_key=self.api_key)
        request: dict[str, Any] = {
            "model": self.model,
            "input": list(texts),
            "encoding_format": "float",
        }

        if self.dimensions is not None:
            request["dimensions"] = self.dimensions

        try:
            response = await client.embeddings.create(**request)
        except (APIError, APIStatusError) as exc:
            raise EmbeddingProviderError("OpenAI embedding request failed.") from exc

        ordered_embeddings = sorted(response.data, key=lambda item: item.index)
        return [list(item.embedding) for item in ordered_embeddings]


def create_embedding_provider(config: Settings = settings) -> EmbeddingProvider:
    if config.openai_api_key:
        return OpenAIEmbeddingProvider(
            api_key=config.openai_api_key,
            model=config.openai_embedding_model,
            dimensions=config.openai_embedding_dimensions,
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
