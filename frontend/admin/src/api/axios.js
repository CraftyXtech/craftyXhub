import axios from 'axios';
// Adjust base URL to match FastAPI backend routes (e.g., http://127.0.0.1:8000/v1)
const BASE_URL = import.meta.env.VITE_APP_API_URL || 'http://127.0.0.1:8000/v1'
 

export default axios.create({
    baseURL: BASE_URL,
    headers: { 
        'Content-Type': 'application/json',
    },
});

export const axiosPrivate = axios.create({
    baseURL: BASE_URL,
    headers: { 
        'Content-Type': 'application/json',
    },
    withCredentials: false
});
