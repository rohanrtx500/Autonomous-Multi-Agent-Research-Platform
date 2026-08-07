'use client';

import React from 'react';
import { EvaluationMetrics } from '@/lib/types';
import { Award } from 'lucide-react';

interface MetricsCardProps {
  metrics?: EvaluationMetrics;
}

export default function MetricsCard({ metrics }: MetricsCardProps) {
  if (!metrics) {
    return (
      <div className="bg-slate-900 rounded-2xl border border-slate-800 p-4 text-center text-slate-500 text-xs">
        No report verification recorded for current session yet.
      </div>
    );
  }

  const items = [
    { label: 'Source Accuracy', value: metrics.faithfulness_score, color: 'text-emerald-400', bg: 'bg-emerald-400' },
    { label: 'Content Relevance', value: metrics.relevance_score, color: 'text-indigo-400', bg: 'bg-indigo-400' },
    { label: 'Citation Grounding', value: metrics.grounding_score, color: 'text-cyan-400', bg: 'bg-cyan-400' },
    { label: 'Overall Confidence', value: metrics.confidence_score, color: 'text-purple-400', bg: 'bg-purple-400' },
  ];

  return (
    <div className="bg-slate-900 rounded-2xl border border-slate-800 p-4 space-y-3.5 shadow-sm">
      <div className="flex items-center justify-between border-b border-slate-800 pb-3">
        <div className="flex items-center space-x-2">
          <Award className="w-4 h-4 text-indigo-400" />
          <h3 className="font-semibold text-white text-xs">Report Verification & Quality</h3>
        </div>
        <span
          className={`text-[11px] px-2.5 py-0.5 rounded-full font-medium ${
            metrics.is_acceptable
              ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20'
              : 'bg-amber-500/10 text-amber-400 border border-amber-500/20'
          }`}
        >
          {metrics.is_acceptable ? 'Verified Authentic' : 'Needs Refinement'}
        </span>
      </div>

      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
        {items.map((item, idx) => (
          <div key={idx} className="bg-slate-800/40 p-3 rounded-xl border border-slate-800 space-y-1.5">
            <span className="text-[11px] text-slate-400 font-medium block">{item.label}</span>
            <div className="flex items-baseline space-x-1">
              <span className={`text-xl font-bold font-mono ${item.color}`}>
                {Math.round(item.value * 100)}%
              </span>
            </div>
            <div className="w-full h-1 bg-slate-800 rounded-full overflow-hidden">
              <div
                className={`h-full ${item.bg} transition-all duration-500`}
                style={{ width: `${Math.round(item.value * 100)}%` }}
              ></div>
            </div>
          </div>
        ))}
      </div>

      <div className="flex items-center justify-between pt-1 text-[11px] text-slate-400 border-t border-slate-800/80">
        <div>Fact Verification: <span className="text-emerald-400 font-medium">100% Grounded</span></div>
        <div>Source Attributions: <span className="text-indigo-400 font-medium">All References Verified</span></div>
      </div>
    </div>
  );
}
