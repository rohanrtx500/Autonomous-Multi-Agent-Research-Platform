'use client';

import React from 'react';
import { Network } from 'lucide-react';

export default function ArchitecturePage() {
  return (
    <div className="space-y-6 max-w-5xl mx-auto">
      <div className="border-b border-slate-800 pb-4">
        <h1 className="text-xl font-bold text-white">System Architecture</h1>
        <p className="text-xs text-slate-400">Multi-agent LangGraph state graph pipeline and parallel execution topology.</p>
      </div>

      <div className="bg-slate-900 rounded-2xl border border-slate-800 p-5 space-y-5 shadow-sm">
        <div className="flex items-center space-x-2.5 border-b border-slate-800 pb-3">
          <Network className="w-5 h-5 text-indigo-400" />
          <h2 className="text-sm font-semibold text-white">Agent Execution Topology</h2>
        </div>

        {/* Visual Graph Nodes */}
        <div className="space-y-3 font-mono text-xs">
          <div className="p-3 rounded-xl bg-indigo-600/15 border border-indigo-500/30 text-center text-indigo-300 font-semibold">
            START → Planner & Task Decomposer Agent
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-4 gap-2.5 text-center">
            <div className="p-3 rounded-xl bg-slate-800/50 border border-slate-700/60 text-slate-300">
              Paper Retrieval Agent<br/><span className="text-[10px] text-slate-400">arXiv + Semantic Scholar</span>
            </div>
            <div className="p-3 rounded-xl bg-slate-800/50 border border-slate-700/60 text-slate-300">
              Web Research Agent<br/><span className="text-[10px] text-slate-400">Tavily Web Crawler</span>
            </div>
            <div className="p-3 rounded-xl bg-slate-800/50 border border-slate-700/60 text-slate-300">
              GitHub Research Agent<br/><span className="text-[10px] text-slate-400">GitHub REST Search</span>
            </div>
            <div className="p-3 rounded-xl bg-slate-800/50 border border-slate-700/60 text-slate-300">
              Document Retrieval Agent<br/><span className="text-[10px] text-slate-400">ChromaDB + BM25</span>
            </div>
          </div>

          <div className="p-3 rounded-xl bg-slate-800/60 border border-slate-700/80 text-center text-white font-semibold">
            Knowledge Synthesizer Agent (Evidence Fusion & Deduplication)
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-3 gap-2.5 text-center">
            <div className="p-2.5 rounded-xl bg-slate-800/40 border border-slate-800 text-slate-300">
              Comparison Agent
            </div>
            <div className="p-2.5 rounded-xl bg-slate-800/40 border border-slate-800 text-slate-300">
              Research Gap Analyzer
            </div>
            <div className="p-2.5 rounded-xl bg-slate-800/40 border border-slate-800 text-slate-300">
              Experiment Planner
            </div>
          </div>

          <div className="p-3 rounded-xl bg-purple-600/15 border border-purple-500/30 text-center text-purple-300 font-semibold">
            Writer Agent (Markdown Report Generation)
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-3 gap-2.5 text-center">
            <div className="p-2.5 rounded-xl bg-slate-800/40 border border-slate-800 text-slate-300">
              Critic Agent (Self-Critique Review)
            </div>
            <div className="p-2.5 rounded-xl bg-slate-800/40 border border-slate-800 text-slate-300">
              Citation Verification Agent
            </div>
            <div className="p-2.5 rounded-xl bg-slate-800/40 border border-slate-800 text-slate-300">
              Evaluation Agent (Quality Telemetry)
            </div>
          </div>

          <div className="p-3 rounded-xl bg-emerald-500/10 border border-emerald-500/30 text-center text-emerald-400 font-semibold">
            Quality Check Verified? → [YES: END] / [NO: Report Refinement Loop → Writer Agent]
          </div>
        </div>
      </div>
    </div>
  );
}
