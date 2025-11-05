import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';
import { notificationService } from '@/api/notificationService';
import { toast } from 'react-toastify';
import useAuth from '@/api/useAuth';

const NotificationContext = createContext();

export const NotificationProvider = ({ children }) => {
  const { isAuthenticated } = useAuth();
  const [notifications, setNotifications] = useState([]);
  const [unreadCount, setUnreadCount] = useState(0);
  const [loading, setLoading] = useState(false);
  const [stats, setStats] = useState({ total: 0, unread: 0, read: 0 });

  // Fetch notifications
  const fetchNotifications = useCallback(async (unreadOnly = false) => {
    try {
      setLoading(true);
      const data = await notificationService.getNotifications(0, 20, unreadOnly);
      setNotifications(data);
    } catch (error) {
      console.error('Failed to load notifications:', error);
      // Only show error if user is authenticated
      if (error.response?.status !== 401) {
        toast.error('Failed to load notifications');
      }
    } finally {
      setLoading(false);
    }
  }, []);

  // Fetch notification stats (unread count)
  const fetchStats = useCallback(async () => {
    try {
      const statsData = await notificationService.getStats();
      setStats(statsData);
      setUnreadCount(statsData.unread);
    } catch (error) {
      // Silently fail for stats to avoid annoying users
      console.error('Failed to fetch notification stats:', error);
    }
  }, []);

  // Mark as read
  const markAsRead = useCallback(async (uuid) => {
    try {
      await notificationService.markAsRead(uuid);
      setNotifications(prev => 
        prev.map(n => n.uuid === uuid ? { ...n, is_read: true } : n)
      );
      setUnreadCount(prev => Math.max(0, prev - 1));
      setStats(prev => ({
        ...prev,
        unread: Math.max(0, prev.unread - 1),
        read: prev.read + 1
      }));
    } catch (error) {
      toast.error('Failed to mark notification as read');
    }
  }, []);

  // Mark all as read
  const markAllAsRead = useCallback(async () => {
    try {
      const response = await notificationService.markAllAsRead();
      setNotifications(prev => prev.map(n => ({ ...n, is_read: true })));
      setUnreadCount(0);
      setStats(prev => ({
        total: prev.total,
        unread: 0,
        read: prev.total
      }));
      toast.success(response.message || 'All notifications marked as read');
    } catch (error) {
      toast.error('Failed to mark all as read');
    }
  }, []);

  // Delete notification
  const deleteNotification = useCallback(async (uuid) => {
    try {
      await notificationService.deleteNotification(uuid);
      
      // Update local state
      const notification = notifications.find(n => n.uuid === uuid);
      setNotifications(prev => prev.filter(n => n.uuid !== uuid));
      
      // Update counts
      if (notification && !notification.is_read) {
        setUnreadCount(prev => Math.max(0, prev - 1));
      }
      
      // Refresh stats from server
      fetchStats();
      toast.success('Notification deleted');
    } catch (error) {
      toast.error('Failed to delete notification');
    }
  }, [notifications, fetchStats]);

  // Delete all notifications
  const deleteAllNotifications = useCallback(async () => {
    try {
      const response = await notificationService.deleteAllNotifications();
      setNotifications([]);
      setUnreadCount(0);
      setStats({ total: 0, unread: 0, read: 0 });
      toast.success(response.message || 'All notifications deleted');
    } catch (error) {
      toast.error('Failed to delete all notifications');
    }
  }, []);

  // Polling for new notifications (every 30 seconds)
  useEffect(() => {
    if (!isAuthenticated) {
      return;
    }

    // Initial fetch
    fetchStats();
    fetchNotifications();
    
    // Set up polling interval
    const interval = setInterval(() => {
      fetchStats();
    }, 30000); // Poll every 30 seconds

    return () => clearInterval(interval);
  }, [isAuthenticated, fetchStats, fetchNotifications]);

  return (
    <NotificationContext.Provider value={{
      notifications,
      unreadCount,
      loading,
      stats,
      fetchNotifications,
      fetchStats,
      markAsRead,
      markAllAsRead,
      deleteNotification,
      deleteAllNotifications
    }}>
      {children}
    </NotificationContext.Provider>
  );
};

export const useNotifications = () => {
  const context = useContext(NotificationContext);
  if (!context) {
    throw new Error('useNotifications must be used within NotificationProvider');
  }
  return context;
};
