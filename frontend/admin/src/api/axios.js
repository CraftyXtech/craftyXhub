import axios from 'axios';
const BASE_URL =   import.meta.env.VITE_APP_API_URL;
 

export default axios.create({
    baseURL: BASE_URL,
    headers: { 'Content-Type': 'application/json','Access-Control-Allow-Origin': 'http://localhost:5173,' },
});

export const axiosPrivate = axios.create({
    baseURL: BASE_URL,
    headers: { 'Content-Type': 'application/json','Access-Control-Allow-Origin': 'http://localhost:5173,' },
    withCredentials: true
});

