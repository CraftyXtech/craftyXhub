/**
 * CraftyXHub Unified API Layer
 * 
 * Central export file for all API services, hooks, and utilities.
 * Import from '@/api' or 'src/api' in your components.
 * 
 * @example
 * // Import services
 * import { getPosts, createPost } from '@/api';
 * 
 * // Import hooks
 * import { useGetPosts, useAuth } from '@/api';
 * 
 * // Import utilities
 * import { getImageUrl, formatDate } from '@/api';
 */

// ===== AXIOS INSTANCES =====
export { axiosPublic, axiosPrivate, getApiBaseUrl, TOKEN_KEY, USER_KEY } from './axios';

// ===== AUTH CONTEXT =====
export { AuthProvider, useAuth } from './AuthProvider';

// ===== SERVICES =====
// Auth
export * from './services/authService';

// Posts
export * from './services/postService';

// Comments
export * from './services/commentService';

// Categories
export * from './services/categoryService';

// Tags
export * from './services/tagService';

// Users
export * from './services/userService';

// Profiles
export * from './services/profileService';

// Media
export * from './services/mediaService';

// Notifications
export * from './services/notificationService';

// AI
export * from './services/aiService';

// Search
export * from './services/searchService';

// ===== HOOKS =====
// Core hooks
export { default as useAxiosPrivate } from './hooks/useAxiosPrivate';
export { default as useRefreshToken } from './hooks/useRefreshToken';

// Posts hooks
export {
  useGetPosts,
  useGetPost,
  useCreatePost,
  useUpdatePost,
  useDeletePost,
  useTogglePostLike,
  usePublishPost,
  useUnpublishPost,
  useFeaturePost,
  useGetPostStats,
  useImageUrl,
} from './hooks/usePosts';

// Comments hooks
export {
  useGetPostComments,
  useCreateComment,
  useUpdateComment,
  useDeleteComment,
  useApproveComment,
} from './hooks/useComments';

// Categories hooks
export {
  useGetCategories,
  useCreateCategory,
  useUpdateCategory,
  useDeleteCategory,
  useGetCategoryStats,
  useValidateCategorySlug,
} from './hooks/useCategories';

// Tags hooks
export {
  useGetTags,
  useCreateTag,
  useUpdateTag,
  useDeleteTag,
} from './hooks/useTags';

// Notifications hooks
export {
  useGetNotifications,
  useNotificationStats,
  useMarkNotificationRead,
} from './hooks/useNotifications';

// ===== UTILITIES =====
// Token utilities
export {
  isTokenExpired,
  getTokenPayload,
  getStoredToken,
  getStoredUser,
  storeAuthData,
  clearAuthData,
} from './utils/token';

// Image URL utilities
export {
  getImageUrl as getImageUrlHelper,
  getMediaUrl,
  getAvatarUrl,
  getPlaceholderUrl,
} from './utils/imageUrl';

// Formatters
export {
  formatFileSize,
  formatDate,
  formatRelativeTime,
  truncateText,
  generateSlug,
  formatNumber,
  calculateReadingTime,
} from './utils/formatters';
