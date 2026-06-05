/* ─── Risk Enums ─── */

export type RiskLevel = 'low' | 'medium' | 'high';
export type RiskCategory =
  | 'privacy'
  | 'security'
  | 'availability'
  | 'liability'
  | 'compliance'
  | 'intellectual_property'
  | 'termination'
  | 'data_retention'
  | 'confidentiality'
  | 'auditability'
  | 'other';

export type AnalysisStatus = 'pending' | 'processing' | 'completed' | 'failed';

/* ─── Domain Models ─── */

export interface RiskFinding {
  id: string;
  title: string;
  category: RiskCategory;
  risk_level: RiskLevel;
  clause_reference: string | null;
  excerpt: string;
  rationale: string;
  suggested_rewrite: string | null;
  legal_basis: string[];
  confidence_score: number;
}

export interface RiskDossier {
  id: string;
  document_id: string;
  document_name: string;
  generated_at: string;
  executive_summary: string;
  overall_risk_level: RiskLevel;
  findings: RiskFinding[];
  technical_recommendations: string[];
}

export interface DocumentAnalysis {
  id: string;
  document_name: string;
  status: AnalysisStatus;
  created_at: string;
  updated_at: string;
  dossier: RiskDossier | null;
  error_message: string | null;
}
