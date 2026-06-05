from dataclasses import dataclass, field
from uuid import uuid4

import pytest

from app.repositories import PersistableDocumentChunk
from app.repositories.document_chunks import DocumentPersistenceError, _to_pgvector_literal
from app.services import (
    DocumentChunkPersistenceError,
    PersistDocumentChunksCommand,
    TextChunk,
    persist_document_chunks,
)


@dataclass
class FakeDocumentChunkRepository:
    saved_document_id: str | None = None
    saved_total_pages: int | None = None
    saved_chunks: list[PersistableDocumentChunk] = field(default_factory=list)

    async def save_document_chunks(
        self,
        *,
        document_id: str,
        total_pages: int,
        chunks: list[PersistableDocumentChunk],
    ) -> None:
        self.saved_document_id = document_id
        self.saved_total_pages = total_pages
        self.saved_chunks = list(chunks)


@pytest.mark.anyio
async def test_persist_document_chunks_saves_metadata_and_vectorized_chunks() -> None:
    repository = FakeDocumentChunkRepository()
    doc_id = uuid4()
    command = PersistDocumentChunksCommand(
        document_id=doc_id,
        total_pages=2,
        chunks=[
            TextChunk(index=0, text="Clausula de dados", start_char=0, end_char=17),
            TextChunk(index=1, text="Clausula de SLA", start_char=10, end_char=25),
        ],
        embeddings=[[0.1, 0.2], [0.3, 0.4]],
    )

    await persist_document_chunks(command, repository)

    assert repository.saved_document_id == doc_id
    assert repository.saved_total_pages == 2
    assert repository.saved_chunks[0] == PersistableDocumentChunk(
        chunk_index=0,
        content="Clausula de dados",
        start_char=0,
        end_char=17,
        embedding=[0.1, 0.2],
    )


@pytest.mark.anyio
async def test_persist_document_chunks_rejects_embedding_count_mismatch() -> None:
    command = PersistDocumentChunksCommand(
        document_id=uuid4(),
        total_pages=1,
        chunks=[TextChunk(index=0, text="Clausula", start_char=0, end_char=8)],
        embeddings=[],
    )

    with pytest.raises(DocumentChunkPersistenceError, match="same length"):
        await persist_document_chunks(command, FakeDocumentChunkRepository())


def test_to_pgvector_literal_formats_embedding_for_pgvector() -> None:
    assert _to_pgvector_literal([0, 0.5, -1]) == "[0.0,0.5,-1.0]"


def test_to_pgvector_literal_rejects_empty_embedding() -> None:
    with pytest.raises(DocumentPersistenceError, match="cannot be empty"):
        _to_pgvector_literal([])
