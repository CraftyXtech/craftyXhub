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

// =============================================================================
// PUBLIC PASSWORD RESET & EMAIL VERIFICATION (Phase 3)
// =============================================================================

/**
 * Request password reset via email
 * @param {string} email - User email address
 * @returns {Promise<object>} { message, success }
 */
export const requestPasswordReset = async (email) => {
  const response = await axiosPublic.post('/auth/password-reset/request', { email });
  return response.data;
};

/**
 * Reset password with token
 * @param {string} token - Reset token from email
 * @param {string} newPassword - New password
 * @param {string} confirmPassword - Confirm new password
 * @returns {Promise<object>} { message, success }
 */
export const resetPassword = async (token, newPassword, confirmPassword) => {
  const response = await axiosPublic.post('/auth/password-reset/confirm', {
    token,
    new_password: newPassword,
    confirm_password: confirmPassword,
  });
  return response.data;
};

/**
 * Verify email with token
 * @param {string} token - Verification token from email
 * @returns {Promise<object>} { message, success }
 */
export const verifyEmail = async (token) => {
  const response = await axiosPublic.post('/auth/verify-email', { token });
  return response.data;
};

