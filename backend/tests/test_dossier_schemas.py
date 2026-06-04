from uuid import uuid4

import pytest
from pydantic import ValidationError

from app.schemas import (
    AnalysisStatus,
    DocumentAnalysis,
    RiskCategory,
    RiskDossier,
    RiskFinding,
    RiskLevel,
)


def make_finding() -> RiskFinding:
    return RiskFinding(
        title="Retencao indefinida de dados",
        category=RiskCategory.DATA_RETENTION,
        risk_level=RiskLevel.HIGH,
        clause_reference="Clausula 7.2",
        excerpt="O fornecedor podera manter dados pelo tempo que entender necessario.",
        rationale="A clausula nao define prazo nem criterio objetivo de retencao.",
        suggested_rewrite="Definir prazo de retencao e rotina de descarte verificavel.",
        legal_basis=["LGPD"],
        confidence_score=0.91,
    )


def test_risk_dossier_serializes_to_frontend_contract() -> None:
    document_id = uuid4()
    dossier = RiskDossier(
        document_id=document_id,
        document_name="api-terms.pdf",
        executive_summary="Contrato exige ajustes em retencao e auditoria.",
        overall_risk_level=RiskLevel.HIGH,
        findings=[make_finding()],
        technical_recommendations=["Negociar prazos de descarte de dados."],
    )

    payload = dossier.model_dump(mode="json")

    assert payload["document_id"] == str(document_id)
    assert payload["overall_risk_level"] == "high"
    assert payload["findings"][0]["category"] == "data_retention"
    assert payload["findings"][0]["confidence_score"] == 0.91


def test_document_analysis_starts_pending_without_dossier() -> None:
    analysis = DocumentAnalysis(document_name="sla.pdf")

    assert analysis.status is AnalysisStatus.PENDING
    assert analysis.dossier is None
    assert analysis.error_message is None


def test_risk_finding_rejects_invalid_confidence_score() -> None:
    with pytest.raises(ValidationError):
        RiskFinding(
            title="Clausula sem auditoria",
            category=RiskCategory.AUDITABILITY,
            risk_level=RiskLevel.MEDIUM,
            excerpt="Nao ha previsao de logs ou auditoria.",
            rationale="Sem trilha de auditoria, incidentes ficam dificeis de apurar.",
            confidence_score=1.5,
        )
