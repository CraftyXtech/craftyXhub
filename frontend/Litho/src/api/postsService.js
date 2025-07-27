import { axiosInstance, axiosPrivate } from './axios';

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