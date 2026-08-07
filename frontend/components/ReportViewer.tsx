'use client';

import React, { useState, useRef, useEffect } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { FileText, Download, Copy, Check, ChevronDown, FileCode, FileType, FileCheck } from 'lucide-react';

interface ReportViewerProps {
  markdown?: string;
  title?: string;
}

export default function ReportViewer({ markdown, title }: ReportViewerProps) {
  const [copied, setCopied] = useState(false);
  const [showDropdown, setShowDropdown] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setShowDropdown(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  if (!markdown) {
    return (
      <div className="bg-slate-900 rounded-2xl border border-slate-800 p-8 text-center space-y-2">
        <div className="w-10 h-10 rounded-xl bg-slate-800/60 flex items-center justify-center mx-auto text-slate-500">
          <FileText className="w-5 h-5" />
        </div>
        <p className="text-xs text-slate-400">No report generated yet. Submit a query to generate a research summary.</p>
      </div>
    );
  }

  const reportTitle = title || 'Research Report';
  const fileBasename = reportTitle.toLowerCase().replace(/[^a-z0-9]+/g, '_');

  const handleCopy = () => {
    navigator.clipboard.writeText(markdown);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const downloadMarkdown = () => {
    const blob = new Blob([markdown], { type: 'text/markdown;charset=utf-8' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${fileBasename}.md`;
    a.click();
    URL.revokeObjectURL(url);
    setShowDropdown(false);
  };

  const downloadPlainText = () => {
    // Strip markdown formatting for clean plain text export
    const plainText = markdown
      .replace(/^#+\s+/gm, '')
      .replace(/\*\*(.*?)\*\*/g, '$1')
      .replace(/\*(.*?)\*/g, '$1')
      .replace(/`{1,3}(.*?)`{1,3}/g, '$1')
      .replace(/\[(.*?)\]\((.*?)\)/g, '$1 ($2)');

    const blob = new Blob([plainText], { type: 'text/plain;charset=utf-8' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${fileBasename}.txt`;
    a.click();
    URL.revokeObjectURL(url);
    setShowDropdown(false);
  };

  const downloadPDF = () => {
    setShowDropdown(false);

    // Create printable window with publication CSS for PDF export
    const printWindow = window.open('', '_blank');
    if (!printWindow) return;

    // Convert Markdown into simple HTML format for print window
    const printContent = `
      <!DOCTYPE html>
      <html>
        <head>
          <title>${reportTitle}</title>
          <style>
            body {
              font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
              color: #1e293b;
              line-height: 1.6;
              padding: 40px;
              max-width: 800px;
              margin: 0 auto;
            }
            h1 { font-size: 24px; color: #0f172a; border-bottom: 2px solid #e2e8f0; padding-bottom: 8px; margin-bottom: 20px; }
            h2 { font-size: 18px; color: #4338ca; margin-top: 24px; margin-bottom: 12px; }
            h3 { font-size: 14px; color: #6d28d9; margin-top: 18px; margin-bottom: 8px; }
            p { font-size: 13px; color: #334155; margin-bottom: 12px; }
            ul, ol { font-size: 13px; color: #334155; margin-bottom: 12px; padding-left: 24px; }
            li { margin-bottom: 4px; }
            blockquote { background: #f8fafc; border-left: 4px solid #6366f1; padding: 12px 16px; margin: 16px 0; font-style: italic; font-size: 13px; }
            table { width: 100%; border-collapse: collapse; margin: 16px 0; font-size: 12px; }
            th { background: #f1f5f9; text-align: left; padding: 8px; border: 1px solid #cbd5e1; font-weight: 600; }
            td { padding: 8px; border: 1px solid #cbd5e1; }
            code { font-family: monospace; background: #f1f5f9; padding: 2px 6px; border-radius: 4px; font-size: 11px; }
            a { color: #4338ca; text-decoration: none; }
            .header-badge { font-size: 11px; color: #64748b; margin-bottom: 30px; text-transform: uppercase; letter-spacing: 0.5px; }
            @media print {
              body { padding: 20px; }
            }
          </style>
        </head>
        <body>
          <div class="header-badge">ResearchMind AI • Verified Research Report</div>
          <div id="content"></div>
          <script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
          <script>
            document.getElementById('content').innerHTML = marked.parse(${JSON.stringify(markdown)});
            setTimeout(() => {
              window.print();
            }, 300);
          </script>
        </body>
      </html>
    `;

    printWindow.document.write(printContent);
    printWindow.document.close();
  };

  return (
    <div className="bg-slate-900 rounded-2xl border border-slate-800 p-5 space-y-5 shadow-sm">
      <div className="flex items-center justify-between border-b border-slate-800 pb-3">
        <div className="flex items-center space-x-2.5">
          <div className="w-8 h-8 rounded-lg bg-indigo-600/15 border border-indigo-500/25 flex items-center justify-center text-indigo-400">
            <FileText className="w-4 h-4" />
          </div>
          <div>
            <h2 className="font-bold text-white text-sm">{reportTitle}</h2>
            <p className="text-[11px] text-slate-400">Synthesized with source attribution & citation verification</p>
          </div>
        </div>

        <div className="flex items-center space-x-2">
          {/* Copy Button */}
          <button
            onClick={handleCopy}
            className="flex items-center space-x-1 px-2.5 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700/80 text-xs font-medium text-slate-300 transition-colors border border-slate-700/60"
          >
            {copied ? <Check className="w-3.5 h-3.5 text-emerald-400" /> : <Copy className="w-3.5 h-3.5" />}
            <span>{copied ? 'Copied' : 'Copy'}</span>
          </button>

          {/* Multi-Format Download Dropdown */}
          <div className="relative" ref={dropdownRef}>
            <button
              onClick={() => setShowDropdown(!showDropdown)}
              className="flex items-center space-x-1.5 px-3 py-1.5 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-xs font-medium text-white transition-all shadow-sm"
            >
              <Download className="w-3.5 h-3.5" />
              <span>Download</span>
              <ChevronDown className="w-3 h-3 text-indigo-200 ml-0.5" />
            </button>

            {showDropdown && (
              <div className="absolute right-0 mt-1.5 w-48 bg-slate-800 border border-slate-700 rounded-xl shadow-xl z-50 py-1 space-y-0.5">
                <button
                  onClick={downloadPDF}
                  className="w-full text-left px-3 py-2 text-xs text-slate-200 hover:bg-indigo-600/20 hover:text-indigo-300 flex items-center space-x-2 transition-colors"
                >
                  <FileCheck className="w-3.5 h-3.5 text-rose-400" />
                  <span>Download as PDF (.pdf)</span>
                </button>
                <button
                  onClick={downloadPlainText}
                  className="w-full text-left px-3 py-2 text-xs text-slate-200 hover:bg-indigo-600/20 hover:text-indigo-300 flex items-center space-x-2 transition-colors"
                >
                  <FileType className="w-3.5 h-3.5 text-cyan-400" />
                  <span>Download Text (.txt)</span>
                </button>
                <button
                  onClick={downloadMarkdown}
                  className="w-full text-left px-3 py-2 text-xs text-slate-200 hover:bg-indigo-600/20 hover:text-indigo-300 flex items-center space-x-2 transition-colors"
                >
                  <FileCode className="w-3.5 h-3.5 text-purple-400" />
                  <span>Download Markdown (.md)</span>
                </button>
              </div>
            )}
          </div>
        </div>
      </div>

      <div className="space-y-3.5">
        <ReactMarkdown
          remarkPlugins={[remarkGfm]}
          components={{
            h1: ({ node, ...props }) => <h1 className="text-lg font-bold text-white border-b border-slate-800 pb-2 mt-5 mb-3" {...props} />,
            h2: ({ node, ...props }) => <h2 className="text-sm font-semibold text-indigo-400 mt-5 mb-2 flex items-center space-x-2" {...props} />,
            h3: ({ node, ...props }) => <h3 className="text-xs font-semibold text-purple-400 mt-3 mb-1.5" {...props} />,
            p: ({ node, ...props }) => <p className="text-xs text-slate-300 leading-relaxed my-1.5" {...props} />,
            ul: ({ node, ...props }) => <ul className="list-disc list-inside space-y-1 text-xs text-slate-300 my-1.5" {...props} />,
            ol: ({ node, ...props }) => <ol className="list-decimal list-inside space-y-1 text-xs text-slate-300 my-1.5" {...props} />,
            li: ({ node, ...props }) => <li className="text-xs text-slate-300" {...props} />,
            blockquote: ({ node, ...props }) => (
              <blockquote className="p-3 my-2.5 rounded-xl bg-indigo-950/40 border-l-3 border-indigo-500 text-slate-300 text-xs italic" {...props} />
            ),
            table: ({ node, ...props }) => (
              <div className="overflow-x-auto my-3 rounded-xl border border-slate-800 bg-slate-950/40">
                <table className="w-full text-left text-xs border-collapse" {...props} />
              </div>
            ),
            thead: ({ node, ...props }) => <thead className="bg-slate-800/60 text-slate-200 font-semibold border-b border-slate-800" {...props} />,
            th: ({ node, ...props }) => <th className="p-2.5 border-r border-slate-800 last:border-r-0" {...props} />,
            td: ({ node, ...props }) => <td className="p-2.5 border-t border-r border-slate-800/60 last:border-r-0 text-slate-300" {...props} />,
            code: ({ node, inline, ...props }: any) => (
              inline ? (
                <code className="px-1 py-0.5 rounded bg-slate-800 font-mono text-cyan-400 text-[11px] border border-slate-700/60" {...props} />
              ) : (
                <code className="block p-3 rounded-xl bg-slate-950/80 font-mono text-xs text-slate-200 overflow-x-auto border border-slate-800 my-2.5" {...props} />
              )
            ),
            a: ({ node, ...props }) => (
              <a className="text-indigo-400 hover:underline font-medium" target="_blank" rel="noopener noreferrer" {...props} />
            )
          }}
        >
          {markdown}
        </ReactMarkdown>
      </div>
    </div>
  );
}
