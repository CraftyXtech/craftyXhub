import { axiosInstance, axiosPrivate } from './axios';


export const getProfile = async (userUuid) => {
    try {
        const response = await axiosInstance.get(`/profiles/${userUuid}`);
        return response.data;
    } catch (error) {
        throw error;
    }
};

export const createProfile = async (profileData) => {
    try {
        const formData = new FormData();
        
        if (profileData.bio) formData.append('bio', profileData.bio);
        if (profileData.location) formData.append('location', profileData.location);
        if (profileData.website) formData.append('website', profileData.website);
        if (profileData.twitter_handle) formData.append('twitter_handle', profileData.twitter_handle);
        if (profileData.github_handle) formData.append('github_handle', profileData.github_handle);
        if (profileData.linkedin_handle) formData.append('linkedin_handle', profileData.linkedin_handle);
        if (profileData.birth_date) formData.append('birth_date', profileData.birth_date);
        
        if (profileData.avatar) {
            formData.append('avatar', profileData.avatar);
        }

        const response = await axiosPrivate.post('/profiles/', formData, {
            headers: {
                'Content-Type': 'multipart/form-data',
            },
        });
        return response.data;
    } catch (error) {
        throw error;
    }
};

export const updateProfile = async (userUuid, profileData) => {
    try {
        const formData = new FormData();
        
        if (profileData.bio !== undefined) formData.append('bio', profileData.bio || '');
        if (profileData.location !== undefined) formData.append('location', profileData.location || '');
        if (profileData.website !== undefined) formData.append('website', profileData.website || '');
        if (profileData.twitter_handle !== undefined) formData.append('twitter_handle', profileData.twitter_handle || '');
        if (profileData.github_handle !== undefined) formData.append('github_handle', profileData.github_handle || '');
        if (profileData.linkedin_handle !== undefined) formData.append('linkedin_handle', profileData.linkedin_handle || '');
        if (profileData.birth_date !== undefined) formData.append('birth_date', profileData.birth_date || '');
        
        if (profileData.avatar) {
            formData.append('avatar', profileData.avatar);
        }

        const response = await axiosPrivate.put(`/profiles/${userUuid}`, formData, {
            headers: {
                'Content-Type': 'multipart/form-data',
            },
        });
        return response.data;
    } catch (error) {
        throw error;
    }
};

export const deleteProfile = async (userUuid) => {
    try {
        const response = await axiosPrivate.delete(`/profiles/${userUuid}`);
        return response.data;
    } catch (error) {
        throw error;
    }
}; 