/**
 * Token utilities for JWT handling
 */

import { TOKEN_KEY, USER_KEY } from '../constants';

/**
 * Decode JWT payload without verification
 * @param {string} token - JWT token
 * @returns {object|null} Decoded payload or null if invalid
 */
export const getTokenPayload = (token) => {
  if (!token) return null;
  
  try {
    const base64Url = token.split('.')[1];
    const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/');
    const jsonPayload = decodeURIComponent(
      atob(base64)
        .split('')
        .map((c) => '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2))
        .join('')
    );
    return JSON.parse(jsonPayload);
  } catch (error) {
    console.error('Error decoding token:', error);
    return null;
  }
};

/**
 * Check if a JWT token is expired
 * @param {string} token - JWT token
 * @returns {boolean} True if expired or invalid
 */
export const isTokenExpired = (token) => {
  if (!token) return true;
  
  const payload = getTokenPayload(token);
  if (!payload || !payload.exp) return true;
  
  // exp is in seconds, Date.now() is in milliseconds
  return Date.now() >= payload.exp * 1000;
};

/**
 * Get stored token from localStorage
 * @returns {string|null} Token or null
 */
export const getStoredToken = () => {
  return localStorage.getItem(TOKEN_KEY);
};

/**
 * Get stored user from localStorage
 * @returns {object|null} User object or null
 */
export const getStoredUser = () => {
  try {
    const userStr = localStorage.getItem(USER_KEY);
    return userStr ? JSON.parse(userStr) : null;
  } catch {
    return null;
  }
};

/**
 * Store auth data in localStorage
 * @param {string} token - JWT token
 * @param {object} user - User object
 */
export const storeAuthData = (token, user) => {
  localStorage.setItem(TOKEN_KEY, token);
  localStorage.setItem(USER_KEY, JSON.stringify(user));
};

/**
 * Clear auth data from localStorage
 */
export const clearAuthData = () => {
  localStorage.removeItem(TOKEN_KEY);
  localStorage.removeItem(USER_KEY);
};

// Re-export token keys for convenience
export { TOKEN_KEY, USER_KEY };
