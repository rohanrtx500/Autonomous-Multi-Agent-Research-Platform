import type { Metadata } from 'next';
import './globals.css';
import Navbar from '@/components/Navbar';
import Sidebar from '@/components/Sidebar';
import { ViewModeProvider } from '@/components/ViewModeContext';

export const metadata: Metadata = {
  title: 'ResearchMind AI - Autonomous Research Assistant',
  description: 'Autonomous multi-agent research platform for scientific, economic, and technical synthesis.',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="dark">
      <body className="bg-slate-950 text-slate-100 min-h-screen flex flex-col antialiased selection:bg-indigo-600 selection:text-white">
        <ViewModeProvider>
          <Navbar />
          <div className="flex-1 flex overflow-hidden">
            <Sidebar />
            <main className="flex-1 overflow-y-auto p-6 space-y-6">
              {children}
            </main>
          </div>
        </ViewModeProvider>
      </body>
    </html>
  );
}
