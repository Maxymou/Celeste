import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';

interface AuthContextType {
  isAuthenticated: boolean;
  userEmail: string | null;
  login: (email: string, token: string) => void;
  logout: () => void;
  token: string | null;
  isLoading: boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [userEmail, setUserEmail] = useState<string | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  // Vérifier la validité du token au chargement
  useEffect(() => {
    const verifyToken = async () => {
      const storedToken = localStorage.getItem('auth_token');
      const storedEmail = localStorage.getItem('user_email');

      if (!storedToken || !storedEmail) {
        setIsLoading(false);
        return;
      }

      try {
        // Vérifier la validité du token auprès du serveur
        const response = await fetch('/api/auth/verify', {
          method: 'GET',
          headers: {
            'Authorization': `Bearer ${storedToken}`,
            'Content-Type': 'application/json'
          }
        });

        if (response.ok) {
          // Token valide, restaurer la session
          setToken(storedToken);
          setUserEmail(storedEmail);
          setIsAuthenticated(true);
        } else {
          // Token invalide ou expiré, nettoyer le localStorage
          localStorage.removeItem('auth_token');
          localStorage.removeItem('user_email');
        }
      } catch (error) {
        // En cas d'erreur réseau, nettoyer également
        console.error('Erreur de vérification du token:', error);
        localStorage.removeItem('auth_token');
        localStorage.removeItem('user_email');
      } finally {
        setIsLoading(false);
      }
    };

    verifyToken();
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
    <AuthContext.Provider value={{ isAuthenticated, userEmail, login, logout, token, isLoading }}>
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
