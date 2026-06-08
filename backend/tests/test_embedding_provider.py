import pytest

from app.services import (
    EmbeddingProvider,
    EmbeddingProviderError,
    MockEmbeddingProvider,
    GeminiEmbeddingProvider,
    create_embedding_provider,
)
from app.core.config import Settings


class FakeEmbeddingValue:
    def __init__(self, values: list[float]) -> None:
        self.values = values


class FakeEmbeddingResponse:
    def __init__(self, embeddings: list[FakeEmbeddingValue]) -> None:
        self.embeddings = embeddings


class FakeModels:
    def __init__(self) -> None:
        self.last_request: dict | None = None

    def embed_content(self, **kwargs) -> FakeEmbeddingResponse:
        self.last_request = kwargs
        return FakeEmbeddingResponse(
            [
                FakeEmbeddingValue([0.1, 0.2]),
                FakeEmbeddingValue([0.3, 0.4]),
            ]
        )


class FakeGeminiClient:
    def __init__(self) -> None:
        self.models = FakeModels()


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
async def test_gemini_embedding_provider_sends_configured_request() -> None:
    fake_client = FakeGeminiClient()
    provider = GeminiEmbeddingProvider(
        api_key="test-key",
        model="gemini-embedding-2",
        dimensions=2,
    )
    # Monkey-patch the client creation to use our fake
    import app.services.embedding_provider as ep
    original_client_class = ep.genai.Client
    ep.genai.Client = lambda **kwargs: fake_client

    try:
        embeddings = await provider.embed_texts(["primeiro chunk", "segundo chunk"])

        assert embeddings == [[0.1, 0.2], [0.3, 0.4]]
        assert fake_client.models.last_request["model"] == "gemini-embedding-2"
        from google.genai import types
        contents = fake_client.models.last_request["contents"]
        assert len(contents) == 2
        assert contents[0].parts[0].text == "primeiro chunk"
        assert contents[1].parts[0].text == "segundo chunk"
    finally:
        ep.genai.Client = original_client_class


def test_gemini_embedding_provider_requires_api_key() -> None:
    with pytest.raises(EmbeddingProviderError, match="GEMINI_API_KEY"):
        GeminiEmbeddingProvider(api_key="")


def test_create_embedding_provider_uses_gemini_when_api_key_is_configured() -> None:
    provider = create_embedding_provider(
        Settings(gemini_api_key="test-key", gemini_embedding_dimensions=2)
    )

    assert isinstance(provider, GeminiEmbeddingProvider)


def test_create_embedding_provider_uses_mock_without_api_key() -> None:
    provider = create_embedding_provider(Settings(gemini_api_key=None))

    assert isinstance(provider, MockEmbeddingProvider)
