import { ResearchResponse } from './types';

const API_BASE = 'http://localhost:8000/api/v1';

export async function runResearch(objective: string, maxIterations: number = 2): Promise<ResearchResponse> {
  const response = await fetch(`${API_BASE}/research`, {
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
  const formData = new FormData();
  formData.append('file', file);

  const response = await fetch(`${API_BASE}/upload`, {
    method: 'POST',
    body: formData,
  });

  if (!response.ok) {
    throw new Error(`Upload failed with status: ${response.status}`);
  }

  return response.json();
}

export async function fetchMetrics(): Promise<any> {
  const response = await fetch(`${API_BASE}/metrics`);
  if (!response.ok) return null;
  return response.json();
}

export async function fetchHealth(): Promise<boolean> {
  try {
    const res = await fetch(`${API_BASE}/health`);
    return res.ok;
  } catch {
    return false;
  }
}
