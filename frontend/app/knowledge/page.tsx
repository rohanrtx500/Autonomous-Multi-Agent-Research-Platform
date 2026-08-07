'use client';

import React, { useState } from 'react';
import KnowledgeUpload from '@/components/KnowledgeUpload';
import { FileText, HardDrive, Inbox } from 'lucide-react';

export default function KnowledgePage() {
  const [documents, setDocuments] = useState<Array<{ name: string; type: string; sections: number; date: string }>>([]);

  const handleUploadSuccess = (filename: string, sections: number) => {
    const ext = filename.split('.').pop()?.toUpperCase() || 'DOC';
    setDocuments((prev) => [
      { name: filename, type: ext, sections, date: 'Just now' },
      ...prev,
    ]);
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
          <span>Storage: Secure Local Repository</span>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-5">
        <div className="lg:col-span-2 space-y-5">
          <KnowledgeUpload onUploadSuccess={handleUploadSuccess} />

          <div className="bg-slate-900 rounded-2xl border border-slate-800 p-5 space-y-3.5 shadow-sm">
            <h3 className="font-semibold text-white text-sm">Ingested Documents</h3>
            
            {documents.length === 0 ? (
              <div className="py-8 text-center text-slate-500 text-xs space-y-1.5 border border-dashed border-slate-800 rounded-xl">
                <Inbox className="w-6 h-6 mx-auto text-slate-600" />
                <p>No documents uploaded yet. Add a PDF, Word document, or text file above.</p>
              </div>
            ) : (
              <div className="space-y-2">
                {documents.map((doc, idx) => (
                  <div key={idx} className="p-3 rounded-xl bg-slate-800/40 border border-slate-800 flex items-center justify-between">
                    <div className="flex items-center space-x-2.5">
                      <FileText className="w-4 h-4 text-indigo-400" />
                      <div>
                        <span className="text-xs font-medium text-white">{doc.name}</span>
                        <p className="text-[11px] text-slate-400">{doc.type} • {doc.sections} document sections</p>
                      </div>
                    </div>
                    <span className="text-[11px] text-slate-500 font-mono">{doc.date}</span>
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
              Uploaded files are parsed, indexed, and made immediately searchable alongside arXiv papers and web sources.
            </p>
            <div className="space-y-1.5 text-[11px] pt-2 border-t border-slate-800">
              <div className="flex justify-between text-slate-400">
                <span>Index Status:</span>
                <span className="font-medium text-emerald-400">Active</span>
              </div>
              <div className="flex justify-between text-slate-400">
                <span>Parse Accuracy:</span>
                <span className="font-medium text-indigo-400">High Precision</span>
              </div>
              <div className="flex justify-between text-slate-400">
                <span>Retrieval Mode:</span>
                <span className="font-medium text-indigo-400">Semantic & Exact</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
