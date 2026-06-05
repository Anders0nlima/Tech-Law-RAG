import { useEffect, useState } from 'react';
import type { DocumentAnalysis } from '../types';
import { listAnalyses } from '../api';
import './AnalysisHistory.css';

interface AnalysisHistoryProps {
  onSelectAnalysis: (analysis: DocumentAnalysis) => void;
}

const STATUS_LABELS: Record<string, string> = {
  pending: 'Pendente',
  processing: 'Processando',
  completed: 'Concluído',
  failed: 'Falhou',
};

export default function AnalysisHistory({ onSelectAnalysis }: AnalysisHistoryProps) {
  const [history, setHistory] = useState<DocumentAnalysis[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let mounted = true;
    listAnalyses()
      .then((data) => {
        if (mounted) {
          setHistory(data);
          setLoading(false);
        }
      })
      .catch((err) => {
        if (mounted) {
          setError('Erro ao carregar o histórico de análises.');
          setLoading(false);
          console.error(err);
        }
      });
    return () => {
      mounted = false;
    };
  }, []);

  if (loading) {
    return (
      <div className="history-container">
        <h3 className="history-title">Histórico de Análises</h3>
        <div className="history-loading">
          <div className="spinner" />
          <span>Carregando histórico...</span>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="history-container">
        <h3 className="history-title">Histórico de Análises</h3>
        <div className="history-error">⚠️ {error}</div>
      </div>
    );
  }

  if (history.length === 0) {
    return null; // Don't show the section if there are no past analyses
  }

  return (
    <div className="history-container animate-fade-in">
      <h3 className="history-title">Histórico de Análises</h3>
      <div className="history-grid">
        {history.map((item) => (
          <div key={item.id} className="history-card card">
            <div className="history-card-main">
              <h4 className="history-doc-name">{item.document_name}</h4>
              <span className="history-date">
                {new Date(item.created_at).toLocaleDateString('pt-BR', {
                  day: '2-digit',
                  month: 'short',
                  year: 'numeric',
                  hour: '2-digit',
                  minute: '2-digit',
                })}
              </span>
            </div>
            <div className="history-card-meta">
              <span className={`badge badge-${item.status}`}>
                {STATUS_LABELS[item.status] || item.status}
              </span>
              <button
                className="btn btn-ghost history-action-btn"
                onClick={() => onSelectAnalysis(item)}
              >
                Abrir →
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
