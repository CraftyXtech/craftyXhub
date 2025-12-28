import { axiosPublic, axiosPrivate } from '../axios';

/**
 * Comment Service
 * Handles all comment-related API operations
 */

/**
 * Get comments for a post
 * @param {string} postUuid - Post UUID
 * @param {object} params - { skip, limit }
 * @returns {Promise<object>} { comments, total }
 */
export const getComments = async (postUuid, params = {}) => {
  if (!postUuid) {
    throw new Error('post_uuid is required to fetch comments');
  }
  const response = await axiosPublic.get(`/comments/${postUuid}/comments`, { params });
  return response.data;
};

/**
 * Get a single comment by UUID
 * @param {string} commentUuid - Comment UUID
 * @returns {Promise<object>} Comment data
 */
export const getComment = async (commentUuid) => {
  const response = await axiosPublic.get(`/comments/${commentUuid}`);
  return response.data;
};

/**
 * Create a new comment
 * @param {string} postUuid - Post UUID
 * @param {object} commentData - { content, parent_id? }
 * @returns {Promise<object>} Created comment
 */
export const createComment = async (postUuid, commentData) => {
  if (!postUuid) {
    throw new Error('post_uuid is required to create a comment');
  }
  const response = await axiosPrivate.post(`/comments/${postUuid}/comments`, commentData);
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
 * @returns {Promise<object>} Updated like status
 */
export const toggleCommentLike = async (commentUuid) => {
  const response = await axiosPrivate.post(`/comments/${commentUuid}/like`);
  return response.data;
};

/**
 * Report a comment
 * @param {string} commentUuid - Comment UUID
 * @param {object} reportData - { reason, details }
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
