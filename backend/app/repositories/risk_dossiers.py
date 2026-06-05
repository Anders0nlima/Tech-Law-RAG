import json
from dataclasses import dataclass
from typing import Protocol

from psycopg import AsyncConnection

from app.schemas.dossier import RiskDossier


class RiskDossierRepositoryError(Exception):
    """Raised when risk dossier operations fail."""


class RiskDossierRepository(Protocol):
    async def save_dossier(self, dossier: RiskDossier) -> None:
        """Save a generated risk dossier."""


@dataclass(frozen=True)
class PostgresRiskDossierRepository:
    database_url: str

    async def save_dossier(self, dossier: RiskDossier) -> None:
        async with await AsyncConnection.connect(self.database_url) as conn:
            async with conn.cursor() as cursor:
                findings_json = json.dumps([f.model_dump(mode="json") for f in dossier.findings])
                recommendations_json = json.dumps(dossier.technical_recommendations)

                await cursor.execute(
                    """
                    insert into public.risk_dossiers (
                        id, document_id, overall_risk_level, executive_summary,
                        findings, technical_recommendations, generated_at
                    )
                    values (%s, %s, %s, %s, %s::jsonb, %s::jsonb, %s)
                    on conflict (document_id) do update set
                        overall_risk_level = excluded.overall_risk_level,
                        executive_summary = excluded.executive_summary,
                        findings = excluded.findings,
                        technical_recommendations = excluded.technical_recommendations,
                        generated_at = excluded.generated_at
                    """,
                    (
                        dossier.id,
                        dossier.document_id,
                        dossier.overall_risk_level.value,
                        dossier.executive_summary,
                        findings_json,
                        recommendations_json,
                        dossier.generated_at,
                    ),
                )
