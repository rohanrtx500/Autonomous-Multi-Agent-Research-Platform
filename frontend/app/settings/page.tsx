'use client';

import React, { useState, useEffect } from 'react';
import { Sliders, FileText, Check, Save, Trash2, Database, Info } from 'lucide-react';

export default function SettingsPage() {
  const [saved, setSaved] = useState(false);
  const [cleared, setCleared] = useState(false);

  const [researchDepth, setResearchDepth] = useState('deep');
  const [exportFormat, setExportFormat] = useState('markdown');
  const [autoSave, setAutoSave] = useState(true);
  const [citationsEnabled, setCitationsEnabled] = useState(true);

  useEffect(() => {
    try {
      const stored = localStorage.getItem('researchmind_settings');
      if (stored) {
        const parsed = JSON.parse(stored);
        if (parsed.researchDepth) setResearchDepth(parsed.researchDepth);
        if (parsed.exportFormat) setExportFormat(parsed.exportFormat);
        if (typeof parsed.autoSave === 'boolean') setAutoSave(parsed.autoSave);
        if (typeof parsed.citationsEnabled === 'boolean') setCitationsEnabled(parsed.citationsEnabled);
      }
    } catch (e) {}
  }, []);

  const handleSave = (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const settingsObj = {
        researchDepth,
        exportFormat,
        autoSave,
        citationsEnabled
      };
      localStorage.setItem('researchmind_settings', JSON.stringify(settingsObj));
      setSaved(true);
      setTimeout(() => setSaved(false), 2500);
    } catch (e) {}
  };

  const handleClearHistory = () => {
    try {
      localStorage.removeItem('researchmind_reports');
      setCleared(true);
      setTimeout(() => setCleared(false), 2500);
    } catch (e) {}
  };

  return (
    <div className="space-y-6 max-w-3xl mx-auto">
      <div className="border-b border-slate-800 pb-4">
        <h1 className="text-xl font-bold text-white">Account & Preference Settings</h1>
        <p className="text-xs text-slate-400">Customize research synthesis depth, default report formats, and local history.</p>
      </div>

      <form onSubmit={handleSave} className="bg-slate-900 rounded-2xl border border-slate-800 p-5 space-y-6 shadow-sm">
        {/* Research Defaults */}
        <div className="space-y-3.5">
          <h3 className="text-xs font-semibold text-white flex items-center space-x-2 border-b border-slate-800 pb-2">
            <Sliders className="w-4 h-4 text-indigo-400" />
            <span>Research Preferences</span>
          </h3>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-xs">
            <div>
              <label className="block text-slate-300 font-medium mb-1 text-[11px]">Default Synthesis Depth</label>
              <select
                value={researchDepth}
                onChange={(e) => setResearchDepth(e.target.value)}
                className="w-full bg-slate-800/80 border border-slate-700/80 rounded-lg px-3 py-2 text-white focus:outline-none focus:border-indigo-500 text-xs"
              >
                <option value="standard">Standard Brief (Fast 1-Pass)</option>
                <option value="deep">Deep Literature Synthesis (Recommended 2-Pass)</option>
                <option value="comprehensive">Comprehensive Multi-Source Audit (Exhaustive 3-Pass)</option>
              </select>
              <p className="text-[10px] text-slate-400 mt-1 flex items-start space-x-1">
                <Info className="w-3 h-3 text-indigo-400 shrink-0 mt-0.5" />
                <span>
                  {researchDepth === 'standard' && 'Standard mode executes a fast 1-pass brief focusing on primary takeaways.'}
                  {researchDepth === 'deep' && 'Deep mode executes a 2-pass iterative loop with full paper citations and research gaps.'}
                  {researchDepth === 'comprehensive' && 'Comprehensive mode executes an exhaustive 3-pass audit combining internal vectors and all live services.'}
                </span>
              </p>
            </div>

            <div>
              <label className="block text-slate-300 font-medium mb-1 text-[11px]">Default Export Format</label>
              <select
                value={exportFormat}
                onChange={(e) => setExportFormat(e.target.value)}
                className="w-full bg-slate-800/80 border border-slate-700/80 rounded-lg px-3 py-2 text-white focus:outline-none focus:border-indigo-500 text-xs"
              >
                <option value="markdown">Markdown (.md)</option>
                <option value="text">Plain Text (.txt)</option>
                <option value="pdf">PDF Document (.pdf)</option>
              </select>
              <p className="text-[10px] text-slate-400 mt-1">Pre-selects your preferred download format when viewing reports.</p>
            </div>
          </div>
        </div>

        {/* Feature Switches */}
        <div className="space-y-3.5">
          <h3 className="text-xs font-semibold text-white flex items-center space-x-2 border-b border-slate-800 pb-2">
            <FileText className="w-4 h-4 text-cyan-400" />
            <span>Report & Storage Options</span>
          </h3>

          <div className="space-y-3 text-xs">
            <div className="flex items-center justify-between p-3 rounded-xl bg-slate-800/40 border border-slate-800">
              <div>
                <span className="font-medium text-white text-xs block">Auto-save Generated Reports</span>
                <span className="text-slate-400 text-[11px]">Automatically store synthesized research in local workspace history</span>
              </div>
              <input
                type="checkbox"
                checked={autoSave}
                onChange={(e) => setAutoSave(e.target.checked)}
                className="w-4 h-4 rounded border-slate-700 text-indigo-600 focus:ring-indigo-500 bg-slate-800"
              />
            </div>

            <div className="flex items-center justify-between p-3 rounded-xl bg-slate-800/40 border border-slate-800">
              <div>
                <span className="font-medium text-white text-xs block">Include Verified Academic References</span>
                <span className="text-slate-400 text-[11px]">Attach verified arXiv and Semantic Scholar paper citations to generated reports</span>
              </div>
              <input
                type="checkbox"
                checked={citationsEnabled}
                onChange={(e) => setCitationsEnabled(e.target.checked)}
                className="w-4 h-4 rounded border-slate-700 text-indigo-600 focus:ring-indigo-500 bg-slate-800"
              />
            </div>
          </div>
        </div>

        {/* Workspace Data Controls */}
        <div className="space-y-3.5">
          <h3 className="text-xs font-semibold text-white flex items-center space-x-2 border-b border-slate-800 pb-2">
            <Database className="w-4 h-4 text-purple-400" />
            <span>Workspace Storage</span>
          </h3>

          <div className="flex items-center justify-between p-3 rounded-xl bg-slate-800/40 border border-slate-800 text-xs">
            <div>
              <span className="font-medium text-white text-xs block">Clear Saved Reports History</span>
              <span className="text-slate-400 text-[11px]">Remove locally saved research reports from browser storage</span>
            </div>
            <button
              type="button"
              onClick={handleClearHistory}
              className="px-3 py-1.5 rounded-lg bg-rose-500/10 hover:bg-rose-500/20 text-rose-400 border border-rose-500/30 text-xs font-medium transition-colors flex items-center space-x-1"
            >
              <Trash2 className="w-3.5 h-3.5" />
              <span>{cleared ? 'History Cleared' : 'Clear History'}</span>
            </button>
          </div>
        </div>

        <div className="pt-2 flex justify-end">
          <button
            type="submit"
            className="px-4 py-2 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white font-medium text-xs transition-all flex items-center space-x-1.5"
          >
            {saved ? <Check className="w-3.5 h-3.5 text-emerald-400" /> : <Save className="w-3.5 h-3.5" />}
            <span>{saved ? 'Preferences Saved' : 'Save Preferences'}</span>
          </button>
        </div>
      </form>
    </div>
  );
}
