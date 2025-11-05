import { axiosPrivate } from './axios';

export const notificationService = {
  // Get user notifications with pagination and filtering
  getNotifications: async (skip = 0, limit = 20, unreadOnly = false) => {
    try {
      const response = await axiosPrivate.get('/notifications/', {
        params: { skip, limit, unread_only: unreadOnly }
      });
      return response.data;
    } catch (error) {
      console.error('Error fetching notifications:', error);
      throw error;
    }
  },

  // Get notification statistics (total, unread, read counts)
  getStats: async () => {
    try {
      const response = await axiosPrivate.get('/notifications/stats');
      return response.data;
    } catch (error) {
      console.error('Error fetching notification stats:', error);
      throw error;
    }
  },

  // Get single notification by UUID
  getNotificationByUuid: async (uuid) => {
    try {
      const response = await axiosPrivate.get(`/notifications/${uuid}`);
      return response.data;
    } catch (error) {
      console.error('Error fetching notification:', error);
      throw error;
    }
  },

  // Mark single notification as read
  markAsRead: async (uuid) => {
    try {
      const response = await axiosPrivate.patch(`/notifications/${uuid}/read`);
      return response.data;
    } catch (error) {
      console.error('Error marking notification as read:', error);
      throw error;
    }
  },

  // Mark all notifications as read
  markAllAsRead: async () => {
    try {
      const response = await axiosPrivate.patch('/notifications/read-all');
      return response.data;
    } catch (error) {
      console.error('Error marking all notifications as read:', error);
      throw error;
    }
  },

  // Delete single notification
  deleteNotification: async (uuid) => {
    try {
      await axiosPrivate.delete(`/notifications/${uuid}`);
    } catch (error) {
      console.error('Error deleting notification:', error);
      throw error;
    }
  },

  // Delete all notifications
  deleteAllNotifications: async () => {
    try {
      const response = await axiosPrivate.delete('/notifications/');
      return response.data;
    } catch (error) {
      console.error('Error deleting all notifications:', error);
      throw error;
    }
  }
};
