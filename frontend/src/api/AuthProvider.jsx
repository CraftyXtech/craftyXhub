import React, { createContext, useState, useEffect, useContext, useCallback } from 'react';
import { isTokenExpired, getStoredToken, getStoredUser, storeAuthData, clearAuthData } from './utils/token';

/**
 * Authentication Context
 */
const AuthContext = createContext({
  auth: null,
  isAuthenticated: false,
  loading: true,
  login: () => {},
  logout: () => {},
  updateUser: () => {},
});

/**
 * Hook to access auth context
 * @returns {object} Auth context value
 */
export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

/**
 * Authentication Provider Component
 * Manages authentication state and provides login/logout functions
 */
export const AuthProvider = ({ children }) => {
  const [auth, setAuth] = useState(null);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [loading, setLoading] = useState(true);

  // Check for existing auth on mount
  useEffect(() => {
    const token = getStoredToken();
    const user = getStoredUser();

    if (token && !isTokenExpired(token) && user) {
      setAuth({ accessToken: token, user });
      setIsAuthenticated(true);
    } else {
      // Clear invalid/expired auth data
      clearAuthData();
      setAuth(null);
      setIsAuthenticated(false);
    }
    
    setLoading(false);
  }, []);

  /**
   * Login - store token and user, update state
   */
  const login = useCallback((token, user) => {
    storeAuthData(token, user);
    setAuth({ accessToken: token, user });
    setIsAuthenticated(true);
  }, []);

  /**
   * Logout - clear storage and state
   */
  const logout = useCallback(() => {
    clearAuthData();
    setAuth(null);
    setIsAuthenticated(false);
  }, []);

  /**
   * Update user data without changing token
   */
  const updateUser = useCallback((user) => {
    if (auth?.accessToken) {
      storeAuthData(auth.accessToken, user);
      setAuth(prev => ({ ...prev, user }));
    }
  }, [auth?.accessToken]);

  const value = {
    auth,
    isAuthenticated,
    loading,
    login,
    logout,
    updateUser,
    // Convenience accessors
    user: auth?.user || null,
    token: auth?.accessToken || null,
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};

export default AuthContext;
