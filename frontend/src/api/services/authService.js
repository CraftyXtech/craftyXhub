import { axiosPublic, axiosPrivate } from '../axios';

/**
 * Authentication Service
 * Handles login, register, logout, and user retrieval
 */

/**
 * Register a new user
 * @param {object} userData - { email, password, first_name, last_name, ... }
 * @returns {Promise<object>} Registration response
 */
export const register = async (userData) => {
  const response = await axiosPublic.post('/auth/register', userData);
  return response.data;
};

/**
 * Login user
 * @param {object} credentials - { email, password }
 * @returns {Promise<object>} { access_token, user, ... }
 */
export const login = async (credentials) => {
  const response = await axiosPublic.post('/auth/login', credentials);
  return response.data;
};

/**
 * Logout current user
 * @returns {Promise<object>} Logout response
 */
export const logout = async () => {
  const response = await axiosPrivate.post('/auth/logout');
  return response.data;
};

/**
 * Get current authenticated user
 * @returns {Promise<object>} Current user data
 */
export const getCurrentUser = async () => {
  const response = await axiosPrivate.get('/auth/me');
  return response.data;
};

/**
 * Request password reset
 * @param {string} email - User email
 * @returns {Promise<object>} Response
 */
export const requestPasswordReset = async (email) => {
  const response = await axiosPublic.post('/auth/password-reset/request', { email });
  return response.data;
};

/**
 * Reset password with token
 * @param {string} token - Reset token
 * @param {string} newPassword - New password
 * @returns {Promise<object>} Response
 */
export const resetPassword = async (token, newPassword) => {
  const response = await axiosPublic.post('/auth/password-reset/confirm', {
    token,
    new_password: newPassword,
  });
  return response.data;
};

/**
 * Verify email with token
 * @param {string} token - Verification token
 * @returns {Promise<object>} Response
 */
export const verifyEmail = async (token) => {
  const response = await axiosPublic.post('/auth/verify-email', { token });
  return response.data;
};
