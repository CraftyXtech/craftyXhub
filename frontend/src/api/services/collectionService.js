import { axiosPrivate } from '../axios';

/**
 * Collection Service
 * API functions for My Collection feature: Reading Lists, Reading History, Highlights
 */

// ===== Reading Lists =====

/**
 * Get user's reading lists
 * @returns {Promise<object>} { lists, total }
 */
export const getReadingLists = async () => {
  const response = await axiosPrivate.get('/collection/lists');
  return response.data;
};

/**
 * Create a new reading list
 * @param {object} data - { name, description?, is_public?, cover_image? }
 * @returns {Promise<object>} Created list
 */
export const createReadingList = async (data) => {
  const response = await axiosPrivate.post('/collection/lists', data);
  return response.data;
};

/**
 * Get a single reading list with items
 * @param {string} uuid - List UUID
 * @returns {Promise<object>} List with items
 */
export const getReadingList = async (uuid) => {
  const response = await axiosPrivate.get(`/collection/lists/${uuid}`);
  return response.data;
};

/**
 * Update a reading list
 * @param {string} uuid - List UUID
 * @param {object} data - { name?, description?, is_public?, cover_image? }
 * @returns {Promise<object>} Updated list
 */
export const updateReadingList = async (uuid, data) => {
  const response = await axiosPrivate.put(`/collection/lists/${uuid}`, data);
  return response.data;
};

/**
 * Delete a reading list
 * @param {string} uuid - List UUID
 */
export const deleteReadingList = async (uuid) => {
  await axiosPrivate.delete(`/collection/lists/${uuid}`);
};

/**
 * Add a post to a reading list
 * @param {string} listUuid - List UUID
 * @param {string} postUuid - Post UUID
 * @param {string} note - Optional note
 * @returns {Promise<object>} { message, item_uuid }
 */
export const addPostToList = async (listUuid, postUuid, note = null) => {
  const response = await axiosPrivate.post(`/collection/lists/${listUuid}/posts`, {
    post_uuid: postUuid,
    note
  });
  return response.data;
};

/**
 * Remove a post from a reading list
 * @param {string} listUuid - List UUID
 * @param {string} postUuid - Post UUID
 */
export const removePostFromList = async (listUuid, postUuid) => {
  await axiosPrivate.delete(`/collection/lists/${listUuid}/posts/${postUuid}`);
};

// ===== Reading History =====

/**
 * Get user's reading history
 * @param {object} params - { skip?, limit? }
 * @returns {Promise<object>} { entries, total }
 */
export const getReadingHistory = async (params = {}) => {
  const response = await axiosPrivate.get('/collection/history', { params });
  return response.data;
};

/**
 * Record a post view in reading history
 * @param {string} postUuid - Post UUID
 * @param {number} progress - Read progress 0-100
 * @returns {Promise<object>} { message, entry_uuid }
 */
export const recordPostView = async (postUuid, progress = 0) => {
  const response = await axiosPrivate.post(`/collection/history/${postUuid}?progress=${progress}`);
  return response.data;
};

/**
 * Clear all reading history
 */
export const clearReadingHistory = async () => {
  await axiosPrivate.delete('/collection/history');
};

// ===== Highlights =====

/**
 * Get user's highlights
 * @param {object} params - { skip?, limit? }
 * @returns {Promise<object>} { highlights, total }
 */
export const getHighlights = async (params = {}) => {
  const response = await axiosPrivate.get('/collection/highlights', { params });
  return response.data;
};

/**
 * Create a new highlight
 * @param {object} data - { post_uuid, text, note?, position_start?, position_end? }
 * @returns {Promise<object>} { message, highlight_uuid }
 */
export const createHighlight = async (data) => {
  const response = await axiosPrivate.post('/collection/highlights', data);
  return response.data;
};

/**
 * Delete a highlight
 * @param {string} uuid - Highlight UUID
 */
export const deleteHighlight = async (uuid) => {
  await axiosPrivate.delete(`/collection/highlights/${uuid}`);
};

// ===== User Comments (for Comments tab) =====

/**
 * Get current user's comments
 * @param {object} params - { skip?, limit? }
 * @returns {Promise<object>} { comments }
 */
export const getUserComments = async (params = {}) => {
  const response = await axiosPrivate.get('/comments/user/me', { params });
  return response.data;
};
