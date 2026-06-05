import { useCallback, useEffect, useState } from 'react';
import UploadZone from './components/UploadZone';
import AnalysisStatus from './components/AnalysisStatus';
import type { DocumentAnalysis } from './types';
import { getHealth } from './api';
import './App.css';

type AppView = 'upload' | 'status';

function App() {
  const [view, setView] = useState<AppView>('upload');
  const [analysis, setAnalysis] = useState<DocumentAnalysis | null>(null);
  const [backendOnline, setBackendOnline] = useState(false);

  useEffect(() => {
    getHealth()
      .then(() => setBackendOnline(true))
      .catch(() => setBackendOnline(false));
  }, []);

  const handleUploadComplete = useCallback((result: DocumentAnalysis) => {
    setAnalysis(result);
    setView('status');
  }, []);

  const handleAnalysisCompleted = useCallback((result: DocumentAnalysis) => {
    setAnalysis(result);
  }, []);

  const handleReset = useCallback(() => {
    setAnalysis(null);
    setView('upload');
  }, []);

  return (
    <div className="app-layout">
      {/* Header */}
      <header className="app-header">
        <div className="header-inner">
          <div className="header-brand">
            <div className="header-logo">⚖</div>
            <div>
              <h1 className="header-title">Tech-Law RAG</h1>
              <span className="header-subtitle">Análise de Riscos em Contratos</span>
            </div>
          </div>
          <div className="header-status">
            <div className={`status-dot ${backendOnline ? '' : 'offline'}`} />
            <span>{backendOnline ? 'API Online' : 'API Offline'}</span>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="app-main">
        <div className="hero-section">
          <h2 className="section-title">
            Identifique riscos contratuais com IA
          </h2>
          <p className="section-subtitle">
            Upload de contratos em PDF • Análise automatizada • Dossiê de riscos detalhado
          </p>
        </div>

        {view === 'upload' && (
          <UploadZone onUploadComplete={handleUploadComplete} />
        )}

        {view === 'status' && analysis && (
          <AnalysisStatus
            analysis={analysis}
            onCompleted={handleAnalysisCompleted}
            onReset={handleReset}
          />
        )}

        {/* Feature Cards */}
        {view === 'upload' && (
          <div className="features-grid">
            <div className="feature-card card">
              <div className="feature-icon">🔍</div>
              <h3 className="feature-title">Análise Semântica</h3>
              <p className="feature-text">
                Busca vetorial com embeddings encontra as cláusulas mais relevantes para revisão.
              </p>
            </div>
            <div className="feature-card card">
              <div className="feature-icon">🛡️</div>
              <h3 className="feature-title">Classificação de Riscos</h3>
              <p className="feature-text">
                Cada risco é categorizado por tipo, severidade e base legal (LGPD, GDPR, etc).
              </p>
            </div>
            <div className="feature-card card">
              <div className="feature-icon">✍️</div>
              <h3 className="feature-title">Sugestão de Reescrita</h3>
              <p className="feature-text">
                A IA sugere redação alternativa para mitigar os riscos identificados.
              </p>
            </div>
          </div>
        )}
      </main>

      {/* Footer */}
      <footer className="app-footer">
        <p>Tech-Law RAG · Análise de contratos com IA &copy; {new Date().getFullYear()}</p>
      </footer>
    </div>
  );
}

export default App;
