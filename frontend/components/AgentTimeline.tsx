'use client';

import React from 'react';
import { AgentExecutionLog } from '@/lib/types';
import { CheckCircle2, Activity, Bot, Search, BookOpen, Layers, ShieldCheck } from 'lucide-react';

interface AgentTimelineProps {
  logs: AgentExecutionLog[];
  currentStatus: string;
}

export default function AgentTimeline({ logs, currentStatus }: AgentTimelineProps) {
  const getHumanTitle = (agentName: string) => {
    switch (agentName) {
      case 'Planner Agent':
        return 'Planning Research Strategy';
      case 'Paper Retrieval Agent':
        return 'Gathering Academic Literature';
      case 'Web Research Agent':
        return 'Analyzing Web & Technical Articles';
      case 'GitHub Research Agent':
        return 'Searching Code Repositories';
      case 'Document Retrieval Agent':
        return 'Searching Knowledge Repository';
      case 'Knowledge Synthesizer':
        return 'Synthesizing Evidence & Findings';
      case 'Comparison Agent':
        return 'Evaluating Methodology Tradeoffs';
      case 'Research Gap Analyzer':
        return 'Identifying Unresolved Research Gaps';
      case 'Experiment Planner':
        return 'Designing Empirical Benchmarks';
      case 'Writer Agent':
        return 'Formatting Verified Report';
      case 'Critic Agent':
        return 'Conducting Quality Review';
      case 'Citation Verification Agent':
        return 'Verifying Source Attribution';
      case 'Evaluation Agent':
        return 'Computing Accuracy Scores';
      default:
        return agentName;
    }
  };

  return (
    <div className="bg-slate-900 rounded-2xl border border-slate-800 p-4 space-y-3.5 shadow-sm">
      <div className="flex items-center justify-between border-b border-slate-800 pb-3">
        <div className="flex items-center space-x-2">
          <Activity className="w-4 h-4 text-indigo-400" />
          <h3 className="font-semibold text-white text-xs">Research Progress</h3>
        </div>
        <span className="text-[11px] px-2 py-0.5 rounded-full bg-indigo-600/10 text-indigo-400 border border-indigo-500/20 font-mono">
          {currentStatus === 'idle' ? 'Ready' : currentStatus === 'completed' ? 'Finished' : 'Analyzing'}
        </span>
      </div>

      {logs.length === 0 ? (
        <div className="py-10 text-center text-slate-500 text-xs space-y-2">
          <Bot className="w-6 h-6 mx-auto text-slate-600" />
          <p>Submit a topic above to launch research analysis.</p>
        </div>
      ) : (
        <div className="space-y-2.5 max-h-[420px] overflow-y-auto pr-1 custom-scrollbar">
          {logs.map((log, index) => {
            const title = getHumanTitle(log.agent_name);

            return (
              <div
                key={index}
                className="p-3 rounded-xl bg-slate-800/40 border border-slate-800 flex items-start space-x-2.5 text-xs transition-colors hover:bg-slate-800/70"
              >
                <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400 shrink-0 mt-0.5" />
                <div className="flex-1 space-y-0.5">
                  <span className="font-medium text-slate-200 block">{title}</span>
                  <p className="text-[11px] text-slate-400 leading-relaxed">{log.decision_reasoning}</p>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
