import { useCallback, useRef, useState } from 'react';
import type { DocumentAnalysis } from '../types';
import { uploadDocument } from '../api';
import './UploadZone.css';

interface UploadZoneProps {
  onUploadComplete: (analysis: DocumentAnalysis) => void;
}

export default function UploadZone({ onUploadComplete }: UploadZoneProps) {
  const [isDragOver, setIsDragOver] = useState(false);
  const [isUploading, setIsUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFile = useCallback(
    async (file: File) => {
      if (!file.name.toLowerCase().endsWith('.pdf')) {
        setError('Apenas arquivos PDF são aceitos.');
        return;
      }
      setError(null);
      setIsUploading(true);
      try {
        const analysis = await uploadDocument(file);
        onUploadComplete(analysis);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Erro ao enviar arquivo.');
      } finally {
        setIsUploading(false);
      }
    },
    [onUploadComplete],
  );

  const handleDrop = useCallback(
    (e: React.DragEvent) => {
      e.preventDefault();
      setIsDragOver(false);
      const file = e.dataTransfer.files[0];
      if (file) handleFile(file);
    },
    [handleFile],
  );

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(true);
  }, []);

  const handleDragLeave = useCallback(() => {
    setIsDragOver(false);
  }, []);

  const handleClick = () => fileInputRef.current?.click();

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) handleFile(file);
  };

  return (
    <div className="card">
      <div className="card-header">
        <div className="card-icon">📄</div>
        <div>
          <h2 className="card-title">Analisar Contrato</h2>
          <p className="card-description">
            Faça upload de um contrato PDF para identificar riscos automaticamente
          </p>
        </div>
      </div>

      <div
        id="upload-zone"
        className={`upload-zone ${isDragOver ? 'drag-over' : ''}`}
        onDrop={handleDrop}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onClick={handleClick}
        role="button"
        tabIndex={0}
        aria-label="Área de upload de arquivo PDF"
      >
        {isUploading ? (
          <div className="upload-loading">
            <div className="spinner spinner-lg" />
            <p className="upload-text">Enviando contrato...</p>
          </div>
        ) : (
          <>
            <div className="upload-icon">⬆️</div>
            <p className="upload-text">
              Arraste um arquivo PDF aqui ou <strong>clique para selecionar</strong>
            </p>
            <p className="upload-hint">Tamanho máximo: 20 MB • Apenas PDF</p>
          </>
        )}

        <input
          ref={fileInputRef}
          type="file"
          accept=".pdf"
          onChange={handleInputChange}
          style={{ display: 'none' }}
          aria-hidden="true"
        />
      </div>

      {error && (
        <div className="upload-error">
          <span>⚠️</span> {error}
        </div>
      )}
    </div>
  );
}
