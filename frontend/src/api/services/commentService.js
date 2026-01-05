import { axiosPublic, axiosPrivate } from '../axios';

/**
 * Comment Service
 * Handles all comment-related API operations
 */

/**
 * Get comments for a post
 * @param {string} postSlug - Post slug
 * @param {object} params - { skip, limit }
 * @returns {Promise<object>} { comments, total }
 */
export const getComments = async (postSlug, params = {}) => {
  if (!postSlug) {
    throw new Error('post_slug is required to fetch comments');
  }
  const response = await axiosPublic.get(`/comments/${postSlug}/comments`, { params });
  return response.data;
};

/**
 * Get a single comment by UUID
 * TODO: Backend endpoint not implemented yet
 * @param {string} commentUuid - Comment UUID
 * @returns {Promise<object>} Comment data
 */
export const getComment = async (/* commentUuid */) => {
  console.warn('getComment: Backend endpoint for single comment not implemented');
  throw new Error('Get single comment functionality is not yet available');
};

/**
 * Create a new comment
 * @param {string} postSlug - Post slug
 * @param {object} commentData - { content, parent_id? }
 * @returns {Promise<object>} Created comment
 */
export const createComment = async (postSlug, commentData) => {
  if (!postSlug) {
    throw new Error('post_slug is required to create a comment');
  }
  const response = await axiosPrivate.post(`/comments/${postSlug}/comments`, commentData);
  return response.data;
};

/**
 * Update a comment
 * @param {string} commentUuid - Comment UUID
 * @param {object} commentData - { content }
 * @returns {Promise<object>} Updated comment
 */
export const updateComment = async (commentUuid, commentData) => {
  const response = await axiosPrivate.put(`/comments/${commentUuid}`, commentData);
  return response.data;
};

/**
 * Delete a comment
 * @param {string} commentUuid - Comment UUID
 * @returns {Promise<object>} Delete response
 */
export const deleteComment = async (commentUuid) => {
  const response = await axiosPrivate.delete(`/comments/${commentUuid}`);
  return response.data;
};

/**
 * Toggle like on a comment
 * @param {string} commentUuid - Comment UUID
 * @returns {Promise<object>} { liked, likes_count }
 */
export const toggleCommentLike = async (commentUuid) => {
  const response = await axiosPrivate.post(`/comments/${commentUuid}/like`);
  return response.data;
};

/**
 * Report a comment
 * @param {string} commentUuid - Comment UUID
 * @param {object} reportData - { reason, description }
 * @returns {Promise<object>} Report response
 */
export const reportComment = async (commentUuid, reportData) => {
  const response = await axiosPrivate.post(`/comments/${commentUuid}/report`, reportData);
  return response.data;
};

/**
 * Approve a comment (admin only)
 * @param {string} commentUuid - Comment UUID
 * @returns {Promise<object>} Approved comment
 */
export const approveComment = async (commentUuid) => {
  const response = await axiosPrivate.put(`/comments/${commentUuid}/approve`);
  return response.data;
};
