import { useState, useEffect, useCallback } from 'react';
import useAxiosPrivate from './useAxiosPrivate';
import { getNotifications, getNotificationStats } from '../services/notificationService';

/**
 * Hook to fetch notifications
 */
export const useGetNotifications = (skip = 0, limit = 20, unreadOnly = false) => {
  const [notifications, setNotifications] = useState([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchNotifications = useCallback(async () => {
    try {
      setLoading(true);
      const data = await getNotifications(skip, limit, unreadOnly);
      setNotifications(data.notifications || []);
      setTotal(data.total || 0);
      setError(null);
    } catch (err) {
      setError(err.response?.data?.detail || err.message);
    } finally {
      setLoading(false);
    }
  }, [skip, limit, unreadOnly]);

  useEffect(() => {
    fetchNotifications();
  }, [fetchNotifications]);

  return { notifications, total, loading, error, refetch: fetchNotifications };
};

/**
 * Hook to get notification stats (unread count, etc.)
 */
export const useNotificationStats = () => {
  const [stats, setStats] = useState({ total: 0, unread: 0, read: 0 });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchStats = useCallback(async () => {
    try {
      setLoading(true);
      const data = await getNotificationStats();
      setStats(data);
      setError(null);
    } catch (err) {
      setError(err.response?.data?.detail || err.message);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchStats();
  }, [fetchStats]);

  return { stats, unreadCount: stats.unread, loading, error, refetch: fetchStats };
};

/**
 * Hook to mark notification as read
 */
export const useMarkNotificationRead = () => {
  const axiosPrivate = useAxiosPrivate();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const markAsRead = async (uuid) => {
    try {
      setLoading(true);
      setError(null);
      const response = await axiosPrivate.patch(`/notifications/${uuid}/read`);
      return response.data;
    } catch (err) {
      setError(err.response?.data?.detail || err.message);
      throw err;
    } finally {
      setLoading(false);
    }
  };

  const markAllAsRead = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await axiosPrivate.patch('/notifications/read-all');
      return response.data;
    } catch (err) {
      setError(err.response?.data?.detail || err.message);
      throw err;
    } finally {
      setLoading(false);
    }
  };

  return { markAsRead, markAllAsRead, loading, error };
};
