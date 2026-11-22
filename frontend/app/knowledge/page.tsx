'use client';

import React, { useState, useEffect } from 'react';
import KnowledgeUpload from '@/components/KnowledgeUpload';
import { FileText, HardDrive, Inbox, Trash2, RefreshCw, Loader2 } from 'lucide-react';
import { getDocuments, deleteDocument, IngestedDocumentInfo } from '@/lib/api';

export default function KnowledgePage() {
  const [documents, setDocuments] = useState<IngestedDocumentInfo[]>([]);
  const [loading, setLoading] = useState(true);
  const [deletingName, setDeletingName] = useState<string | null>(null);

  const loadDocs = async () => {
    try {
      setLoading(true);
      const docs = await getDocuments();
      setDocuments(docs);
    } catch {
      // keep fallback
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadDocs();
  }, []);

  const handleUploadSuccess = () => {
    loadDocs();
  };

  const handleDelete = async (filename: string) => {
    try {
      setDeletingName(filename);
      const success = await deleteDocument(filename);
      if (success) {
        setDocuments((prev) => prev.filter((d) => d.name !== filename));
      }
    } finally {
      setDeletingName(null);
    }
  };

  return (
    <div className="space-y-6 max-w-5xl mx-auto">
      <div className="flex items-center justify-between border-b border-slate-800 pb-4">
        <div>
          <h1 className="text-xl font-bold text-white">Document Knowledge Base</h1>
          <p className="text-xs text-slate-400">Ingest research papers, technical documentation, and PDFs into your workspace.</p>
        </div>
        <div className="flex items-center space-x-2 px-3 py-1 rounded-full bg-slate-800/60 border border-slate-700/60 text-[11px] text-slate-300 font-medium">
          <HardDrive className="w-3.5 h-3.5 text-indigo-400" />
          <span>Storage: ChromaDB & BM25</span>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-5">
        <div className="lg:col-span-2 space-y-5">
          <KnowledgeUpload onUploadSuccess={handleUploadSuccess} />

          <div className="bg-slate-900 rounded-2xl border border-slate-800 p-5 space-y-3.5 shadow-sm">
            <div className="flex items-center justify-between">
              <h3 className="font-semibold text-white text-sm">
                Ingested Documents {documents.length > 0 && `(${documents.length})`}
              </h3>
              <button
                onClick={loadDocs}
                disabled={loading}
                title="Refresh documents"
                className="p-1 rounded-lg hover:bg-slate-800 text-slate-400 hover:text-white transition-colors disabled:opacity-50"
              >
                <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} />
              </button>
            </div>
            
            {loading ? (
              <div className="py-8 text-center text-slate-500 text-xs flex justify-center items-center space-x-2">
                <Loader2 className="w-4 h-4 animate-spin text-indigo-400" />
                <span>Loading indexed documents...</span>
              </div>
            ) : documents.length === 0 ? (
              <div className="py-8 text-center text-slate-500 text-xs space-y-1.5 border border-dashed border-slate-800 rounded-xl">
                <Inbox className="w-6 h-6 mx-auto text-slate-600" />
                <p>No documents uploaded yet. Add a PDF, Word document, or text file above.</p>
              </div>
            ) : (
              <div className="space-y-2">
                {documents.map((doc, idx) => (
                  <div key={idx} className="p-3 rounded-xl bg-slate-800/40 border border-slate-800 flex items-center justify-between group hover:border-slate-700 transition-colors">
                    <div className="flex items-center space-x-2.5 min-w-0">
                      <FileText className="w-4 h-4 text-indigo-400 shrink-0" />
                      <div className="min-w-0">
                        <span className="text-xs font-medium text-white truncate block">{doc.name}</span>
                        <p className="text-[11px] text-slate-400">{doc.type} • {doc.sections} document sections indexed</p>
                      </div>
                    </div>
                    <div className="flex items-center space-x-3 shrink-0">
                      <span className="text-[11px] text-emerald-400 font-mono hidden sm:inline">{doc.date}</span>
                      <button
                        onClick={() => handleDelete(doc.name)}
                        disabled={deletingName === doc.name}
                        title={`Delete ${doc.name}`}
                        className="p-1.5 rounded-lg text-slate-500 hover:text-rose-400 hover:bg-rose-500/10 transition-colors disabled:opacity-50"
                      >
                        {deletingName === doc.name ? (
                          <Loader2 className="w-3.5 h-3.5 animate-spin text-rose-400" />
                        ) : (
                          <Trash2 className="w-3.5 h-3.5" />
                        )}
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>

        <div className="space-y-4">
          <div className="bg-slate-900 rounded-2xl border border-slate-800 p-4 space-y-2.5">
            <h4 className="font-medium text-white text-xs">Document Processing & Indexing</h4>
            <p className="text-[11px] text-slate-400 leading-relaxed">
              Uploaded files are parsed, chunked with boundary awareness, and embedded into persistent ChromaDB & BM25 for hybrid semantic and keyword retrieval.
            </p>
            <div className="space-y-1.5 text-[11px] pt-2 border-t border-slate-800">
              <div className="flex justify-between text-slate-400">
                <span>Index Status:</span>
                <span className="font-medium text-emerald-400">Active</span>
              </div>
              <div className="flex justify-between text-slate-400">
                <span>Vector Engine:</span>
                <span className="font-medium text-indigo-400">ChromaDB Persistent</span>
              </div>
              <div className="flex justify-between text-slate-400">
                <span>Lexical Engine:</span>
                <span className="font-medium text-indigo-400">BM25 Okapi</span>
              </div>
              <div className="flex justify-between text-slate-400">
                <span>Retrieval Mode:</span>
                <span className="font-medium text-indigo-400">Hybrid (Dense + Sparse)</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
