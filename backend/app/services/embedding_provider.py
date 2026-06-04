from collections.abc import Sequence
from dataclasses import dataclass
from hashlib import sha256
from typing import Protocol


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
