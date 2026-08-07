'use client';

import React, { useState, useEffect } from 'react';
import Link from 'next/link';
import { Sparkles, FileText, Database } from 'lucide-react';
import { fetchHealth } from '@/lib/api';

export default function Navbar() {
  const [isHealthy, setIsHealthy] = useState<boolean>(true);

  useEffect(() => {
    fetchHealth().then((status) => setIsHealthy(status));
    const interval = setInterval(() => {
      fetchHealth().then((status) => setIsHealthy(status));
    }, 15000);
    return () => clearInterval(interval);
  }, []);

  return (
    <header className="h-14 border-b border-slate-800 bg-slate-900/90 backdrop-blur-md px-6 flex items-center justify-between sticky top-0 z-50">
      <div className="flex items-center space-x-3">
        <Link href="/" className="flex items-center space-x-2.5">
          <div className="w-8 h-8 rounded-lg bg-indigo-600/15 border border-indigo-500/30 flex items-center justify-center text-indigo-400">
            <Sparkles className="w-4 h-4" />
          </div>
          <div className="flex items-baseline space-x-2">
            <span className="font-bold text-base text-white tracking-tight">ResearchMind</span>
            <span className="text-[11px] font-medium text-slate-400 font-mono">v1.0</span>
          </div>
        </Link>
      </div>

      <div className="flex items-center space-x-4">
        <div className="flex items-center space-x-2 bg-slate-800/60 px-3 py-1 rounded-full border border-slate-700/60 text-xs">
          <span className={`w-2 h-2 rounded-full ${isHealthy ? 'bg-emerald-400' : 'bg-rose-500'}`}></span>
          <span className="text-slate-300 font-medium text-[11px]">{isHealthy ? 'Service Operational' : 'Service Offline'}</span>
        </div>

        <Link
          href="/reports"
          className="text-slate-400 hover:text-white transition-colors flex items-center space-x-1.5 text-xs font-medium px-2.5 py-1 rounded-lg hover:bg-slate-800/50"
        >
          <FileText className="w-3.5 h-3.5" />
          <span>Saved Reports</span>
        </Link>
      </div>
    </header>
  );
}
