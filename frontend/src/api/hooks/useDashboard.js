import { useState, useEffect, useCallback } from 'react';
import { getAdminDashboard, getUserDashboard } from '../services/dashboardService';
import { useAuth } from '../AuthProvider';

/**
 * Hook for fetching admin dashboard data
 * @returns {object} { data, isLoading, error, refetch }
 */
export const useAdminDashboard = () => {
  const [data, setData] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchData = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      const result = await getAdminDashboard();
      setData(result);
    } catch (err) {
      setError(err.response?.data?.detail || err.message || 'Failed to load dashboard');
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  return { data, isLoading, error, refetch: fetchData };
};

/**
 * Hook for fetching user dashboard data
 * @returns {object} { data, isLoading, error, refetch }
 */
export const useUserDashboard = () => {
  const [data, setData] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchData = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      const result = await getUserDashboard();
      setData(result);
    } catch (err) {
      setError(err.response?.data?.detail || err.message || 'Failed to load dashboard');
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  return { data, isLoading, error, refetch: fetchData };
};

/**
 * Smart hook that returns appropriate dashboard based on user role
 * @returns {object} { data, isLoading, error, refetch, isAdmin }
 */
export const useDashboard = () => {
  const { user } = useAuth();
  const isAdmin = user?.role === 'admin' || user?.role === 'moderator';
  
  const [data, setData] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchData = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      const result = isAdmin 
        ? await getAdminDashboard() 
        : await getUserDashboard();
      setData(result);
    } catch (err) {
      setError(err.response?.data?.detail || err.message || 'Failed to load dashboard');
    } finally {
      setIsLoading(false);
    }
  }, [isAdmin]);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  return { data, isLoading, error, refetch: fetchData, isAdmin };
};
