import { axiosPrivate } from '../axios';

/**
 * Dashboard Service
 * Handles dashboard analytics fetching for admin and user views
 */

/**
 * Get admin dashboard analytics
 * System-wide metrics for admins and moderators
 * @returns {Promise<object>} Admin dashboard data including:
 *   - post_stats: { total, published, drafts, featured }
 *   - user_stats: { total, active, new_this_month }
 *   - engagement: { total_views, total_likes, total_comments }
 *   - top_posts: Array of top performing posts
 *   - recent_activity: Array of recent events
 */
export const getAdminDashboard = async () => {
  const response = await axiosPrivate.get('/dashboard/admin');
  return response.data;
};

/**
 * Get user dashboard analytics
 * Creator-focused metrics for the current user
 * @returns {Promise<object>} User dashboard data including:
 *   - post_stats: { total, published, drafts }
 *   - engagement: { total_views, total_likes, total_comments }
 *   - top_posts: Array of user's top performing posts
 *   - recent_activity: Array of recent events on user's content
 *   - drafts: Array of recent drafts
 */
export const getUserDashboard = async () => {
  const response = await axiosPrivate.get('/dashboard/user');
  return response.data;
};
