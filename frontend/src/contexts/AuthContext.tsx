import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';

interface AuthContextType {
  isAuthenticated: boolean;
  userEmail: string | null;
  login: (email: string, token: string) => void;
  logout: () => void;
  token: string | null;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [userEmail, setUserEmail] = useState<string | null>(null);
  const [token, setToken] = useState<string | null>(null);

  // Vérifier si un token existe au chargement
  useEffect(() => {
    const storedToken = localStorage.getItem('auth_token');
    const storedEmail = localStorage.getItem('user_email');

    if (storedToken && storedEmail) {
      setToken(storedToken);
      setUserEmail(storedEmail);
      setIsAuthenticated(true);
    }
  }, []);

  const login = (email: string, newToken: string) => {
    localStorage.setItem('auth_token', newToken);
    localStorage.setItem('user_email', email);
    setToken(newToken);
    setUserEmail(email);
    setIsAuthenticated(true);
  };

  const logout = () => {
    localStorage.removeItem('auth_token');
    localStorage.removeItem('user_email');
    setToken(null);
    setUserEmail(null);
    setIsAuthenticated(false);
  };

  return (
    <AuthContext.Provider value={{ isAuthenticated, userEmail, login, logout, token }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}
