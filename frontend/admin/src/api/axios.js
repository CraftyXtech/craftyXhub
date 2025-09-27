import axios from 'axios';
const BASE_URL = import.meta.env.VITE_API_BASE_URL;
console.log('Environment Variables:', import.meta.env);
console.log('VITE_API_BASE_URL:', import.meta.env.VITE_API_BASE_URL);
console.log('Final BASE_URL:', BASE_URL);
export const axiosPublic = axios.create({
    baseURL: BASE_URL,
    headers: {
        'Content-Type': 'application/json',
    },
});

export default axiosPublic;

export const axiosPrivate = axios.create({
    baseURL: BASE_URL,
    headers: { 
        'Content-Type': 'application/json',
    },
    withCredentials: false
});

// Add request interceptor to include auth token
axiosPrivate.interceptors.request.use(
    (config) => {
        const token = localStorage.getItem('accessToken');
        if (token) {
            config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
    },
    (error) => {
        return Promise.reject(error);
    }
);

// Add response interceptor to handle auth errors
axiosPrivate.interceptors.response.use(
    (response) => {
        return response;
    },
    async (error) => {
        if (error.response?.status === 401) {
            // Token expired or invalid, redirect to login
            localStorage.removeItem('accessToken');
            localStorage.removeItem('userInfo');
            window.location.href = '/login';
        }
        return Promise.reject(error);
    }
);
