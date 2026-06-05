from pydantic import BaseModel, Field

from app.schemas.dossier import RiskCategory, RiskLevel


class LLMRiskFinding(BaseModel):
    """
    Schema for a single risk finding identified by the LLM.
    """
    title: str = Field(description="A short, descriptive title for the risk finding.")
    category: RiskCategory = Field(description="The category of the risk.")
    risk_level: RiskLevel = Field(description="The severity level of the risk.")
    clause_reference: str | None = Field(
        default=None,
        description="The specific clause number or section reference, if available."
    )
    excerpt: str = Field(description="The exact text excerpt from the contract containing the risk.")
    rationale: str = Field(
        description="Detailed explanation of why this is a risk and its potential impact."
    )
    suggested_rewrite: str | None = Field(
        default=None,
        description="A suggested redline or rewrite to mitigate the risk."
    )
    legal_basis: list[str] = Field(
        description="List of applicable laws, regulations, or legal principles (e.g., GDPR, LGPD, CCPA).",
        default_factory=list,
    )
    confidence_score: float = Field(
        description="A confidence score between 0.0 and 1.0 for this finding.",
        ge=0.0,
        le=1.0,
    )


class LLMRiskDossierOutput(BaseModel):
    """
    Structured output schema for the entire LLM risk analysis.
    """
    executive_summary: str = Field(
        description="A high-level summary of the contract's overall risk profile."
    )
    overall_risk_level: RiskLevel = Field(
        description="The overall risk level of the entire contract."
    )
    findings: list[LLMRiskFinding] = Field(
        description="List of identified risk findings in the contract.", default_factory=list
    )
    technical_recommendations: list[str] = Field(
        description="List of technical or operational recommendations to mitigate the risks.",
        default_factory=list,
    )


def build_analysis_prompt(contract_text: str) -> list[dict[str, str]]:
    """
    Builds the messages array for the OpenAI Chat Completions API.
    """
    system_prompt = """You are an expert technology lawyer and contract analyst specializing in IT agreements, SaaS contracts, data privacy (e.g., GDPR, LGPD), and cybersecurity.
Your task is to analyze the provided contract excerpts and generate a comprehensive risk dossier in the requested structured format.

Instructions:
1. Carefully review the contract text to identify legal, security, privacy, and compliance risks.
2. For each risk, provide a clear title, categorize it, assess its severity, and quote the exact excerpt.
3. Explain the rationale behind the risk and provide a suggested rewrite to protect the client's interests.
4. Cite relevant legal bases where applicable.
5. Provide an executive summary and overall risk assessment for the entire provided text.
6. Suggest actionable technical and operational recommendations.

Be objective, precise, and professional. Focus on risks that could materially impact the business, such as data breaches, unlimited liability, intellectual property loss, or vendor lock-in.
"""
    return [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": f"Please analyze the following contract text:\n\n{contract_text}"},
    ]
