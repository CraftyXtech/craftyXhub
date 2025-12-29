import { axiosPrivate, axiosPublic } from '../axios';

/**
 * User Service
 * Handles user management operations (both standard and admin)
 */

// ===== PUBLIC USER OPERATIONS =====

/**
 * Get user by username (public profile)
 * @param {string} username - Username
 * @returns {Promise<object>} User data
 */
export const getUserByUsername = async (username) => {
  const response = await axiosPublic.get(`/users/username/${username}`);
  return response.data;
};

// ===== STANDARD USER OPERATIONS =====

// NOTE: getCurrentUser is in authService.js

/**
 * Get user by UUID
 * @param {string} userUuid - User UUID
 * @returns {Promise<object>} User data
 */
export const getUserByUuid = async (userUuid) => {
  const response = await axiosPrivate.get(`/auth/user/${userUuid}`);
  return response.data;
};

/**
 * Update user profile
 * @param {string} userUuid - User UUID
 * @param {object} updateData - Data to update
 * @returns {Promise<object>} Updated user
 */
export const updateUserProfile = async (userUuid, updateData) => {
  const response = await axiosPrivate.put(`/auth/user/${userUuid}`, updateData);
  return response.data;
};

// ===== ADMIN USER OPERATIONS =====

/**
 * Get all users (admin only)
 * @param {object} params - { skip, limit, search, role, is_active }
 * @returns {Promise<object>} { users, total }
 */
export const getUsers = async (params = {}) => {
  const response = await axiosPrivate.get('/admin/users', { params });
  return response.data;
};

/**
 * Get user by UUID (admin endpoint)
 * @param {string} userUuid - User UUID
 * @returns {Promise<object>} User data with admin details
 */
export const getAdminUserByUuid = async (userUuid) => {
  const response = await axiosPrivate.get(`/admin/users/${userUuid}`);
  return response.data;
};

/**
 * Update user (admin only)
 * @param {string} userUuid - User UUID
 * @param {object} updateData - Data to update
 * @returns {Promise<object>} Updated user
 */
export const updateAdminUser = async (userUuid, updateData) => {
  const response = await axiosPrivate.put(`/admin/users/${userUuid}`, updateData);
  return response.data;
};

/**
 * Change user role (admin only)
 * @param {string} userUuid - User UUID
 * @param {string} role - New role
 * @param {string} reason - Optional reason for role change
 * @returns {Promise<object>} Updated user
 */
export const changeUserRole = async (userUuid, role, reason) => {
  const payload = reason ? { role, reason } : { role };
  const response = await axiosPrivate.patch(`/admin/users/${userUuid}/role`, payload);
  return response.data;
};

/**
 * Toggle user active status (admin only)
 * @param {string} userUuid - User UUID
 * @param {boolean} isActive - New active status
 * @returns {Promise<object>} Updated user
 */
export const toggleUserStatus = async (userUuid, isActive) => {
  const response = await axiosPrivate.patch(`/admin/users/${userUuid}/status`, { is_active: isActive });
  return response.data;
};

/**
 * Deactivate/delete user (admin only)
 * @param {string} userUuid - User UUID
 * @returns {Promise<object>} Response
 */
export const deactivateUser = async (userUuid) => {
  const response = await axiosPrivate.delete(`/admin/users/${userUuid}`);
  return response.data;
};

/**
 * Get user statistics (admin only)
 * @returns {Promise<object>} User stats
 */
export const getUserStats = async () => {
  const response = await axiosPrivate.get('/admin/users/stats');
  return response.data;
};

// =============================================================================
// USER FOLLOW FUNCTIONS (Phase 6)
// =============================================================================

/**
 * Follow a user
 * @param {string} userUuid - UUID of user to follow
 * @returns {Promise<object>} Follow response
 */
export const followUser = async (userUuid) => {
  const response = await axiosPrivate.post(`/users/${userUuid}/follow`);
  return response.data;
};

/**
 * Unfollow a user
 * @param {string} userUuid - UUID of user to unfollow
 * @returns {Promise<object>} Unfollow response
 */
export const unfollowUser = async (userUuid) => {
  const response = await axiosPrivate.post(`/users/${userUuid}/unfollow`);
  return response.data;
};

/**
 * Get followers of a user
 * @param {string} userUuid - UUID of user
 * @param {object} params - { skip, limit }
 * @returns {Promise<object>} { followers, total, page, size }
 */
export const getFollowers = async (userUuid, params = {}) => {
  const response = await axiosPrivate.get(`/users/${userUuid}/followers`, { params });
  return response.data;
};

/**
 * Get users that a user is following
 * @param {string} userUuid - UUID of user
 * @param {object} params - { skip, limit }
 * @returns {Promise<object>} { following, total, page, size }
 */
export const getFollowing = async (userUuid, params = {}) => {
  const response = await axiosPrivate.get(`/users/${userUuid}/following`, { params });
  return response.data;
};
