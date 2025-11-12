import React, { createContext, useContext, useState, ReactNode } from 'react';

/**
 * View types for user personas
 * - provider: Healthcare professionals (objective, clinical responses)
 * - patient: Parents/caregivers (empathetic, plain language responses)
 */
export type ViewType = 'provider' | 'patient';

interface ViewContextType {
  selectedView: ViewType | null;
  setSelectedView: (view: ViewType) => void;
}

const ViewContext = createContext<ViewContextType | undefined>(undefined);

interface ViewProviderProps {
  children: ReactNode;
}

/**
 * ViewProvider manages the user's selected view (provider vs patient)
 *
 * The view selection determines which system prompt is used by the LLM
 * to tailor responses. Selection persists only during the current session
 * (no localStorage persistence).
 */
export const ViewProvider: React.FC<ViewProviderProps> = ({ children }) => {
  const [selectedView, setSelectedView] = useState<ViewType | null>(null);

  return (
    <ViewContext.Provider value={{ selectedView, setSelectedView }}>
      {children}
    </ViewContext.Provider>
  );
};

/**
 * Hook to access view context
 *
 * @throws Error if used outside ViewProvider
 */
// eslint-disable-next-line react-refresh/only-export-components
export const useView = (): ViewContextType => {
  const context = useContext(ViewContext);
  if (context === undefined) {
    throw new Error('useView must be used within a ViewProvider');
  }
  return context;
};
