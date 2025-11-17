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
    },

    getUsers: async (params = {}) => {
        try {
            const response = await axiosPrivate.get('/admin/users', { params });
            return response.data;
        } catch (error) {
            console.error('Error fetching admin users:', error);
            throw error;
        }
    },

    getAdminUserByUuid: async (userUuid) => {
        try {
            const response = await axiosPrivate.get(`/admin/users/${userUuid}`);
            return response.data;
        } catch (error) {
            console.error('Error fetching admin user:', error);
            throw error;
        }
    },

    updateAdminUser: async (userUuid, updateData) => {
        try {
            const response = await axiosPrivate.put(`/admin/users/${userUuid}`, updateData);
            return response.data;
        } catch (error) {
            console.error('Error updating admin user:', error);
            throw error;
        }
    },

    changeUserRole: async (userUuid, role, reason) => {
        try {
            const payload = reason ? { role, reason } : { role };
            const response = await axiosPrivate.patch(`/admin/users/${userUuid}/role`, payload);
            return response.data;
        } catch (error) {
            console.error('Error changing user role:', error);
            throw error;
        }
    },

    toggleUserStatus: async (userUuid, isActive) => {
        try {
            const response = await axiosPrivate.patch(`/admin/users/${userUuid}/status`, { is_active: isActive });
            return response.data;
        } catch (error) {
            console.error('Error updating user status:', error);
            throw error;
        }
    },

    deactivateUser: async (userUuid) => {
        try {
            const response = await axiosPrivate.delete(`/admin/users/${userUuid}`);
            return response.data;
        } catch (error) {
            console.error('Error deactivating user:', error);
            throw error;
        }
    },

    getUserStats: async () => {
        try {
            const response = await axiosPrivate.get('/admin/users/stats');
            return response.data;
        } catch (error) {
            console.error('Error fetching user stats:', error);
            throw error;
        }
    },
}; 