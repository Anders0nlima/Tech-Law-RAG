from collections.abc import Sequence
from uuid import UUID, uuid4

import pytest

from app.repositories.document_chunks import DocumentChunkRepository, PersistableDocumentChunk, PersistedDocument
from app.schemas.dossier import RiskCategory, RiskLevel
from app.services.analysis_prompt import LLMRiskDossierOutput, LLMRiskFinding
from app.services.dossier_generator import DossierGenerationError, generate_risk_dossier
from app.services.embedding_provider import EmbeddingProvider


class FakeDocumentChunkRepository(DocumentChunkRepository):
    async def save_document_chunks(
        self,
        *,
        original_filename: str,
        content_sha256: str,
        total_pages: int,
        chunks: Sequence[PersistableDocumentChunk],
    ) -> PersistedDocument:
        pass

    async def get_relevant_chunks(
        self,
        *,
        document_id: UUID,
        query_embedding: Sequence[float],
        limit: int = 10,
    ) -> list[str]:
        return ["Chunk 1: The vendor limits liability.", "Chunk 2: Data is stored securely."]


class FakeEmbeddingProvider(EmbeddingProvider):
    async def embed_texts(self, texts: Sequence[str]) -> list[list[float]]:
        return [[0.1, 0.2, 0.3] for _ in texts]


class FakeMessage:
    def __init__(self, parsed):
        self.parsed = parsed


class FakeChoice:
    def __init__(self, message):
        self.message = message


class FakeResponse:
    def __init__(self, parsed_output):
        self.choices = [FakeChoice(FakeMessage(parsed_output))]


class FakeCompletions:
    def __init__(self, parsed_output):
        self.parsed_output = parsed_output

    async def parse(self, **kwargs):
        return FakeResponse(self.parsed_output)


class FakeChat:
    def __init__(self, parsed_output):
        self.completions = FakeCompletions(parsed_output)


class FakeBeta:
    def __init__(self, parsed_output):
        self.chat = FakeChat(parsed_output)


class FakeAsyncOpenAI:
    def __init__(self, parsed_output):
        self.beta = FakeBeta(parsed_output)


@pytest.mark.anyio
async def test_generate_risk_dossier():
    doc_id = uuid4()
    
    mock_llm_output = LLMRiskDossierOutput(
        executive_summary="Test summary",
        overall_risk_level=RiskLevel.MEDIUM,
        findings=[
            LLMRiskFinding(
                title="Liability limit",
                category=RiskCategory.LIABILITY,
                risk_level=RiskLevel.HIGH,
                excerpt="vendor limits liability",
                rationale="Too low",
                confidence_score=0.9,
            )
        ],
    )
    
    client = FakeAsyncOpenAI(mock_llm_output)
    repo = FakeDocumentChunkRepository()
    embedder = FakeEmbeddingProvider()
    
    dossier = await generate_risk_dossier(
        document_id=doc_id,
        document_name="test_contract.pdf",
        repository=repo,
        embedding_provider=embedder,
        openai_client=client,
    )
    
    assert dossier.document_id == doc_id
    assert dossier.document_name == "test_contract.pdf"
    assert dossier.executive_summary == "Test summary"
    assert dossier.overall_risk_level == RiskLevel.MEDIUM
    assert len(dossier.findings) == 1
    assert dossier.findings[0].title == "Liability limit"
