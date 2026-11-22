import { NextRequest, NextResponse } from 'next/server';

const PRODUCTION_BACKEND_URL = 'https://autonomous-multi-agent-research-platform.onrender.com/api/v1';

function resolveBackendUrl(): string {
  let base = process.env.BACKEND_API_BASE || process.env.NEXT_PUBLIC_API_BASE;
  if (!base || base.trim() === '') {
    base = PRODUCTION_BACKEND_URL;
  }
  base = base.trim().replace(/\/+$/, '');
  if (!base.startsWith('http://') && !base.startsWith('https://')) {
    base = `https://${base}`;
  }
  if (!base.endsWith('/api/v1')) {
    base = `${base}/api/v1`;
  }
  return base;
}

export async function POST(req: NextRequest) {
  try {
    const formData = await req.formData();
    const file = formData.get('file');

    if (!file || !(file instanceof Blob)) {
      return NextResponse.json(
        { detail: 'No file provided in upload payload' },
        { status: 400 }
      );
    }

    const backendBase = resolveBackendUrl();
    const targetUrl = `${backendBase}/upload`;

    // Forward the file payload to Render backend server-to-server (bypasses browser CORS completely)
    const forwardData = new FormData();
    forwardData.append('file', file, (file as any).name || 'uploaded_document');

    const backendResponse = await fetch(targetUrl, {
      method: 'POST',
      body: forwardData,
    });

    const bodyText = await backendResponse.text();
    let parsedData: any;
    try {
      parsedData = JSON.parse(bodyText);
    } catch {
      parsedData = { detail: bodyText || `Backend responded with HTTP ${backendResponse.status}` };
    }

    if (!backendResponse.ok) {
      return NextResponse.json(
        parsedData,
        { status: backendResponse.status }
      );
    }

    return NextResponse.json(parsedData, { status: 200 });
  } catch (error: any) {
    return NextResponse.json(
      { detail: `Upload proxy error: ${error?.message || 'Failed to connect to backend server'}` },
      { status: 502 }
    );
  }
}
