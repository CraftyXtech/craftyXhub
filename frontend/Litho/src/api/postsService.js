import { axiosInstance, axiosPrivate } from './axios';

// ===== POSTS SERVICES =====
export const getPosts = async (params = {}) => {
    try {
        const clientParams = { ...params, published: true };
        const response = await axiosInstance.get('/posts/', { params: clientParams });
        return response.data;
    } catch (error) {
        throw error;
    }
};

export const getPost = async (postUuid) => {
    try {
        const response = await axiosInstance.get(`/posts/${postUuid}`);
        return response.data;
    } catch (error) {
        throw error;
    }
};

export const getPostImage = async (filename) => {
    try {
        const response = await axiosInstance.get(`/posts/images/${filename}`);
        return response.data;
    } catch (error) {
        throw error;
    }
};

export const togglePostLike = async (postUuid) => {
    try {
        const response = await axiosPrivate.post(`/posts/${postUuid}/like`);
        return response.data;
    } catch (error) {
        throw error;
    }
};

export const getPostStats = async () => {
    try {
        const response = await axiosInstance.get('/posts/stats/');
        return response.data;
    } catch (error) {
        throw error;
    }
};

export const getPostsByCategory = async (categoryId, params = {}) => {
    try {
        const clientParams = { ...params, category_id: categoryId, published: true };
        const response = await axiosInstance.get('/posts/', { params: clientParams });
        return response.data;
    } catch (error) {
        throw error;
    }
};

export const getPostsByAuthor = async (authorId, params = {}) => {
    try {
        const clientParams = { ...params, author_id: authorId, published: true };
        const response = await axiosInstance.get('/posts/', { params: clientParams });
        return response.data;
    } catch (error) {
        throw error;
    }
};

export const getPopularPosts = async (params = {}) => {
    try {
        const response = await axiosInstance.get('/posts/popular', { params });
        return response.data;
    } catch (error) {
        throw error;
    }
};

export const getRecentPosts = async (params = {}) => {
    try {
        const response = await axiosInstance.get('/v1/posts/recent', { params });
        return response.data;
    } catch (error) {
        console.error('Error fetching recent posts:', error);
        throw error;
    }
};

// Get related posts for a specific post
export const getRelatedPosts = async (postUuid, params = {}) => {
    try {
        const response = await axiosInstance.get(`/v1/posts/${postUuid}/related`, { params });
        return response.data;
    } catch (error) {
        console.error('Error fetching related posts:', error);
        throw error;
    }
};

// ===== COMMENTS SERVICES =====

// Get comments for a post or all comments with filters
export const getComments = async (params = {}) => {
    try {
        const response = await axiosInstance.get('/v1/comments/', { params });
        return response.data;
    } catch (error) {
        console.error('Error fetching comments:', error);
        throw error;
    }
};

// Get a single comment by UUID
export const getComment = async (commentUuid) => {
    try {
        const response = await axiosInstance.get(`/v1/comments/${commentUuid}`);
        return response.data;
    } catch (error) {
        console.error('Error fetching comment:', error);
        throw error;
    }
};

// Create a new comment
export const createComment = async (commentData) => {
    try {
        const response = await axiosPrivate.post('/v1/comments/', commentData);
        return response.data;
    } catch (error) {
        console.error('Error creating comment:', error);
        throw error;
    }
};

// Update a comment
export const updateComment = async (commentUuid, commentData) => {
    try {
        const response = await axiosPrivate.put(`/v1/comments/${commentUuid}`, commentData);
        return response.data;
    } catch (error) {
        console.error('Error updating comment:', error);
        throw error;
    }
};

// Delete a comment
export const deleteComment = async (commentUuid) => {
    try {
        const response = await axiosPrivate.delete(`/v1/comments/${commentUuid}`);
        return response.data;
    } catch (error) {
        console.error('Error deleting comment:', error);
        throw error;
    }
};

// Toggle like on a comment
export const toggleCommentLike = async (commentUuid) => {
    try {
        const response = await axiosPrivate.post(`/v1/comments/${commentUuid}/like`);
        return response.data;
    } catch (error) {
        console.error('Error toggling comment like:', error);
        throw error;
    }
};

// Report a comment
export const reportComment = async (commentUuid, reportData) => {
    try {
        const response = await axiosPrivate.post(`/v1/comments/${commentUuid}/report`, reportData);
        return response.data;
    } catch (error) {
        console.error('Error reporting comment:', error);
        throw error;
    }
};


// ===== CATEGORIES SERVICES =====
export const getCategories = async () => {
    try {
        const response = await axiosInstance.get('/posts/categories/');
        return response.data;
    } catch (error) {
        throw error;
    }
};

export const getSubcategories = async (categoryId) => {
    try {
        // TODO: Implement when backend API supports subcategories        
        return [];
    } catch (error) {
        throw error;
    }
};

// ===== TAGS SERVICES =====
export const getTags = async () => {
    try {
        const response = await axiosInstance.get('/posts/tags/');
        return response.data;
    } catch (error) {
        throw error;
    }
};

// ===== PROFILES SERVICES =====
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
        
        // Add profile fields
        if (profileData.bio) formData.append('bio', profileData.bio);
        if (profileData.location) formData.append('location', profileData.location);
        if (profileData.website) formData.append('website', profileData.website);
        if (profileData.twitter_handle) formData.append('twitter_handle', profileData.twitter_handle);
        if (profileData.github_handle) formData.append('github_handle', profileData.github_handle);
        if (profileData.linkedin_handle) formData.append('linkedin_handle', profileData.linkedin_handle);
        if (profileData.birth_date) formData.append('birth_date', profileData.birth_date);
        
        // Add avatar file if provided
        if (profileData.avatar) {
            formData.append('avatar', profileData.avatar);
        }

        const response = await axiosPrivate.post('/profiles', formData, {
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