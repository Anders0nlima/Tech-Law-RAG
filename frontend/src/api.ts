import type { DocumentAnalysis } from './types';

const API_BASE = '/api';

class ApiError extends Error {
  status: number;

  constructor(status: number, message: string) {
    super(message);
    this.status = status;
    this.name = 'ApiError';
  }
}

async function handleResponse<T>(response: Response): Promise<T> {
  if (!response.ok) {
    const body = await response.text();
    throw new ApiError(response.status, body || response.statusText);
  }
  return response.json() as Promise<T>;
}

/** Upload a PDF to start analysis. Returns the initial DocumentAnalysis (status: pending). */
export async function uploadDocument(file: File): Promise<DocumentAnalysis> {
  const formData = new FormData();
  formData.append('file', file);

  const response = await fetch(`${API_BASE}/analysis/`, {
    method: 'POST',
    body: formData,
  });

  return handleResponse<DocumentAnalysis>(response);
}

/** Poll analysis status by ID. */
export async function getAnalysis(id: string): Promise<DocumentAnalysis> {
  const response = await fetch(`${API_BASE}/analysis/${id}`);
  return handleResponse<DocumentAnalysis>(response);
}

/** List all analysis history. */
export async function listAnalyses(): Promise<DocumentAnalysis[]> {
  const response = await fetch(`${API_BASE}/analysis/`);
  return handleResponse<DocumentAnalysis[]>(response);
}

/** Check backend health. */
export async function getHealth(): Promise<{ status: string }> {
  const response = await fetch(`${API_BASE}/health`);
  return handleResponse<{ status: string }>(response);
}
