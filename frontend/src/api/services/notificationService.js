import { axiosPrivate } from '../axios';

/**
 * Notification Service
 * Handles notification operations
 */

/**
 * Get user notifications
 * @param {number} skip - Offset for pagination
 * @param {number} limit - Number of items
 * @param {boolean} unreadOnly - Filter only unread
 * @returns {Promise<object>} Notifications list
 */
export const getNotifications = async (skip = 0, limit = 20, unreadOnly = false) => {
  const response = await axiosPrivate.get('/notifications/', {
    params: { skip, limit, unread_only: unreadOnly },
  });
  return response.data;
};

/**
 * Get notification statistics
 * @returns {Promise<object>} { total, unread, read }
 */
export const getNotificationStats = async () => {
  const response = await axiosPrivate.get('/notifications/stats');
  return response.data;
};

/**
 * Get a single notification
 * @param {string} uuid - Notification UUID
 * @returns {Promise<object>} Notification data
 */
export const getNotificationByUuid = async (uuid) => {
  const response = await axiosPrivate.get(`/notifications/${uuid}`);
  return response.data;
};

/**
 * Mark a notification as read
 * @param {string} uuid - Notification UUID
 * @returns {Promise<object>} Updated notification
 */
export const markAsRead = async (uuid) => {
  const response = await axiosPrivate.patch(`/notifications/${uuid}/read`);
  return response.data;
};

/**
 * Mark all notifications as read
 * @returns {Promise<object>} Response
 */
export const markAllAsRead = async () => {
  const response = await axiosPrivate.patch('/notifications/read-all');
  return response.data;
};

/**
 * Delete a notification
 * @param {string} uuid - Notification UUID
 * @returns {Promise<void>}
 */
export const deleteNotification = async (uuid) => {
  await axiosPrivate.delete(`/notifications/${uuid}`);
};

/**
 * Delete all notifications
 * @returns {Promise<object>} Response
 */
export const deleteAllNotifications = async () => {
  const response = await axiosPrivate.delete('/notifications/');
  return response.data;
};
