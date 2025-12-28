import { axiosPublic } from '../axios';

/**
 * Search Service
 * Handles site-wide search functionality
 */

/**
 * Search content across posts, categories, tags, and authors
 * @param {string} query - Search query
 * @returns {Promise<object>} Search results
 */
export const searchContent = async (query) => {
  const response = await axiosPublic.get('/search', { params: { q: query } });
  return response.data;
};

/**
 * Search posts only
 * @param {string} query - Search query
 * @param {object} params - Additional filters
 * @returns {Promise<object>} Post search results
 */
export const searchPosts = async (query, params = {}) => {
  const response = await axiosPublic.get('/posts/', {
    params: { search: query, published: true, ...params },
  });
  return response.data;
};
