// API base URL - defaults to localhost:8000/v1 for development
export const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/v1';

// Token storage keys
export const TOKEN_KEY = 'craftyxhub_token';
export const USER_KEY = 'craftyxhub_user';

/**
 * Get the API base URL (without /v1 suffix)
 */
export const getApiBaseUrl = () => {
  return API_BASE_URL.replace('/v1', '').replace(/\/$/, '');
};
