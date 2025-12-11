import React, { createContext, useContext, useState, useCallback, useEffect, ReactNode } from 'react';

type Direction = 'rtl' | 'ltr';
type Theme = 'light' | 'dark';

interface ThemeContextType {
  direction: Direction;
  theme: Theme;
  setDirection: (dir: Direction) => void;
  setTheme: (theme: Theme) => void;
  toggleDirection: () => void;
  toggleTheme: () => void;
}

const ThemeContext = createContext<ThemeContextType | undefined>(undefined);

interface ThemeProviderProps {
  children: ReactNode;
  defaultDirection?: Direction;
  defaultTheme?: Theme;
}

export const ThemeProvider: React.FC<ThemeProviderProps> = ({
  children,
  defaultDirection = 'rtl',
  defaultTheme = 'light',
}) => {
  const [direction, setDirectionState] = useState<Direction>(defaultDirection);
  const [theme, setThemeState] = useState<Theme>(defaultTheme);

  // Update document direction when it changes
  useEffect(() => {
    document.documentElement.dir = direction;
    document.documentElement.lang = direction === 'rtl' ? 'ar' : 'en';
  }, [direction]);

  // Update document theme class when it changes
  useEffect(() => {
    if (theme === 'dark') {
      document.documentElement.classList.add('dark');
    } else {
      document.documentElement.classList.remove('dark');
    }
  }, [theme]);

  const setDirection = useCallback((dir: Direction) => {
    setDirectionState(dir);
  }, []);

  const setTheme = useCallback((newTheme: Theme) => {
    setThemeState(newTheme);
  }, []);

  const toggleDirection = useCallback(() => {
    setDirectionState((prev) => (prev === 'rtl' ? 'ltr' : 'rtl'));
  }, []);

  const toggleTheme = useCallback(() => {
    setThemeState((prev) => (prev === 'light' ? 'dark' : 'light'));
  }, []);

  const value: ThemeContextType = {
    direction,
    theme,
    setDirection,
    setTheme,
    toggleDirection,
    toggleTheme,
  };

  return (
    <ThemeContext.Provider value={value}>
      {children}
    </ThemeContext.Provider>
  );
};

export const useTheme = (): ThemeContextType => {
  const context = useContext(ThemeContext);
  if (context === undefined) {
    throw new Error('useTheme must be used within a ThemeProvider');
  }
  return context;
};

export default ThemeContext;
