import { axiosPrivate } from './axios';

export const userService = {
    getCurrentUser: async () => {
        try {
            const response = await axiosPrivate.get('/auth/me');
            return response.data;
        } catch (error) {
            console.error('Error fetching current user:', error);
            throw error;
        }
    },
    updateProfile: async (userUuid, updateData) => {
        try {
            const response = await axiosPrivate.put(`/auth/user/${userUuid}`, updateData);
            return response.data;
        } catch (error) {
            console.error('Error updating user profile:', error);
            throw error;
        }
    },

    getUserByUuid: async (userUuid) => {
        try {
            const response = await axiosPrivate.get(`/auth/user/${userUuid}`);
            return response.data;
        } catch (error) {
            console.error('Error fetching user:', error);
            throw error;
        }
    }
}; 