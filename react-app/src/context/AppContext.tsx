import React, { createContext, useContext, useState, ReactNode } from 'react';

export type PersonaType = 'general' | 'developer' | 'product_manager' | 'designer';

export interface SummaryData {
  title: string;
  url: string;
  persona: PersonaType;
  summary: string;
  isLoading: boolean;
}

interface AppContextType {
  currentPage: 'home' | 'summary';
  setCurrentPage: (page: 'home' | 'summary') => void;
  confluenceUrl: string;
  setConfluenceUrl: (url: string) => void;
  selectedPersona: PersonaType | null;
  setSelectedPersona: (persona: PersonaType | null) => void;
  summaryData: SummaryData | null;
  setSummaryData: (data: SummaryData | null) => void;
  isLoading: boolean;
  setIsLoading: (loading: boolean) => void;
  error: string | null;
  setError: (error: string | null) => void;
  resetApp: () => void;
}

const AppContext = createContext<AppContextType | undefined>(undefined);

export const useApp = () => {
  const context = useContext(AppContext);
  if (context === undefined) {
    throw new Error('useApp must be used within an AppProvider');
  }
  return context;
};

interface AppProviderProps {
  children: ReactNode;
}

export const AppProvider: React.FC<AppProviderProps> = ({ children }) => {
  const [currentPage, setCurrentPage] = useState<'home' | 'summary'>('home');
  const [confluenceUrl, setConfluenceUrl] = useState('');
  const [selectedPersona, setSelectedPersona] = useState<PersonaType | null>(null);
  const [summaryData, setSummaryData] = useState<SummaryData | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const resetApp = () => {
    setCurrentPage('home');
    setConfluenceUrl('');
    setSelectedPersona(null);
    setSummaryData(null);
    setIsLoading(false);
    setError(null);
  };

  const value: AppContextType = {
    currentPage,
    setCurrentPage,
    confluenceUrl,
    setConfluenceUrl,
    selectedPersona,
    setSelectedPersona,
    summaryData,
    setSummaryData,
    isLoading,
    setIsLoading,
    error,
    setError,
    resetApp,
  };

  return <AppContext.Provider value={value}>{children}</AppContext.Provider>;
};