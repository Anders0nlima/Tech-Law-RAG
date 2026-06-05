from app.services.analysis_prompt import (
    LLMRiskDossierOutput,
    LLMRiskFinding,
    build_analysis_prompt,
)
from app.schemas.dossier import RiskCategory, RiskLevel


def test_build_analysis_prompt():
    text = "The vendor limits liability to $100."
    messages = build_analysis_prompt(text)
    
    assert len(messages) == 2
    assert messages[0]["role"] == "system"
    assert "expert technology lawyer" in messages[0]["content"]
    assert messages[1]["role"] == "user"
    assert text in messages[1]["content"]


def test_llm_schemas():
    finding = LLMRiskFinding(
        title="Liability Limit",
        category=RiskCategory.LIABILITY,
        risk_level=RiskLevel.HIGH,
        excerpt="liability to $100",
        rationale="Too low",
        confidence_score=0.9,
    )
    assert finding.title == "Liability Limit"
    assert finding.category == RiskCategory.LIABILITY
    assert finding.risk_level == RiskLevel.HIGH
    
    dossier = LLMRiskDossierOutput(
        executive_summary="Summary",
        overall_risk_level=RiskLevel.HIGH,
        findings=[finding],
    )
    assert dossier.overall_risk_level == RiskLevel.HIGH
    assert len(dossier.findings) == 1
