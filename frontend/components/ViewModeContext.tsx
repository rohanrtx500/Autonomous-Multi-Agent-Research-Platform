'use client';

import React, { createContext, useContext, useState, useEffect } from 'react';

type ViewMode = 'standard' | 'developer';

interface ViewModeContextType {
  viewMode: ViewMode;
  setViewMode: (mode: ViewMode) => void;
}

const ViewModeContext = createContext<ViewModeContextType>({
  viewMode: 'standard',
  setViewMode: () => {},
});

export function ViewModeProvider({ children }: { children: React.ReactNode }) {
  const [viewMode, setViewModeState] = useState<ViewMode>('standard');

  useEffect(() => {
    try {
      const saved = localStorage.getItem('researchmind_view_mode') as ViewMode;
      if (saved === 'standard' || saved === 'developer') {
        setViewModeState(saved);
      }
    } catch (e) {}
  }, []);

  const setViewMode = (mode: ViewMode) => {
    setViewModeState(mode);
    try {
      localStorage.setItem('researchmind_view_mode', mode);
    } catch (e) {}
  };

  return (
    <ViewModeContext.Provider value={{ viewMode, setViewMode }}>
      {children}
    </ViewModeContext.Provider>
  );
}

export function useViewMode() {
  return useContext(ViewModeContext);
}
