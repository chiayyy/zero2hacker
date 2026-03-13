import React, { createContext, useContext, useEffect, useState, ReactNode } from 'react';

interface ThemeContextType {
  darkMode: boolean;
  toggleDarkMode: () => void;
  primaryColor: string;
  setPrimaryColor: (color: string) => void;
}

const ThemeContext = createContext<ThemeContextType | undefined>(undefined);

export const useTheme = (): ThemeContextType => {
  const context = useContext(ThemeContext);
  if (!context) {
    throw new Error('useTheme must be used within a ThemeProvider');
  }
  return context;
};

interface ThemeProviderProps {
  children: ReactNode;
}

export const ThemeProvider: React.FC<ThemeProviderProps> = ({ children }) => {
  const [darkMode, setDarkMode] = useState(() => {
    // Check localStorage first, then system preference
    const saved = localStorage.getItem('darkMode');
    if (saved !== null) {
      return JSON.parse(saved);
    }
    return window.matchMedia('(prefers-color-scheme: dark)').matches;
  });

  const [primaryColor, setPrimaryColorState] = useState(() => {
    return localStorage.getItem('primaryColor') || '#3b82f6';
  });

  useEffect(() => {
    localStorage.setItem('darkMode', JSON.stringify(darkMode));

    // Update document class
    if (darkMode) {
      document.documentElement.classList.add('dark');
    } else {
      document.documentElement.classList.remove('dark');
    }
  }, [darkMode]);

  useEffect(() => {
    localStorage.setItem('primaryColor', primaryColor);

    // Update CSS custom property
    document.documentElement.style.setProperty('--primary-color', primaryColor);
  }, [primaryColor]);

  const toggleDarkMode = () => {
    setDarkMode((prev: boolean) => !prev);
  };

  const setPrimaryColor = (color: string) => {
    setPrimaryColorState(color);
  };

  const value: ThemeContextType = {
    darkMode,
    toggleDarkMode,
    primaryColor,
    setPrimaryColor
  };

  return (
    <ThemeContext.Provider value={value}>
      {children}
    </ThemeContext.Provider>
  );
};