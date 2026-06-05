import { useMemo, useState } from 'react';
import type { RiskDossier, RiskLevel } from '../types';
import './DossierViewer.css';

interface DossierViewerProps {
  dossier: RiskDossier;
  onReset: () => void;
}

const SEVERITY_LABELS: Record<RiskLevel, string> = {
  high: 'Alto Risco',
  medium: 'Médio Risco',
  low: 'Baixo Risco',
};

const CATEGORY_LABELS: Record<string, string> = {
  privacy: 'Privacidade',
  security: 'Segurança',
  availability: 'Disponibilidade',
  liability: 'Responsabilidade',
  compliance: 'Conformidade',
  intellectual_property: 'Propriedade Intelectual',
  termination: 'Rescisão',
  data_retention: 'Retenção de Dados',
  confidentiality: 'Confidencialidade',
  auditability: 'Auditabilidade',
  other: 'Outro',
};

export default function DossierViewer({ dossier, onReset }: DossierViewerProps) {
  const [selectedSeverity, setSelectedSeverity] = useState<RiskLevel | 'all'>('all');
  const [searchQuery, setSearchQuery] = useState('');
  const [expandedFindings, setExpandedFindings] = useState<Record<string, boolean>>({});

  // Stats calculation
  const stats = useMemo(() => {
    const findings = dossier.findings || [];
    return {
      total: findings.length,
      high: findings.filter((f) => f.risk_level === 'high').length,
      medium: findings.filter((f) => f.risk_level === 'medium').length,
      low: findings.filter((f) => f.risk_level === 'low').length,
    };
  }, [dossier.findings]);

  // Filtered findings
  const filteredFindings = useMemo(() => {
    let list = dossier.findings || [];

    if (selectedSeverity !== 'all') {
      list = list.filter((f) => f.risk_level === selectedSeverity);
    }

    if (searchQuery.trim()) {
      const query = searchQuery.toLowerCase();
      list = list.filter(
        (f) =>
          f.title.toLowerCase().includes(query) ||
          f.excerpt.toLowerCase().includes(query) ||
          f.rationale.toLowerCase().includes(query) ||
          (f.clause_reference && f.clause_reference.toLowerCase().includes(query)),
      );
    }

    return list;
  }, [dossier.findings, selectedSeverity, searchQuery]);

  const toggleExpandFinding = (id: string) => {
    setExpandedFindings((prev) => ({
      ...prev,
      [id]: !prev[id],
    }));
  };

  return (
    <div className="dossier-viewer animate-fade-in">
      {/* Dashboard Top Navigation */}
      <div className="dossier-header-bar">
        <button className="btn btn-ghost" onClick={onReset}>
          ← Voltar para Upload
        </button>
        <div className="dossier-meta">
          <span className="meta-date">
            Analisado em: {new Date(dossier.generated_at).toLocaleDateString('pt-BR')}
          </span>
        </div>
      </div>

      {/* Main Title Banner */}
      <div className="dossier-title-card card">
        <div className="title-card-inner">
          <div className="title-card-info">
            <span className="badge badge-document-name">Contrato</span>
            <h1 className="dossier-title">{dossier.document_name}</h1>
          </div>
          <div className="overall-risk-badge-container">
            <span className="overall-label">Risco Geral</span>
            <span className={`overall-badge overall-badge-${dossier.overall_risk_level}`}>
              {SEVERITY_LABELS[dossier.overall_risk_level]}
            </span>
          </div>
        </div>
      </div>

      {/* Metrics Row */}
      <div className="metrics-grid">
        <div
          className={`metric-card card ${selectedSeverity === 'all' ? 'active' : ''}`}
          onClick={() => setSelectedSeverity('all')}
          role="button"
          tabIndex={0}
        >
          <div className="metric-icon">📊</div>
          <div className="metric-info">
            <span className="metric-label">Total de Riscos</span>
            <span className="metric-value">{stats.total}</span>
          </div>
        </div>

        <div
          className={`metric-card card card-risk-high ${selectedSeverity === 'high' ? 'active' : ''}`}
          onClick={() => setSelectedSeverity('high')}
          role="button"
          tabIndex={0}
        >
          <div className="metric-icon">🚨</div>
          <div className="metric-info">
            <span className="metric-label">Alto Risco</span>
            <span className="metric-value">{stats.high}</span>
          </div>
        </div>

        <div
          className={`metric-card card card-risk-medium ${selectedSeverity === 'medium' ? 'active' : ''}`}
          onClick={() => setSelectedSeverity('medium')}
          role="button"
          tabIndex={0}
        >
          <div className="metric-icon">⚠️</div>
          <div className="metric-info">
            <span className="metric-label">Médio Risco</span>
            <span className="metric-value">{stats.medium}</span>
          </div>
        </div>

        <div
          className={`metric-card card card-risk-low ${selectedSeverity === 'low' ? 'active' : ''}`}
          onClick={() => setSelectedSeverity('low')}
          role="button"
          tabIndex={0}
        >
          <div className="metric-icon">🛡️</div>
          <div className="metric-info">
            <span className="metric-label">Baixo Risco</span>
            <span className="metric-value">{stats.low}</span>
          </div>
        </div>
      </div>

      {/* Two Column Layout: Summary & Recommendations (Left) | Findings & Filters (Right) */}
      <div className="dossier-layout-grid">
        {/* Left Column: Context details */}
        <div className="dossier-sidebar">
          {/* Executive Summary */}
          <div className="card sidebar-card">
            <h3 className="card-section-title">Resumo Executivo</h3>
            <p className="executive-summary-text">{dossier.executive_summary}</p>
          </div>

          {/* Technical Recommendations */}
          <div className="card sidebar-card">
            <h3 className="card-section-title">Recomendações Técnicas</h3>
            {dossier.technical_recommendations && dossier.technical_recommendations.length > 0 ? (
              <ul className="recommendations-list">
                {dossier.technical_recommendations.map((rec, index) => (
                  <li key={index} className="recommendation-item">
                    <span className="recommendation-checkbox">✓</span>
                    <span className="recommendation-text">{rec}</span>
                  </li>
                ))}
              </ul>
            ) : (
              <p className="empty-text-small">Nenhuma recomendação técnica fornecida.</p>
            )}
          </div>
        </div>

        {/* Right Column: Findings */}
        <div className="dossier-main-content">
          {/* Filters and Search */}
          <div className="card filters-card">
            <div className="filters-header">
              <h3 className="filters-title">Filtrar Achados</h3>
              {filteredFindings.length !== stats.total && (
                <button
                  className="btn btn-link-reset"
                  onClick={() => {
                    setSelectedSeverity('all');
                    setSearchQuery('');
                  }}
                >
                  Limpar Filtros
                </button>
              )}
            </div>
            <div className="filters-controls">
              <div className="search-wrapper">
                <span className="search-icon">🔍</span>
                <input
                  type="text"
                  placeholder="Buscar na cláusula, título, explicação..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="search-input"
                />
              </div>
              <div className="severity-tabs">
                <button
                  className={`tab-btn ${selectedSeverity === 'all' ? 'active' : ''}`}
                  onClick={() => setSelectedSeverity('all')}
                >
                  Todos ({stats.total})
                </button>
                <button
                  className={`tab-btn tab-btn-high ${selectedSeverity === 'high' ? 'active' : ''}`}
                  onClick={() => setSelectedSeverity('high')}
                >
                  Alto ({stats.high})
                </button>
                <button
                  className={`tab-btn tab-btn-medium ${selectedSeverity === 'medium' ? 'active' : ''}`}
                  onClick={() => setSelectedSeverity('medium')}
                >
                  Médio ({stats.medium})
                </button>
                <button
                  className={`tab-btn tab-btn-low ${selectedSeverity === 'low' ? 'active' : ''}`}
                  onClick={() => setSelectedSeverity('low')}
                >
                  Baixo ({stats.low})
                </button>
              </div>
            </div>
          </div>

          {/* Findings List */}
          <div className="findings-section-header">
            <h3>Cláusulas com Risco ({filteredFindings.length})</h3>
          </div>

          {filteredFindings.length === 0 ? (
            <div className="card empty-findings-card">
              <div className="empty-findings-icon">🔍</div>
              <p className="empty-findings-title">Nenhum risco encontrado</p>
              <p className="empty-findings-desc">
                Tente ajustar seus filtros de severidade ou pesquisa de texto.
              </p>
            </div>
          ) : (
            <div className="findings-list">
              {filteredFindings.map((finding) => {
                const isExpanded = expandedFindings[finding.id] || false;
                return (
                  <div
                    key={finding.id}
                    className={`finding-card card risk-level-${finding.risk_level}`}
                  >
                    {/* Finding Header */}
                    <div className="finding-header" onClick={() => toggleExpandFinding(finding.id)}>
                      <div className="finding-title-group">
                        <div className="finding-badges">
                          <span className={`badge-severity badge-severity-${finding.risk_level}`}>
                            {SEVERITY_LABELS[finding.risk_level]}
                          </span>
                          <span className="badge-category">
                            {CATEGORY_LABELS[finding.category] || finding.category}
                          </span>
                        </div>
                        <h4 className="finding-title">{finding.title}</h4>
                      </div>
                      <div className="finding-meta-actions">
                        <span className="finding-confidence">
                          IA: {(finding.confidence_score * 100).toFixed(0)}%
                        </span>
                        <button className="btn-expand-arrow">
                          {isExpanded ? '▲' : '▼'}
                        </button>
                      </div>
                    </div>

                    {/* Finding Content */}
                    <div className={`finding-content ${isExpanded ? 'expanded' : 'collapsed'}`}>
                      <hr className="divider" />
                      
                      {finding.clause_reference && (
                        <div className="finding-meta-row">
                          <strong>Referência do Contrato:</strong>{' '}
                          <code className="clause-code">{finding.clause_reference}</code>
                        </div>
                      )}

                      {/* Excerpt section */}
                      <div className="finding-section">
                        <h5 className="section-label">Trecho Original do Contrato:</h5>
                        <blockquote className="excerpt-block">
                          “{finding.excerpt}”
                        </blockquote>
                      </div>

                      {/* Rationale section */}
                      <div className="finding-section">
                        <h5 className="section-label">Explicação / Racional de Risco:</h5>
                        <p className="rationale-text">{finding.rationale}</p>
                      </div>

                      {/* Legal Basis section */}
                      {finding.legal_basis && finding.legal_basis.length > 0 && (
                        <div className="finding-section">
                          <h5 className="section-label">Base Legal Aplicável:</h5>
                          <div className="legal-basis-tags">
                            {finding.legal_basis.map((basis, idx) => (
                              <span key={idx} className="legal-basis-tag">
                                ⚖️ {basis}
                              </span>
                            ))}
                          </div>
                        </div>
                      )}

                      {/* Suggested Rewrite section */}
                      {finding.suggested_rewrite && (
                        <div className="finding-section rewrite-section">
                          <h5 className="section-label">Sugestão de Reescrita (Mitigação):</h5>
                          <div className="rewrite-block">
                            <div className="rewrite-header">Redação Recomendada</div>
                            <div className="rewrite-content">
                              {finding.suggested_rewrite}
                            </div>
                          </div>
                        </div>
                      )}
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
