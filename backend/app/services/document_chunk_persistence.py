from collections.abc import Sequence
from dataclasses import dataclass
from hashlib import sha256
from uuid import UUID

from app.repositories import (
    DocumentChunkRepository,
    PersistableDocumentChunk,
)
from app.services.contract_text_chunker import TextChunk


class DocumentChunkPersistenceError(Exception):
    """Raised when prepared document chunks cannot be sent to persistence."""


@dataclass(frozen=True)
class PersistDocumentChunksCommand:
    document_id: UUID
    total_pages: int
    chunks: Sequence[TextChunk]
    embeddings: Sequence[Sequence[float]]


async def persist_document_chunks(
    command: PersistDocumentChunksCommand,
    repository: DocumentChunkRepository,
) -> None:
    if len(command.chunks) != len(command.embeddings):
        raise DocumentChunkPersistenceError(
            "Chunks and embeddings must have the same length."
        )
    if not command.chunks:
        raise DocumentChunkPersistenceError("Cannot persist a document without chunks.")

    persistable_chunks = [
        PersistableDocumentChunk(
            chunk_index=chunk.index,
            content=chunk.text,
            start_char=chunk.start_char,
            end_char=chunk.end_char,
            embedding=list(embedding),
        )
        for chunk, embedding in zip(command.chunks, command.embeddings, strict=True)
    ]

    await repository.save_document_chunks(
        document_id=command.document_id,
        total_pages=command.total_pages,
        chunks=persistable_chunks,
    )
