'use client';

import React, { useState, useRef } from 'react';
import { UploadCloud, File, CheckCircle2, AlertCircle, Loader2 } from 'lucide-react';
import { uploadDocument } from '@/lib/api';

interface KnowledgeUploadProps {
  onUploadSuccess?: (filename: string, sections_ingested: number) => void;
}

export default function KnowledgeUpload({ onUploadSuccess }: KnowledgeUploadProps) {
  const [file, setFile] = useState<File | null>(null);
  const [uploading, setUploading] = useState(false);
  const [result, setResult] = useState<{ filename: string; chunks_ingested: number; message: string } | null>(null);
  const [error, setError] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0]);
      setResult(null);
      setError(null);
    }
  };

  const handleUpload = async () => {
    if (!file) return;
    setUploading(true);
    setError(null);
    try {
      const res = await uploadDocument(file);
      setResult(res);
      if (onUploadSuccess) {
        onUploadSuccess(res.filename, res.chunks_ingested);
      }
      setFile(null);
      if (fileInputRef.current) {
        fileInputRef.current.value = '';
      }
    } catch (err: any) {
      setError(err.message || 'Upload failed');
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="bg-slate-900 rounded-2xl border border-slate-800 p-5 space-y-4 shadow-sm">
      <div className="flex items-center space-x-2.5 border-b border-slate-800 pb-3">
        <UploadCloud className="w-4 h-4 text-indigo-400" />
        <div>
          <h3 className="font-semibold text-white text-xs">Upload Documents</h3>
          <p className="text-[11px] text-slate-400">Supports PDF, DOCX, TXT, MD, CSV, HTML, PPTX</p>
        </div>
      </div>

      <div className="border-2 border-dashed border-slate-800 hover:border-indigo-500/50 transition-colors rounded-xl p-6 text-center space-y-2.5 bg-slate-800/20">
        <File className="w-6 h-6 mx-auto text-slate-500" />
        <div className="text-xs text-slate-300">
          {file ? (
            <span className="font-mono text-indigo-400 font-medium">{file.name} ({(file.size / 1024).toFixed(1)} KB)</span>
          ) : (
            <span>Select a document to add to your workspace knowledge base</span>
          )}
        </div>
        <input
          ref={fileInputRef}
          type="file"
          id="fileInput"
          className="hidden"
          onChange={handleFileChange}
          accept=".pdf,.docx,.txt,.md,.csv,.html,.pptx"
        />
        <div className="flex justify-center space-x-2.5">
          <label
            htmlFor="fileInput"
            className="px-3.5 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700/80 text-xs font-medium text-white cursor-pointer transition-colors border border-slate-700/60"
          >
            Browse File
          </label>
          {file && (
            <button
              onClick={handleUpload}
              disabled={uploading}
              className="px-3.5 py-1.5 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-xs font-medium text-white transition-all flex items-center space-x-1.5 disabled:opacity-50"
            >
              {uploading ? (
                <>
                  <Loader2 className="w-3.5 h-3.5 animate-spin" />
                  <span>Processing (Indexing into Vector DB)...</span>
                </>
              ) : (
                <span>Upload & Index</span>
              )}
            </button>
          )}
        </div>
        {uploading && (
          <p className="text-[11px] text-slate-400 animate-pulse pt-1">
            Extracting text, chunking, and embedding into ChromaDB & BM25...
          </p>
        )}
      </div>

      {result && (
        <div className="p-3 rounded-xl bg-emerald-500/10 border border-emerald-500/20 text-xs text-emerald-400 flex items-center space-x-2">
          <CheckCircle2 className="w-4 h-4 shrink-0" />
          <span>Document ingested successfully ({result.chunks_ingested} sections indexed)</span>
        </div>
      )}

      {error && (
        <div className="p-3 rounded-xl bg-rose-500/10 border border-rose-500/20 text-xs text-rose-400 flex items-center space-x-2">
          <AlertCircle className="w-4 h-4 shrink-0" />
          <span>{error}</span>
        </div>
      )}
    </div>
  );
}
