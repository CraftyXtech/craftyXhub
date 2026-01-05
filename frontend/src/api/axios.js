
import axios from 'axios';
import { isTokenExpired } from './utils/token';
import { API_BASE_URL, TOKEN_KEY, USER_KEY, getApiBaseUrl } from './constants';

export { TOKEN_KEY, USER_KEY, getApiBaseUrl };

/**
 * Public axios instance for unauthenticated requests
 */
export const axiosPublic = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: { 'Content-Type': 'application/json' },
});

/**
 * Private axios instance for authenticated requests
 * Automatically injects Bearer token from localStorage
 */
export const axiosPrivate = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: { 'Content-Type': 'application/json' },
});

// Request interceptor - add auth token to requests
axiosPrivate.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem(TOKEN_KEY);
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor - handle 401 errors
axiosPrivate.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Token expired or invalid - clear storage and redirect to login
      localStorage.removeItem(TOKEN_KEY);
      localStorage.removeItem(USER_KEY);
      
      // Only redirect if not already on auth page
      if (!window.location.pathname.startsWith('/auth')) {
        window.location.href = '/auth/login';
      }
    }
    return Promise.reject(error);
  }
);

/**
 * Get the API base URL (without /v1 suffix)
 */


export default axiosPublic;
