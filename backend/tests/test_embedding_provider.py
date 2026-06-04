import pytest

from app.services import (
    EmbeddingProvider,
    EmbeddingProviderError,
    MockEmbeddingProvider,
    OpenAIEmbeddingProvider,
    create_embedding_provider,
)
from app.core.config import Settings


class FakeEmbeddingItem:
    def __init__(self, index: int, embedding: list[float]) -> None:
        self.index = index
        self.embedding = embedding


class FakeEmbeddingResponse:
    def __init__(self, data: list[FakeEmbeddingItem]) -> None:
        self.data = data


class FakeEmbeddingsResource:
    def __init__(self) -> None:
        self.last_request: dict | None = None

    async def create(self, **kwargs) -> FakeEmbeddingResponse:
        self.last_request = kwargs
        return FakeEmbeddingResponse(
            [
                FakeEmbeddingItem(index=1, embedding=[0.3, 0.4]),
                FakeEmbeddingItem(index=0, embedding=[0.1, 0.2]),
            ]
        )


class FakeOpenAIClient:
    def __init__(self) -> None:
        self.embeddings = FakeEmbeddingsResource()


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


@pytest.mark.anyio
async def test_openai_embedding_provider_sends_configured_request() -> None:
    client = FakeOpenAIClient()
    provider = OpenAIEmbeddingProvider(
        api_key="test-key",
        model="text-embedding-3-small",
        dimensions=2,
        client=client,
    )

    embeddings = await provider.embed_texts(["primeiro chunk", "segundo chunk"])

    assert embeddings == [[0.1, 0.2], [0.3, 0.4]]
    assert client.embeddings.last_request == {
        "model": "text-embedding-3-small",
        "input": ["primeiro chunk", "segundo chunk"],
        "encoding_format": "float",
        "dimensions": 2,
    }


def test_openai_embedding_provider_requires_api_key() -> None:
    with pytest.raises(EmbeddingProviderError, match="OPENAI_API_KEY"):
        OpenAIEmbeddingProvider(api_key="")


def test_create_embedding_provider_uses_openai_when_api_key_is_configured() -> None:
    provider = create_embedding_provider(
        Settings(openai_api_key="test-key", openai_embedding_dimensions=2)
    )

    assert isinstance(provider, OpenAIEmbeddingProvider)


def test_create_embedding_provider_uses_mock_without_api_key() -> None:
    provider = create_embedding_provider(Settings(openai_api_key=None))

    assert isinstance(provider, MockEmbeddingProvider)
