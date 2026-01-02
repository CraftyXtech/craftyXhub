import { axiosPublic, axiosPrivate, getApiBaseUrl } from '../axios';

/**
 * Profile Service
 * Handles user profile operations (bio, social links, avatar)
 */

/**
 * Get a user's public profile
 * @param {string} userUuid - User UUID
 * @returns {Promise<object>} Profile data
 */
export const getProfile = async (userUuid) => {
  const response = await axiosPublic.get(`/profiles/${userUuid}`);
  return response.data;
};

/**
 * Create a profile
 * @param {object} profileData - Profile data with optional avatar file
 * @returns {Promise<object>} Created profile
 */
export const createProfile = async (profileData) => {
  const formData = new FormData();
  
  if (profileData.bio) formData.append('bio', profileData.bio);
  if (profileData.location) formData.append('location', profileData.location);
  if (profileData.twitter_handle) formData.append('twitter_handle', profileData.twitter_handle);
  if (profileData.linkedin_handle) formData.append('linkedin_handle', profileData.linkedin_handle);
  if (profileData.instagram_handle) formData.append('instagram_handle', profileData.instagram_handle);
  if (profileData.facebook_handle) formData.append('facebook_handle', profileData.facebook_handle);
  if (profileData.birth_date) formData.append('birth_date', profileData.birth_date);
  
  // Avatar file
  if (profileData.avatar instanceof File) {
    formData.append('avatar', profileData.avatar);
  }
  
  const response = await axiosPrivate.post('/profiles', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });
  return response.data;
};

/**
 * Update a profile
 * @param {string} userUuid - User UUID
 * @param {object} profileData - Profile data to update
 * @returns {Promise<object>} Updated profile
 */
export const updateProfile = async (userUuid, profileData) => {
  const formData = new FormData();
  
  if (profileData.bio !== undefined) formData.append('bio', profileData.bio || '');
  if (profileData.location !== undefined) formData.append('location', profileData.location || '');
  if (profileData.twitter_handle !== undefined) formData.append('twitter_handle', profileData.twitter_handle || '');
  if (profileData.linkedin_handle !== undefined) formData.append('linkedin_handle', profileData.linkedin_handle || '');
  if (profileData.instagram_handle !== undefined) formData.append('instagram_handle', profileData.instagram_handle || '');
  if (profileData.facebook_handle !== undefined) formData.append('facebook_handle', profileData.facebook_handle || '');
  if (profileData.birth_date !== undefined) formData.append('birth_date', profileData.birth_date || '');
  
  if (profileData.avatar instanceof File) {
    formData.append('avatar', profileData.avatar);
  }
  
  const response = await axiosPrivate.put(`/profiles/${userUuid}`, formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });
  return response.data;
};

/**
 * Delete a profile
 * @param {string} userUuid - User UUID
 * @returns {Promise<object>} Delete response
 */
export const deleteProfile = async (userUuid) => {
  const response = await axiosPrivate.delete(`/profiles/${userUuid}`);
  return response.data;
};

/**
 * Get avatar URL
 * @param {string} avatarPath - Avatar path
 * @returns {string|null} Full avatar URL
 */
export const getAvatarUrl = (avatarPath) => {
  if (!avatarPath) return null;
  if (avatarPath.startsWith('http')) return avatarPath;
  
  const apiBase = getApiBaseUrl();
  return `${apiBase}/v1/uploads/avatars/${avatarPath}`;
};
