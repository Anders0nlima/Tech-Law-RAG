from collections.abc import Sequence
from dataclasses import dataclass
from hashlib import sha256

from app.repositories import (
    DocumentChunkRepository,
    PersistableDocumentChunk,
    PersistedDocument,
)
from app.services.contract_text_chunker import TextChunk


class DocumentChunkPersistenceError(Exception):
    """Raised when prepared document chunks cannot be sent to persistence."""


@dataclass(frozen=True)
class PersistDocumentChunksCommand:
    original_filename: str
    file_bytes: bytes
    total_pages: int
    chunks: Sequence[TextChunk]
    embeddings: Sequence[Sequence[float]]


async def persist_document_chunks(
    command: PersistDocumentChunksCommand,
    repository: DocumentChunkRepository,
) -> PersistedDocument:
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

    return await repository.save_document_chunks(
        original_filename=command.original_filename,
        content_sha256=sha256(command.file_bytes).hexdigest(),
        total_pages=command.total_pages,
        chunks=persistable_chunks,
    )
