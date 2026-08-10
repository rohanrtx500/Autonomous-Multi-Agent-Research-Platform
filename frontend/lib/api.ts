import { ResearchResponse } from './types';

function getApiBase(): string {
  let envBase = process.env.NEXT_PUBLIC_API_BASE || 'http://localhost:8000/api/v1';
  envBase = envBase.trim().replace(/\/+$/, '');
  if (!envBase.endsWith('/api/v1')) {
    envBase = `${envBase}/api/v1`;
  }
  return envBase;
}

export async function runResearch(objective: string, maxIterations: number = 2): Promise<ResearchResponse> {
  const apiBase = getApiBase();
  const response = await fetch(`${apiBase}/research`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ objective, max_iterations: maxIterations }),
  });

  if (!response.ok) {
    throw new Error(`Research request failed with status: ${response.status}`);
  }

  return response.json();
}

export async function uploadDocument(file: File): Promise<{ filename: string; chunks_ingested: number; message: string }> {
  const apiBase = getApiBase();
  const formData = new FormData();
  formData.append('file', file);

  const response = await fetch(`${apiBase}/upload`, {
    method: 'POST',
    body: formData,
  });

  if (!response.ok) {
    throw new Error(`Upload failed with status: ${response.status}`);
  }

  return response.json();
}

export async function fetchMetrics(): Promise<any> {
  const apiBase = getApiBase();
  const response = await fetch(`${apiBase}/metrics`);
  if (!response.ok) return null;
  return response.json();
}

export async function fetchHealth(): Promise<boolean> {
  try {
    const apiBase = getApiBase();
    const res = await fetch(`${apiBase}/health`);
    return res.ok;
  } catch {
    return false;
  }
}
