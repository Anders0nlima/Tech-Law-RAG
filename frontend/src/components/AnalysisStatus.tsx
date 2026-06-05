import { useEffect, useRef, useState } from 'react';
import type { DocumentAnalysis } from '../types';
import { getAnalysis } from '../api';
import './AnalysisStatus.css';

interface AnalysisStatusProps {
  analysis: DocumentAnalysis;
  onCompleted: (analysis: DocumentAnalysis) => void;
  onReset: () => void;
}

const STATUS_LABELS: Record<string, string> = {
  pending: 'Pendente',
  processing: 'Processando',
  completed: 'Concluído',
  failed: 'Falhou',
};

const STATUS_ICONS: Record<string, string> = {
  pending: '⏳',
  processing: '⚙️',
  completed: '✅',
  failed: '❌',
};

export default function AnalysisStatus({ analysis, onCompleted, onReset }: AnalysisStatusProps) {
  const [current, setCurrent] = useState<DocumentAnalysis>(analysis);
  const intervalRef = useRef<ReturnType<typeof setInterval> | null>(null);

  useEffect(() => {
    if (current.status === 'completed' || current.status === 'failed') {
      return;
    }

    intervalRef.current = setInterval(async () => {
      try {
        const updated = await getAnalysis(current.id);
        setCurrent(updated);
        if (updated.status === 'completed') {
          onCompleted(updated);
          if (intervalRef.current) clearInterval(intervalRef.current);
        } else if (updated.status === 'failed') {
          if (intervalRef.current) clearInterval(intervalRef.current);
        }
      } catch {
        // silently retry on next interval
      }
    }, 3000);

    return () => {
      if (intervalRef.current) clearInterval(intervalRef.current);
    };
  }, [current.id, current.status, onCompleted]);

  return (
    <div className="card analysis-status-card">
      <div className="card-header">
        <div className="card-icon">{STATUS_ICONS[current.status] || '📋'}</div>
        <div>
          <h2 className="card-title">{current.document_name}</h2>
          <p className="card-description">Análise de risco do contrato</p>
        </div>
      </div>

      <div className="status-details">
        <div className="status-row">
          <span className="status-label">Status</span>
          <span className={`badge badge-${current.status}`}>
            {STATUS_LABELS[current.status]}
          </span>
        </div>
        <div className="status-row">
          <span className="status-label">Criado em</span>
          <span className="status-value">
            {new Date(current.created_at).toLocaleString('pt-BR')}
          </span>
        </div>
        <div className="status-row">
          <span className="status-label">ID</span>
          <span className="status-value status-id">{current.id}</span>
        </div>

        {current.status === 'processing' && (
          <div className="status-progress">
            <div className="progress-bar">
              <div className="progress-fill" />
            </div>
            <p className="progress-text">Analisando com IA... isso pode levar alguns minutos</p>
          </div>
        )}

        {current.status === 'failed' && current.error_message && (
          <div className="status-error">
            <strong>Erro:</strong> {current.error_message}
          </div>
        )}
      </div>

      <div className="status-actions">
        <button className="btn btn-ghost" onClick={onReset}>
          ← Novo Upload
        </button>
      </div>
    </div>
  );
}
