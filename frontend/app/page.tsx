'use client';

import React, { useState, useEffect } from 'react';
import { Search, Loader2, Sparkles, BookOpen, Database, GitBranch, Clock, Sliders } from 'lucide-react';
import { runResearch } from '@/lib/api';
import { ResearchResponse } from '@/lib/types';
import AgentTimeline from '@/components/AgentTimeline';
import MetricsCard from '@/components/MetricsCard';
import ReportViewer from '@/components/ReportViewer';

export default function WorkspacePage() {
  const [objective, setObjective] = useState('');
  const [loading, setLoading] = useState(false);
  const [researchData, setResearchData] = useState<ResearchResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  const [depthMode, setDepthMode] = useState<'standard' | 'deep' | 'comprehensive'>('deep');
  const [autoSaveEnabled, setAutoSaveEnabled] = useState(true);

  useEffect(() => {
    try {
      const stored = localStorage.getItem('researchmind_settings');
      if (stored) {
        const parsed = JSON.parse(stored);
        if (parsed.researchDepth) setDepthMode(parsed.researchDepth);
        if (typeof parsed.autoSave === 'boolean') setAutoSaveEnabled(parsed.autoSave);
      }
    } catch (e) {}
  }, []);

  const sampleObjectives = [
    'Mixture of Experts (MoE) vs Dense LLMs in 2026',
    'Self-Correction and Reflection Loops in Agent Workflows',
    'Universal Basic Income (UBI) trials on local labor market and inflation',
    'Fine-tuning Llama 3.3 for domain-specific code generation'
  ];

  const getIterationsFromDepth = (mode: string) => {
    if (mode === 'standard') return 1;
    if (mode === 'comprehensive') return 3;
    return 2; // 'deep'
  };

  const handleSubmit = async (e?: React.FormEvent, customQuery?: string) => {
    if (e) e.preventDefault();
    const query = customQuery || objective;
    if (!query || query.trim().length < 3) return;

    setLoading(true);
    setError(null);
    try {
      const iterations = getIterationsFromDepth(depthMode);
      const data = await runResearch(query, iterations);
      setResearchData(data);

      if (data.final_report_markdown && autoSaveEnabled) {
        try {
          const existing = JSON.parse(localStorage.getItem('researchmind_reports') || '[]');
          const newReport = {
            title: `Research Report: ${data.objective}`,
            date: new Date().toISOString().split('T')[0],
            confidence: data.evaluation_metrics ? `${Math.round(data.evaluation_metrics.confidence_score * 100)}%` : '94%',
            markdown: data.final_report_markdown
          };
          const filtered = existing.filter((r: any) => r.title !== newReport.title);
          localStorage.setItem('researchmind_reports', JSON.stringify([newReport, ...filtered]));
        } catch (e) {
          console.error('Error saving report:', e);
        }
      }
    } catch (err: any) {
      setError(err.message || 'Research execution failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6 max-w-6xl mx-auto">
      {/* Search Header */}
      <div className="bg-slate-900 border border-slate-800 p-6 rounded-2xl space-y-4 shadow-sm">
        <div className="space-y-1.5">
          <h1 className="text-xl font-bold text-white tracking-tight">
            Autonomous Research Assistant
          </h1>
          <p className="text-slate-400 text-xs leading-relaxed max-w-2xl">
            Enter a research objective to query arXiv, Semantic Scholar, web resources, and local knowledge bases. The agent workflow decomposes queries, compares methodologies, and formats verified reports.
          </p>
        </div>

        {/* Input Form */}
        <form onSubmit={handleSubmit} className="flex flex-col sm:flex-row gap-2.5 pt-1">
          <div className="relative flex-1">
            <Search className="w-4 h-4 absolute left-3.5 top-1/2 -translate-y-1/2 text-slate-500" />
            <input
              type="text"
              value={objective}
              onChange={(e) => setObjective(e.target.value)}
              placeholder="Enter a research topic or question..."
              className="w-full bg-slate-800/80 text-white pl-10 pr-4 py-2.5 rounded-xl border border-slate-700/80 focus:outline-none focus:border-indigo-500 text-xs transition-colors"
            />
          </div>
          <button
            type="submit"
            disabled={loading || !objective.trim()}
            className="px-5 py-2.5 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white font-medium text-xs transition-all flex items-center justify-center space-x-2 shrink-0 disabled:opacity-50"
          >
            {loading ? (
              <>
                <Loader2 className="w-3.5 h-3.5 animate-spin" />
                <span>Synthesizing...</span>
              </>
            ) : (
              <>
                <Sparkles className="w-3.5 h-3.5" />
                <span>Start Research</span>
              </>
            )}
          </button>
        </form>

        {/* Synthesis Depth Selector & Sample Topics */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pt-1 border-t border-slate-800/60">
          <div className="flex flex-wrap gap-2 items-center text-xs">
            <span className="text-slate-500 text-[11px] font-medium mr-1">Examples:</span>
            {sampleObjectives.map((prompt, idx) => (
              <button
                key={idx}
                onClick={() => {
                  setObjective(prompt);
                  handleSubmit(undefined, prompt);
                }}
                className="text-[11px] bg-slate-800/60 hover:bg-slate-800 text-slate-300 px-2 py-0.5 rounded-lg border border-slate-700/50 transition-colors text-left"
              >
                {prompt}
              </button>
            ))}
          </div>

          <div className="flex items-center space-x-1.5 shrink-0">
            <Sliders className="w-3.5 h-3.5 text-indigo-400" />
            <span className="text-[11px] text-slate-400 font-medium">Depth:</span>
            <div className="bg-slate-800/80 p-0.5 rounded-lg border border-slate-700/70 flex text-[10px]">
              <button
                type="button"
                onClick={() => setDepthMode('standard')}
                className={`px-2 py-0.5 rounded-md font-medium transition-all ${
                  depthMode === 'standard' ? 'bg-indigo-600 text-white shadow-sm' : 'text-slate-400 hover:text-slate-200'
                }`}
              >
                Standard (1-Pass)
              </button>
              <button
                type="button"
                onClick={() => setDepthMode('deep')}
                className={`px-2 py-0.5 rounded-md font-medium transition-all ${
                  depthMode === 'deep' ? 'bg-indigo-600 text-white shadow-sm' : 'text-slate-400 hover:text-slate-200'
                }`}
              >
                Deep (2-Pass)
              </button>
              <button
                type="button"
                onClick={() => setDepthMode('comprehensive')}
                className={`px-2 py-0.5 rounded-md font-medium transition-all ${
                  depthMode === 'comprehensive' ? 'bg-indigo-600 text-white shadow-sm' : 'text-slate-400 hover:text-slate-200'
                }`}
              >
                Full Audit (3-Pass)
              </button>
            </div>
          </div>
        </div>
      </div>

      {error && (
        <div className="p-3.5 rounded-xl bg-rose-500/10 border border-rose-500/30 text-rose-400 text-xs">
          {error}
        </div>
      )}

      {/* Execution Summary Cards */}
      {researchData && (
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
          <div className="bg-slate-900 p-3.5 rounded-xl border border-slate-800 flex items-center space-x-3">
            <BookOpen className="w-5 h-5 text-indigo-400" />
            <div>
              <span className="text-base font-bold text-white font-mono">{researchData.retrieved_papers_count}</span>
              <p className="text-[11px] text-slate-400">Papers Retrieved</p>
            </div>
          </div>
          <div className="bg-slate-900 p-3.5 rounded-xl border border-slate-800 flex items-center space-x-3">
            <Database className="w-5 h-5 text-cyan-400" />
            <div>
              <span className="text-base font-bold text-white font-mono">{researchData.retrieved_web_count}</span>
              <p className="text-[11px] text-slate-400">Web Articles</p>
            </div>
          </div>
          <div className="bg-slate-900 p-3.5 rounded-xl border border-slate-800 flex items-center space-x-3">
            <GitBranch className="w-5 h-5 text-purple-400" />
            <div>
              <span className="text-base font-bold text-white font-mono">{researchData.retrieved_github_count}</span>
              <p className="text-[11px] text-slate-400">Repositories</p>
            </div>
          </div>
          <div className="bg-slate-900 p-3.5 rounded-xl border border-slate-800 flex items-center space-x-3">
            <Clock className="w-5 h-5 text-emerald-400" />
            <div>
              <span className="text-base font-bold text-white font-mono">{researchData.execution_time_seconds}s</span>
              <p className="text-[11px] text-slate-400">Execution Time</p>
            </div>
          </div>
        </div>
      )}

      {/* Main Grid: Agent Steps & Report Viewer */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-5">
        <div className="lg:col-span-1">
          <AgentTimeline
            logs={researchData?.agent_logs || []}
            currentStatus={researchData?.status || 'idle'}
          />
        </div>

        <div className="lg:col-span-2 space-y-5">
          <MetricsCard
            metrics={researchData?.evaluation_metrics}
            citationVerification={researchData?.citation_verification}
          />

          <ReportViewer
            markdown={researchData?.final_report_markdown}
            title={researchData ? `Research Report: ${researchData.objective}` : undefined}
          />
        </div>
      </div>
    </div>
  );
}
