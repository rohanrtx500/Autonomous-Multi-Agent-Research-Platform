'use client';

import React, { useState } from 'react';
import { EvaluationMetrics, CitationVerificationResult } from '@/lib/types';
import { Award, Info, CheckCircle2, AlertTriangle, XCircle, HelpCircle } from 'lucide-react';

interface MetricsCardProps {
  metrics?: EvaluationMetrics;
  citationVerification?: CitationVerificationResult;
}

export default function MetricsCard({ metrics, citationVerification }: MetricsCardProps) {
  const [showDetails, setShowDetails] = useState(false);

  if (!metrics) {
    return (
      <div className="bg-slate-900 rounded-2xl border border-slate-800 p-4 text-center text-slate-500 text-xs">
        No report verification recorded for current session yet.
      </div>
    );
  }

  const primaryItems = [
    {
      label: 'Faithfulness',
      value: metrics.faithfulness_score,
      color: 'text-emerald-400',
      bg: 'bg-emerald-400',
      desc: 'Proportion of factual claims grounded in retrieved evidence.'
    },
    {
      label: 'Answer Relevance',
      value: metrics.relevance_score,
      color: 'text-indigo-400',
      bg: 'bg-indigo-400',
      desc: 'Thematic alignment between generated report and research objective.'
    },
    {
      label: 'Context Relevance',
      value: metrics.context_relevance ?? metrics.grounding_score,
      color: 'text-cyan-400',
      bg: 'bg-cyan-400',
      desc: 'Lexical alignment of retrieved source chunks with query terms.'
    },
    {
      label: 'Overall Confidence',
      value: metrics.confidence_score,
      color: 'text-purple-400',
      bg: 'bg-purple-400',
      desc: 'Weighted multi-factor score across groundedness and retrieval quality.'
    },
  ];

  const precision = metrics.precision_at_k !== null && metrics.precision_at_k !== undefined ? `${Math.round(metrics.precision_at_k * 100)}%` : 'N/A';
  const mrr = metrics.mrr !== null && metrics.mrr !== undefined ? metrics.mrr.toFixed(2) : 'N/A';
  const coverage = metrics.citation_coverage !== null && metrics.citation_coverage !== undefined ? `${Math.round(metrics.citation_coverage * 100)}%` : 'N/A';
  const unsupportedRate = metrics.unsupported_claim_rate !== null && metrics.unsupported_claim_rate !== undefined ? `${Math.round(metrics.unsupported_claim_rate * 100)}%` : '0%';

  return (
    <div className="bg-slate-900 rounded-2xl border border-slate-800 p-4 space-y-3.5 shadow-sm">
      <div className="flex items-center justify-between border-b border-slate-800 pb-3">
        <div className="flex items-center space-x-2">
          <Award className="w-4 h-4 text-indigo-400" />
          <h3 className="font-semibold text-white text-xs">Measurable Evaluation & Verification</h3>
        </div>
        <div className="flex items-center space-x-2">
          <button
            onClick={() => setShowDetails(!showDetails)}
            className="text-[11px] text-slate-400 hover:text-slate-200 transition flex items-center space-x-1"
          >
            <Info className="w-3.5 h-3.5" />
            <span>{showDetails ? 'Hide Details' : 'Methodology'}</span>
          </button>
          <span
            className={`text-[11px] px-2.5 py-0.5 rounded-full font-medium ${
              metrics.is_acceptable
                ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20'
                : 'bg-amber-500/10 text-amber-400 border border-amber-500/20'
            }`}
          >
            {metrics.is_acceptable ? 'Verification Passed' : 'Refinement Advised'}
          </span>
        </div>
      </div>

      {/* Primary Scores Grid */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
        {primaryItems.map((item, idx) => (
          <div key={idx} className="bg-slate-800/40 p-3 rounded-xl border border-slate-800 space-y-1.5" title={item.desc}>
            <span className="text-[11px] text-slate-400 font-medium block truncate">{item.label}</span>
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

      {/* Information Retrieval & Claim Stats */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 pt-1 border-t border-slate-800/60 text-[11px]">
        <div className="bg-slate-800/20 px-2.5 py-1.5 rounded-lg border border-slate-800/60">
          <span className="text-slate-500 block text-[10px]">Retrieval Precision@5</span>
          <span className="font-mono font-semibold text-slate-200">{precision}</span>
        </div>
        <div className="bg-slate-800/20 px-2.5 py-1.5 rounded-lg border border-slate-800/60">
          <span className="text-slate-500 block text-[10px]">Mean Reciprocal Rank (MRR)</span>
          <span className="font-mono font-semibold text-slate-200">{mrr}</span>
        </div>
        <div className="bg-slate-800/20 px-2.5 py-1.5 rounded-lg border border-slate-800/60">
          <span className="text-slate-500 block text-[10px]">Citation Coverage</span>
          <span className="font-mono font-semibold text-slate-200">{coverage}</span>
        </div>
        <div className="bg-slate-800/20 px-2.5 py-1.5 rounded-lg border border-slate-800/60">
          <span className="text-slate-500 block text-[10px]">Unsupported Claim Rate</span>
          <span className={`font-mono font-semibold ${metrics.unsupported_claim_rate && metrics.unsupported_claim_rate > 0.25 ? 'text-amber-400' : 'text-slate-200'}`}>
            {unsupportedRate}
          </span>
        </div>
      </div>

      {/* Optional Claim-level Breakdown if available */}
      {citationVerification && citationVerification.claim_details && citationVerification.claim_details.length > 0 && (
        <div className="pt-2 border-t border-slate-800/60 space-y-1.5">
          <span className="text-[11px] font-medium text-slate-400 block">Extracted Factual Claims Status:</span>
          <div className="max-h-36 overflow-y-auto space-y-1 pr-1 text-[11px]">
            {citationVerification.claim_details.map((claim, cIdx) => (
              <div key={cIdx} className="bg-slate-800/30 p-2 rounded-lg border border-slate-800/40 flex items-start justify-between gap-2">
                <div className="space-y-0.5 flex-1">
                  <p className="text-slate-300 text-[11px] leading-snug">{claim.claim_text}</p>
                  {claim.evidence_snippets.length > 0 && (
                    <p className="text-slate-500 text-[10px] italic">Evidence: &ldquo;{claim.evidence_snippets[0].slice(0, 120)}...&rdquo;</p>
                  )}
                </div>
                <span className={`text-[10px] px-2 py-0.5 rounded-md whitespace-nowrap font-medium flex items-center space-x-1 ${
                  claim.status === 'supported' ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20' :
                  claim.status === 'partially_supported' ? 'bg-cyan-500/10 text-cyan-400 border border-cyan-500/20' :
                  claim.status === 'unsupported' ? 'bg-rose-500/10 text-rose-400 border border-rose-500/20' :
                  'bg-amber-500/10 text-amber-400 border border-amber-500/20'
                }`}>
                  {claim.status === 'supported' && <CheckCircle2 className="w-3 h-3 mr-0.5" />}
                  {claim.status === 'partially_supported' && <HelpCircle className="w-3 h-3 mr-0.5" />}
                  {claim.status === 'unsupported' && <XCircle className="w-3 h-3 mr-0.5" />}
                  {claim.status === 'unverified' && <AlertTriangle className="w-3 h-3 mr-0.5" />}
                  {claim.status.replace('_', ' ')}
                </span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Methodology Expandable Panel */}
      {showDetails && (
        <div className="pt-2 border-t border-slate-800/80 text-[11px] text-slate-400 space-y-1 bg-slate-950/40 p-2.5 rounded-xl">
          <p className="text-slate-300 font-medium">Evaluation Methodology:</p>
          <p>{metrics.methodology || 'Deterministic information retrieval metrics (Precision@5, MRR) and claim-level n-gram evidence grounding.'}</p>
          {metrics.limitations && metrics.limitations.length > 0 && (
            <div className="pt-1">
              <span className="text-slate-500 text-[10px] block font-medium">Reported Limitations:</span>
              <ul className="list-disc list-inside text-[10px] text-slate-500 space-y-0.5">
                {metrics.limitations.map((lim, i) => (
                  <li key={i}>{lim}</li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
