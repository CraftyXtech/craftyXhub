import { getApiBaseUrl } from '../axios';

/**
 * Image URL Utilities
 * Helpers for constructing full URLs from image paths
 */

/**
 * Get full image URL from path
 * @param {string} imagePath - Image path or URL
 * @param {string} folder - Image folder (default: 'posts')
 * @returns {string|null} Full image URL
 */
export const getImageUrl = (imagePath, folder = 'posts') => {
  if (!imagePath) return null;
  if (imagePath.startsWith('http://') || imagePath.startsWith('https://')) {
    return imagePath;
  }

  const filename = imagePath.split('/').pop();
  const apiBase = getApiBaseUrl();
  return `${apiBase}/v1/uploads/images/${filename}?folder=${folder}`;
};

/**
 * Get full media URL from path
 * @param {string} filePath - File path
 * @returns {string|null} Full media URL
 */
export const getMediaUrl = (filePath) => {
  if (!filePath) return null;
  if (filePath.startsWith('http')) return filePath;
  
  const apiBase = getApiBaseUrl();
  return `${apiBase}/media/files/${filePath}`;
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

/**
 * Get placeholder image URL
 * @param {number} width - Image width
 * @param {number} height - Image height
 * @param {string} text - Placeholder text
 * @returns {string} Placeholder URL
 */
export const getPlaceholderUrl = (width = 400, height = 300, text = '') => {
  return `https://via.placeholder.com/${width}x${height}${text ? `?text=${encodeURIComponent(text)}` : ''}`;
};
