'use client';

import React from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { Search, Database, FileText, Settings, BookOpen } from 'lucide-react';

const userNavItems = [
  { label: 'Workspace', href: '/', icon: Search },
  { label: 'Knowledge Base', href: '/knowledge', icon: Database },
  { label: 'Saved Reports', href: '/reports', icon: FileText },
  { label: 'Settings', href: '/settings', icon: Settings },
];

export default function Sidebar() {
  const pathname = usePathname();

  return (
    <aside className="w-60 bg-slate-900 border-r border-slate-800 flex flex-col justify-between p-3.5 shrink-0">
      <div className="space-y-4">
        <div className="px-2.5 pt-1 text-[11px] font-semibold text-slate-500 uppercase tracking-wider">
          Navigation
        </div>
        <nav className="space-y-0.5">
          {userNavItems.map((item) => {
            const Icon = item.icon;
            const isActive = pathname === item.href;
            return (
              <Link
                key={item.href}
                href={item.href}
                className={`flex items-center space-x-2.5 px-2.5 py-2 rounded-lg text-xs font-medium transition-all ${
                  isActive
                    ? 'bg-indigo-600/15 text-indigo-400 border border-indigo-500/25'
                    : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/40'
                }`}
              >
                <Icon className={`w-4 h-4 ${isActive ? 'text-indigo-400' : 'text-slate-400'}`} />
                <span>{item.label}</span>
              </Link>
            );
          })}
        </nav>
      </div>

      <div className="p-3 bg-slate-800/40 rounded-xl border border-slate-800 text-xs space-y-1.5">
        <div className="flex items-center space-x-2 text-slate-300 font-medium">
          <BookOpen className="w-3.5 h-3.5 text-indigo-400" />
          <span>Research Engine</span>
        </div>
        <p className="text-slate-400 text-[11px] leading-snug">
          Synthesizes multi-source literature with verified citation grounding.
        </p>
      </div>
    </aside>
  );
}
