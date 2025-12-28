import { axiosPublic, axiosPrivate } from '../axios';

/**
 * Tag Service
 * Handles all tag-related API operations
 */

/**
 * Get all tags
 * @returns {Promise<object>} { tags }
 */
export const getTags = async () => {
  const response = await axiosPublic.get('/posts/tags/');
  return response.data;
};

/**
 * Get a tag by ID
 * @param {number} tagId - Tag ID
 * @returns {Promise<object|null>} Tag or null
 */
export const getTagById = async (tagId) => {
  const { data } = await axiosPublic.get('/posts/tags/');
  const tags = data.tags || [];
  return tags.find((t) => t.id === tagId) || null;
};

/**
 * Get a tag by slug
 * @param {string} slug - Tag slug
 * @returns {Promise<object|null>} Tag or null
 */
export const getTagBySlug = async (slug) => {
  const { data } = await axiosPublic.get('/posts/tags/');
  const tags = data.tags || [];
  return tags.find((t) => t.slug === slug) || null;
};

/**
 * Create a new tag (admin only)
 * @param {object} tagData - { name, slug?, description? }
 * @returns {Promise<object>} Created tag
 */
export const createTag = async (tagData) => {
  const response = await axiosPrivate.post('/posts/tags/', tagData);
  return response.data;
};

/**
 * Update a tag (admin only)
 * @param {number} tagId - Tag ID
 * @param {object} tagData - Tag data to update
 * @returns {Promise<object>} Updated tag
 */
export const updateTag = async (tagId, tagData) => {
  const response = await axiosPrivate.put(`/posts/tags/${tagId}`, tagData);
  return response.data;
};

/**
 * Delete a tag (admin only)
 * @param {number} tagId - Tag ID
 * @returns {Promise<void>}
 */
export const deleteTag = async (tagId) => {
  await axiosPrivate.delete(`/posts/tags/${tagId}`);
};
