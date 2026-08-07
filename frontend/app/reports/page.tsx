'use client';

import React, { useState, useEffect } from 'react';
import ReportViewer from '@/components/ReportViewer';
import { FileText, Inbox, Sparkles, CheckCircle2 } from 'lucide-react';
import Link from 'next/link';

interface SavedReport {
  title: string;
  date: string;
  confidence: string;
  markdown: string;
}

export default function ReportsPage() {
  const [reports, setReports] = useState<SavedReport[]>([]);
  const [selectedIndex, setSelectedIndex] = useState<number>(0);

  useEffect(() => {
    try {
      const saved = localStorage.getItem('researchmind_reports');
      if (saved) {
        const parsed = JSON.parse(saved);
        if (Array.isArray(parsed) && parsed.length > 0) {
          setReports(parsed);
        }
      }
    } catch (e) {
      console.error('Failed to load reports from storage:', e);
    }
  }, []);

  return (
    <div className="space-y-6 max-w-6xl mx-auto">
      <div className="border-b border-slate-800 pb-4">
        <h1 className="text-xl font-bold text-white">Saved Research Reports</h1>
        <p className="text-xs text-slate-400">View and export reports synthesized during your research sessions.</p>
      </div>

      {reports.length === 0 ? (
        <div className="bg-slate-900 rounded-2xl border border-slate-800 p-10 text-center space-y-3.5 shadow-sm max-w-xl mx-auto">
          <div className="w-10 h-10 rounded-xl bg-slate-800/60 border border-slate-700/60 flex items-center justify-center mx-auto text-slate-400">
            <Inbox className="w-5 h-5" />
          </div>
          <div className="space-y-1">
            <h3 className="font-semibold text-white text-sm">No Reports Saved Yet</h3>
            <p className="text-xs text-slate-400">Run a research topic in the workspace to synthesize a report with evidence grounding and references.</p>
          </div>
          <Link
            href="/"
            className="inline-flex items-center space-x-1.5 px-4 py-2 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-medium transition-all"
          >
            <Sparkles className="w-3.5 h-3.5" />
            <span>Go to Workspace</span>
          </Link>
        </div>
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-5">
          <div className="lg:col-span-1 space-y-2">
            <div className="text-[11px] font-semibold text-slate-500 uppercase tracking-wider px-1 pb-1">
              Saved History ({reports.length})
            </div>
            {reports.map((report, idx) => (
              <div
                key={idx}
                onClick={() => setSelectedIndex(idx)}
                className={`p-3.5 rounded-xl cursor-pointer transition-all border text-xs ${
                  selectedIndex === idx
                    ? 'bg-indigo-600/15 border-indigo-500/30 text-white'
                    : 'bg-slate-900 border-slate-800 hover:bg-slate-800/50 text-slate-300'
                }`}
              >
                <div className="space-y-2">
                  <span className="font-medium text-xs leading-snug line-clamp-2 block">{report.title}</span>
                  <div className="flex items-center justify-between text-[11px] text-slate-400">
                    <span>{report.date}</span>
                    <span className="flex items-center space-x-1 px-2 py-0.5 rounded-full bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 text-[10px] font-medium">
                      <CheckCircle2 className="w-3 h-3" />
                      <span>Verified</span>
                    </span>
                  </div>
                </div>
              </div>
            ))}
          </div>

          <div className="lg:col-span-3">
            <ReportViewer
              markdown={reports[selectedIndex]?.markdown}
              title={reports[selectedIndex]?.title}
            />
          </div>
        </div>
      )}
    </div>
  );
}
