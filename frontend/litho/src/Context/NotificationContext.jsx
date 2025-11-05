import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';
import { notificationService } from '../api/notificationService';

const NotificationContext = createContext();

export const NotificationProvider = ({ children }) => {
  const [notifications, setNotifications] = useState([]);
  const [unreadCount, setUnreadCount] = useState(0);
  const [loading, setLoading] = useState(false);

  const fetchNotifications = useCallback(async () => {
    try {
      setLoading(true);
      const data = await notificationService.getNotifications(0, 20, false);
      setNotifications(data);
    } catch (error) {
      console.error('Failed to load notifications:', error);
    } finally {
      setLoading(false);
    }
  }, []);

  const fetchStats = useCallback(async () => {
    try {
      const stats = await notificationService.getStats();
      setUnreadCount(stats.unread);
    } catch (error) {
      console.error('Failed to fetch notification stats:', error);
    }
  }, []);

  const markAsRead = useCallback(async (uuid) => {
    try {
      await notificationService.markAsRead(uuid);
      setNotifications(prev => 
        prev.map(n => n.uuid === uuid ? { ...n, is_read: true } : n)
      );
      setUnreadCount(prev => Math.max(0, prev - 1));
    } catch (error) {
      console.error('Failed to mark notification as read:', error);
    }
  }, []);

  const markAllAsRead = useCallback(async () => {
    try {
      await notificationService.markAllAsRead();
      setNotifications(prev => prev.map(n => ({ ...n, is_read: true })));
      setUnreadCount(0);
    } catch (error) {
      console.error('Failed to mark all as read:', error);
    }
  }, []);

  const deleteNotification = useCallback(async (uuid) => {
    try {
      await notificationService.deleteNotification(uuid);
      const notification = notifications.find(n => n.uuid === uuid);
      setNotifications(prev => prev.filter(n => n.uuid !== uuid));
      if (notification && !notification.is_read) {
        setUnreadCount(prev => Math.max(0, prev - 1));
      }
      fetchStats(); // Refresh stats
    } catch (error) {
      console.error('Failed to delete notification:', error);
    }
  }, [notifications, fetchStats]);

  // Poll for new notifications every 30 seconds
  useEffect(() => {
    fetchStats();
    fetchNotifications();
    
    const interval = setInterval(() => {
      fetchStats();
    }, 30000);

    return () => clearInterval(interval);
  }, [fetchStats, fetchNotifications]);

  return (
    <NotificationContext.Provider value={{
      notifications,
      unreadCount,
      loading,
      fetchNotifications,
      markAsRead,
      markAllAsRead,
      deleteNotification
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
