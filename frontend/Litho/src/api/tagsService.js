import { axiosInstance } from './axios';

export const getTags = async () => {
    try {
        const response = await axiosInstance.get('/posts/tags/');
        return response.data;
    } catch (error) {
        throw error;
    }
}; 