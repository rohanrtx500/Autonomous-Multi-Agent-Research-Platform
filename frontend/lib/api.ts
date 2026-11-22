import { PersistentJob, ResearchResponse } from './types';

function getApiBase(): string {
  let envBase = process.env.NEXT_PUBLIC_API_BASE || 'http://localhost:8000/api/v1';
  envBase = envBase.trim().replace(/\/+$/, '');
  if (!envBase.endsWith('/api/v1')) {
    envBase = `${envBase}/api/v1`;
  }
  return envBase;
}

export async function runResearch(
  objective: string,
  maxIterations: number = 2,
  background: boolean = false
): Promise<ResearchResponse> {
  const cleanObj = objective.trim();
  if (cleanObj.length < 3) {
    throw new Error('Research objective must be at least 3 characters long.');
  }

  const apiBase = getApiBase();
  const response = await fetch(`${apiBase}/research`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      objective: cleanObj,
      max_iterations: maxIterations,
      background: background
    }),
  });

  if (!response.ok) {
    let errorDetail = `Status ${response.status}`;
    try {
      const errBody = await response.json();
      if (errBody && errBody.detail) {
        errorDetail = typeof errBody.detail === 'string' ? errBody.detail : JSON.stringify(errBody.detail);
      }
    } catch {
      // fallback to status code
    }
    throw new Error(`Research request failed: ${errorDetail}`);
  }

  return response.json();
}

export async function getJobStatus(jobId: string): Promise<PersistentJob> {
  const apiBase = getApiBase();
  const response = await fetch(`${apiBase}/jobs/${encodeURIComponent(jobId)}`);

  if (!response.ok) {
    throw new Error(`Could not fetch status for job ${jobId} (${response.status})`);
  }

  return response.json();
}

export async function cancelJob(jobId: string): Promise<boolean> {
  const apiBase = getApiBase();
  const response = await fetch(`${apiBase}/jobs/${encodeURIComponent(jobId)}/cancel`, {
    method: 'POST',
  });
  return response.ok;
}

export async function listRecentJobs(limit: number = 20): Promise<PersistentJob[]> {
  const apiBase = getApiBase();
  const response = await fetch(`${apiBase}/jobs?limit=${limit}`);
  if (!response.ok) return [];
  return response.json();
}

export async function uploadDocument(file: File): Promise<{ filename: string; chunks_ingested: number; message: string }> {
  const maxBytes = 15 * 1024 * 1024;
  if (file.size > maxBytes) {
    throw new Error(`File size (${(file.size / (1024 * 1024)).toFixed(1)}MB) exceeds the 15MB limit.`);
  }

  const apiBase = getApiBase();
  const formData = new FormData();
  formData.append('file', file);

  const response = await fetch(`${apiBase}/upload`, {
    method: 'POST',
    body: formData,
  });

  if (!response.ok) {
    let errorDetail = `Upload error: HTTP ${response.status}`;
    try {
      const errBody = await response.json();
      if (errBody?.detail) {
        errorDetail = typeof errBody.detail === 'string' ? errBody.detail : JSON.stringify(errBody.detail);
      }
    } catch {
      // ignore
    }
    throw new Error(errorDetail);
  }

  return response.json();
}

export async function fetchMetrics(): Promise<any> {
  const apiBase = getApiBase();
  try {
    const response = await fetch(`${apiBase}/metrics`);
    if (!response.ok) return null;
    return response.json();
  } catch {
    return null;
  }
}

export async function fetchHealth(): Promise<boolean> {
  try {
    const apiBase = getApiBase();
    const res = await fetch(`${apiBase}/health`);
    if (!res.ok) return false;
    const body = await res.json();
    return body.status === 'ok' || res.ok;
  } catch {
    return false;
  }
}

export interface IngestedDocumentInfo {
  name: string;
  type: string;
  sections: number;
  source_type: string;
  date: string;
}

export async function getDocuments(): Promise<IngestedDocumentInfo[]> {
  try {
    const apiBase = getApiBase();
    const res = await fetch(`${apiBase}/documents`);
    if (!res.ok) return [];
    return res.json();
  } catch {
    return [];
  }
}

export async function deleteDocument(filename: string): Promise<boolean> {
  try {
    const apiBase = getApiBase();
    const res = await fetch(`${apiBase}/documents/${encodeURIComponent(filename)}`, {
      method: 'DELETE',
    });
    return res.ok;
  } catch {
    return false;
  }
}
