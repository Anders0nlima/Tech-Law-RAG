from collections.abc import Sequence
from dataclasses import dataclass
from typing import Protocol
from uuid import UUID

from psycopg import AsyncConnection
from psycopg.rows import dict_row


class DocumentPersistenceError(Exception):
    """Raised when document metadata or chunks cannot be persisted."""


@dataclass(frozen=True)
class PersistableDocumentChunk:
    chunk_index: int
    content: str
    start_char: int
    end_char: int
    embedding: list[float]
    page_start: int | None = None
    page_end: int | None = None


@dataclass(frozen=True)
class PersistedDocument:
    id: UUID
    original_filename: str
    content_sha256: str
    total_pages: int
    total_chunks: int


class DocumentChunkRepository(Protocol):
    async def save_document_chunks(
        self,
        *,
        original_filename: str,
        content_sha256: str,
        total_pages: int,
        chunks: Sequence[PersistableDocumentChunk],
    ) -> PersistedDocument:
        """Persist a document record and its vectorized chunks."""

    async def get_relevant_chunks(
        self,
        *,
        document_id: UUID,
        query_embedding: Sequence[float],
        limit: int = 10,
    ) -> list[str]:
        """Retrieve the most relevant chunk contents for a given document."""


@dataclass(frozen=True)
class PostgresDocumentChunkRepository:
    database_url: str

    async def save_document_chunks(
        self,
        *,
        original_filename: str,
        content_sha256: str,
        total_pages: int,
        chunks: Sequence[PersistableDocumentChunk],
    ) -> PersistedDocument:
        if not chunks:
            raise DocumentPersistenceError("Cannot persist a document without chunks.")

        async with await AsyncConnection.connect(
            self.database_url,
            row_factory=dict_row,
        ) as conn:
            async with conn.transaction():
                document_row = await self._insert_document(
                    conn=conn,
                    original_filename=original_filename,
                    content_sha256=content_sha256,
                    total_pages=total_pages,
                    total_chunks=len(chunks),
                )
                document_id = document_row["id"]
                await self._insert_chunks(conn=conn, document_id=document_id, chunks=chunks)

        return PersistedDocument(
            id=document_row["id"],
            original_filename=document_row["original_filename"],
            content_sha256=document_row["content_sha256"],
            total_pages=document_row["total_pages"],
            total_chunks=document_row["total_chunks"],
        )

    async def get_relevant_chunks(
        self,
        *,
        document_id: UUID,
        query_embedding: Sequence[float],
        limit: int = 10,
    ) -> list[str]:
        async with await AsyncConnection.connect(
            self.database_url,
            row_factory=dict_row,
        ) as conn:
            async with conn.cursor() as cursor:
                await cursor.execute(
                    """
                    select content
                    from public.document_chunks
                    where document_id = %s
                    order by embedding <=> %s::extensions.vector
                    limit %s
                    """,
                    (document_id, _to_pgvector_literal(query_embedding), limit),
                )
                rows = await cursor.fetchall()
                return [row["content"] for row in rows]

    async def _insert_document(
        self,
        *,
        conn: AsyncConnection,
        original_filename: str,
        content_sha256: str,
        total_pages: int,
        total_chunks: int,
    ) -> dict:
        async with conn.cursor() as cursor:
            await cursor.execute(
                """
                insert into public.documents (
                    original_filename,
                    content_sha256,
                    status,
                    total_pages,
                    total_chunks
                )
                values (%s, %s, 'processing', %s, %s)
                returning id, original_filename, content_sha256, total_pages, total_chunks
                """,
                (original_filename, content_sha256, total_pages, total_chunks),
            )
            row = await cursor.fetchone()

        if row is None:
            raise DocumentPersistenceError("Failed to persist document metadata.")

        return row

    async def _insert_chunks(
        self,
        *,
        conn: AsyncConnection,
        document_id: UUID,
        chunks: Sequence[PersistableDocumentChunk],
    ) -> None:
        records = [
            (
                document_id,
                chunk.chunk_index,
                chunk.page_start,
                chunk.page_end,
                chunk.start_char,
                chunk.end_char,
                chunk.content,
                _to_pgvector_literal(chunk.embedding),
            )
            for chunk in chunks
        ]

        async with conn.cursor() as cursor:
            await cursor.executemany(
                """
                insert into public.document_chunks (
                    document_id,
                    chunk_index,
                    page_start,
                    page_end,
                    start_char,
                    end_char,
                    content,
                    embedding
                )
                values (%s, %s, %s, %s, %s, %s, %s, %s::extensions.vector)
                """,
                records,
            )


def _to_pgvector_literal(embedding: Sequence[float]) -> str:
    if not embedding:
        raise DocumentPersistenceError("Embedding vector cannot be empty.")

    return "[" + ",".join(str(float(value)) for value in embedding) + "]"
