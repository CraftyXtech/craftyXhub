import { axiosPrivate, getApiBaseUrl } from '../axios';

/**
 * Media Service
 * Handles file uploads and media management
 */

// ===== MEDIA CRUD =====

/**
 * Get user's media files
 * @param {number} page - Page number
 * @param {number} limit - Items per page
 * @returns {Promise<object>} Media list
 */
export const getUserMedia = async (page = 1, limit = 20) => {
  const response = await axiosPrivate.get('/media/', { params: { page, limit } });
  return response.data;
};

/**
 * Upload a media file
 * @param {File} file - File to upload
 * @param {string} description - Optional description
 * @param {function} onProgress - Optional progress callback
 * @returns {Promise<object>} Uploaded media data
 */
export const uploadMedia = async (file, description = null, onProgress = null) => {
  const formData = new FormData();
  formData.append('file', file);
  if (description) formData.append('description', description);
  
  const config = {
    headers: { 'Content-Type': 'multipart/form-data' },
    onUploadProgress: onProgress
      ? (progressEvent) => {
          const percentCompleted = Math.round((progressEvent.loaded * 100) / progressEvent.total);
          onProgress(percentCompleted);
        }
      : undefined,
  };
  
  const response = await axiosPrivate.post('/media/upload', formData, config);
  return response.data;
};

/**
 * Get media by UUID
 * @param {string} mediaUuid - Media UUID
 * @returns {Promise<object>} Media data
 */
export const getMediaByUuid = async (mediaUuid) => {
  const response = await axiosPrivate.get(`/media/${mediaUuid}`);
  return response.data;
};

/**
 * Update media description
 * @param {string} mediaUuid - Media UUID
 * @param {string} description - New description
 * @returns {Promise<object>} Updated media
 */
export const updateMedia = async (mediaUuid, description) => {
  const response = await axiosPrivate.put(`/media/${mediaUuid}`, { description });
  return response.data;
};

/**
 * Delete a media file
 * @param {string} mediaUuid - Media UUID
 * @returns {Promise<object>} Delete response
 */
export const deleteMedia = async (mediaUuid) => {
  const response = await axiosPrivate.delete(`/media/${mediaUuid}`);
  return response.data;
};

// ===== HELPER FUNCTIONS =====

/**
 * Get full URL for a media file
 * @param {string} filePath - File path
 * @returns {string|null} Full URL
 */
export const getMediaUrl = (filePath) => {
  if (!filePath) return null;
  if (filePath.startsWith('http')) return filePath;
  
  const apiBase = getApiBaseUrl();
  return `${apiBase}/media/files/${filePath}`;
};

/**
 * Format file size to human readable
 * @param {number} bytes - File size in bytes
 * @returns {string} Formatted size
 */
export const formatFileSize = (bytes) => {
  if (!bytes) return '0 Bytes';
  
  const k = 1024;
  const sizes = ['Bytes', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
};

/**
 * Check if file is an image
 * @param {string} mimeType - MIME type
 * @returns {boolean}
 */
export const isImageFile = (mimeType) => mimeType?.startsWith('image/');

/**
 * Check if file is a video
 * @param {string} mimeType - MIME type
 * @returns {boolean}
 */
export const isVideoFile = (mimeType) => mimeType?.startsWith('video/');

/**
 * Check if file is a PDF
 * @param {string} mimeType - MIME type
 * @returns {boolean}
 */
export const isPdfFile = (mimeType) => mimeType === 'application/pdf';

/**
 * Get appropriate icon class for file type
 * @param {string} mimeType - MIME type
 * @returns {string} Icon class
 */
export const getFileIcon = (mimeType) => {
  if (isImageFile(mimeType)) return 'fas fa-image';
  if (isVideoFile(mimeType)) return 'fas fa-video';
  if (isPdfFile(mimeType)) return 'fas fa-file-pdf';
  if (mimeType?.includes('audio')) return 'fas fa-music';
  if (mimeType?.includes('text')) return 'fas fa-file-alt';
  return 'fas fa-file';
};

/**
 * Validate file before upload
 * @param {File} file - File to validate
 * @param {number} maxSizeBytes - Max file size (default 10MB)
 * @returns {object} { isValid, errors }
 */
export const validateFile = (file, maxSizeBytes = 10 * 1024 * 1024) => {
  const errors = [];
  
  if (file.size > maxSizeBytes) {
    errors.push(`File size must be less than ${formatFileSize(maxSizeBytes)}`);
  }
  
  const allowedTypes = [
    'image/jpeg', 'image/jpg', 'image/png', 'image/gif', 'image/webp',
    'video/mp4', 'video/webm', 'video/ogg',
    'application/pdf',
    'audio/mpeg', 'audio/wav',
  ];
  
  if (!allowedTypes.includes(file.type)) {
    errors.push('File type not supported');
  }
  
  return { isValid: errors.length === 0, errors };
};
