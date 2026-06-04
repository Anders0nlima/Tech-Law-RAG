from datetime import UTC, datetime
from enum import Enum
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field


class RiskLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class RiskCategory(str, Enum):
    PRIVACY = "privacy"
    SECURITY = "security"
    AVAILABILITY = "availability"
    LIABILITY = "liability"
    COMPLIANCE = "compliance"
    INTELLECTUAL_PROPERTY = "intellectual_property"
    TERMINATION = "termination"
    DATA_RETENTION = "data_retention"
    CONFIDENTIALITY = "confidentiality"
    AUDITABILITY = "auditability"
    OTHER = "other"


class AnalysisStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class RiskFinding(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: UUID = Field(default_factory=uuid4)
    title: str = Field(min_length=3)
    category: RiskCategory
    risk_level: RiskLevel
    clause_reference: str | None = None
    excerpt: str = Field(min_length=1)
    rationale: str = Field(min_length=1)
    suggested_rewrite: str | None = None
    legal_basis: list[str] = Field(default_factory=list)
    confidence_score: float = Field(ge=0, le=1)


class RiskDossier(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: UUID = Field(default_factory=uuid4)
    document_id: UUID
    document_name: str = Field(min_length=1)
    generated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    executive_summary: str = Field(min_length=1)
    overall_risk_level: RiskLevel
    findings: list[RiskFinding] = Field(default_factory=list)
    technical_recommendations: list[str] = Field(default_factory=list)


class DocumentAnalysis(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: UUID = Field(default_factory=uuid4)
    document_name: str = Field(min_length=1)
    status: AnalysisStatus = AnalysisStatus.PENDING
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    dossier: RiskDossier | None = None
    error_message: str | None = None
