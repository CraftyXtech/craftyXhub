import axios from 'axios';
import { isTokenExpired } from './utils/token';

// API base URL - defaults to localhost:8000/v1 for development
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/v1';

// Token storage keys
export const TOKEN_KEY = 'craftyxhub_token';
export const USER_KEY = 'craftyxhub_user';

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
export const getApiBaseUrl = () => {
  return API_BASE_URL.replace('/v1', '').replace(/\/$/, '');
};

export default axiosPublic;
