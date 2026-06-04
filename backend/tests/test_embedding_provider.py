import pytest

from app.services import (
    EmbeddingProvider,
    EmbeddingProviderError,
    MockEmbeddingProvider,
)


def assert_embedding_provider(provider: EmbeddingProvider) -> EmbeddingProvider:
    return provider


@pytest.mark.anyio
async def test_mock_embedding_provider_generates_one_vector_per_text() -> None:
    provider = MockEmbeddingProvider(dimension=6)

    embeddings = await provider.embed_texts(["clausula de dados", "sla de uptime"])

    assert len(embeddings) == 2
    assert all(len(embedding) == 6 for embedding in embeddings)
    assert embeddings[0] != embeddings[1]


@pytest.mark.anyio
async def test_mock_embedding_provider_is_deterministic() -> None:
    provider = MockEmbeddingProvider(dimension=8)

    first_result = await provider.embed_texts(["retencao de dados"])
    second_result = await provider.embed_texts(["retencao de dados"])

    assert first_result == second_result


@pytest.mark.anyio
async def test_mock_embedding_provider_rejects_empty_text() -> None:
    provider = MockEmbeddingProvider(dimension=4)

    with pytest.raises(EmbeddingProviderError, match="empty text"):
        await provider.embed_texts(["   "])


def test_mock_embedding_provider_rejects_invalid_dimension() -> None:
    with pytest.raises(EmbeddingProviderError, match="dimension"):
        MockEmbeddingProvider(dimension=0)


def test_mock_embedding_provider_matches_embedding_protocol() -> None:
    provider = assert_embedding_provider(MockEmbeddingProvider(dimension=4))

    assert isinstance(provider, MockEmbeddingProvider)
