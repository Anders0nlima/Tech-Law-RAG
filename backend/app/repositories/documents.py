from dataclasses import dataclass
from typing import Protocol
from uuid import UUID

from psycopg import AsyncConnection
from psycopg.rows import dict_row

from app.schemas.dossier import AnalysisStatus, DocumentAnalysis, RiskDossier, RiskFinding


class DocumentRepositoryError(Exception):
    """Raised when document metadata operations fail."""


class DocumentRepository(Protocol):
    async def create_document(self, original_filename: str, content_sha256: str) -> UUID:
        """Create a new document tracking record in 'pending' status."""

    async def update_status(
        self, document_id: UUID, status: AnalysisStatus, error_message: str | None = None
    ) -> None:
        """Update the document status and optional error message."""

    async def get_document_analysis(self, document_id: UUID) -> DocumentAnalysis | None:
        """Fetch the analysis status, joined with the dossier if completed."""


@dataclass(frozen=True)
class PostgresDocumentRepository:
    database_url: str

    async def create_document(self, original_filename: str, content_sha256: str) -> UUID:
        async with await AsyncConnection.connect(self.database_url, row_factory=dict_row) as conn:
            async with conn.cursor() as cursor:
                await cursor.execute(
                    """
                    insert into public.documents (original_filename, content_sha256, status)
                    values (%s, %s, 'pending')
                    returning id
                    """,
                    (original_filename, content_sha256),
                )
                row = await cursor.fetchone()
                if row is None:
                    raise DocumentRepositoryError("Failed to insert document.")
                return row["id"]

    async def update_status(
        self, document_id: UUID, status: AnalysisStatus, error_message: str | None = None
    ) -> None:
        async with await AsyncConnection.connect(self.database_url) as conn:
            async with conn.cursor() as cursor:
                completed_at_sql = ", completed_at = now()" if status in (AnalysisStatus.COMPLETED, AnalysisStatus.FAILED) else ""
                
                await cursor.execute(
                    f"""
                    update public.documents
                    set status = %s, error_message = %s {completed_at_sql}
                    where id = %s
                    """,
                    (status.value, error_message, document_id),
                )

    async def get_document_analysis(self, document_id: UUID) -> DocumentAnalysis | None:
        async with await AsyncConnection.connect(self.database_url, row_factory=dict_row) as conn:
            async with conn.cursor() as cursor:
                await cursor.execute(
                    """
                    select d.id, d.original_filename, d.status, d.created_at, d.updated_at, d.error_message,
                           rd.id as dossier_id, rd.overall_risk_level, rd.executive_summary, rd.findings, 
                           rd.technical_recommendations, rd.generated_at
                    from public.documents d
                    left join public.risk_dossiers rd on d.id = rd.document_id
                    where d.id = %s
                    """,
                    (document_id,),
                )
                row = await cursor.fetchone()
                if row is None:
                    return None

                dossier = None
                if row["overall_risk_level"] is not None:
                    dossier = RiskDossier(
                        id=row["dossier_id"],
                        document_id=row["id"],
                        document_name=row["original_filename"],
                        generated_at=row["generated_at"],
                        executive_summary=row["executive_summary"],
                        overall_risk_level=row["overall_risk_level"],
                        findings=[RiskFinding(**f) for f in row["findings"]],
                        technical_recommendations=row["technical_recommendations"],
                    )

                return DocumentAnalysis(
                    id=row["id"],
                    document_name=row["original_filename"],
                    status=AnalysisStatus(row["status"]),
                    created_at=row["created_at"],
                    updated_at=row["updated_at"],
                    error_message=row["error_message"],
                    dossier=dossier,
                )
