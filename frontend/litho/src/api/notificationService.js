import { axiosPrivate } from './axios';

export const notificationService = {
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

  getStats: async () => {
    try {
      const response = await axiosPrivate.get('/notifications/stats');
      return response.data;
    } catch (error) {
      console.error('Error fetching notification stats:', error);
      throw error;
    }
  },

  markAsRead: async (uuid) => {
    try {
      const response = await axiosPrivate.patch(`/notifications/${uuid}/read`);
      return response.data;
    } catch (error) {
      console.error('Error marking notification as read:', error);
      throw error;
    }
  },

  markAllAsRead: async () => {
    try {
      const response = await axiosPrivate.patch('/notifications/read-all');
      return response.data;
    } catch (error) {
      console.error('Error marking all notifications as read:', error);
      throw error;
    }
  },

  deleteNotification: async (uuid) => {
    try {
      await axiosPrivate.delete(`/notifications/${uuid}`);
    } catch (error) {
      console.error('Error deleting notification:', error);
      throw error;
    }
  }
};
