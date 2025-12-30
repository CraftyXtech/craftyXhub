import { axiosPublic, axiosPrivate, getApiBaseUrl } from '../axios';

/**
 * Post Service
 * Handles all post-related API operations
 */

// ===== IMAGE UTILITIES =====

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

// ===== PUBLIC POST ENDPOINTS =====

/**
 * Get posts with filters and pagination
 * @param {object} params - { page, limit, category_id, author_id, tag_id, search, ... }
 * @returns {Promise<object>} { posts, total, page, size }
 */
export const getPosts = async (params = {}) => {
  const clientParams = { ...params, published: true };
  const response = await axiosPublic.get('/posts/', { params: clientParams });
  return response.data;
};

/**
 * Get a single post by UUID
 * @param {string} postUuid - Post UUID
 * @returns {Promise<object>} Post data
 */
export const getPost = async (postUuid) => {
  const response = await axiosPublic.get(`/posts/${postUuid}`);
  return response.data;
};

/**
 * Get a single post by slug
 * First tries to get by UUID (in case slug is a uuid), 
 * then fallback to querying posts list and finding match
 * @param {string} slug - Post slug or UUID
 * @returns {Promise<object>} Post data
 */
export const getPostBySlug = async (slug) => {
  // First try direct UUID fetch (works if slug is actually UUID)
  try {
    const response = await axiosPublic.get(`/posts/${slug}`);
    return response.data;
  } catch (err) {
    // Not found by UUID, search by slug in posts list
    if (err.response?.status === 404 || err.response?.status === 422) {
      const postsResponse = await axiosPublic.get('/posts/', {
        params: { limit: 1, published: true }
      });
      
      // Need to search through posts - get more to find by slug
      const allPostsResponse = await axiosPublic.get('/posts/', {
        params: { limit: 100, published: true }
      });
      
      const post = allPostsResponse.data.posts?.find(p => p.slug === slug);
      if (post) {
        // Get full post data by UUID
        return await getPost(post.uuid);
      }
      throw new Error('Post not found');
    }
    throw err;
  }
};

/**
 * Get popular posts
 * @param {object} params - { limit }
 * @returns {Promise<object>} Posts list
 */
export const getPopularPosts = async (params = {}) => {
  const response = await axiosPublic.get('/posts/popular', { params });
  return response.data;
};

/**
 * Get recent posts
 * @param {object} params - { limit }
 * @returns {Promise<object>} Posts list
 */
export const getRecentPosts = async (params = {}) => {
  const response = await axiosPublic.get('/posts/recent', { params });
  return response.data;
};

/**
 * Get trending posts
 * @param {object} params - { limit }
 * @returns {Promise<object>} Posts list
 */
export const getTrendingPosts = async (params = {}) => {
  const response = await axiosPublic.get('/posts/trending/', { params });
  return response.data;
};

/**
 * Get featured posts
 * @param {object} params - { limit }
 * @returns {Promise<object>} Posts list
 */
export const getFeaturedPosts = async (params = {}) => {
  const response = await axiosPublic.get('/posts/featured', { params });
  return response.data;
};

/**
 * Get personalized "For You" posts based on following and reading history
 * @param {object} params - { limit }
 * @returns {Promise<object>} Personalized posts list
 */
export const getForYouPosts = async (params = {}) => {
  const response = await axiosPrivate.get('/posts/for-you', { params });
  return response.data;
};

/**
 * Get related posts for a specific post
 * @param {string} postUuid - Post UUID
 * @param {object} params - { limit }
 * @returns {Promise<object>} Related posts list
 */
export const getRelatedPosts = async (postUuid, params = {}) => {
  const response = await axiosPublic.get(`/posts/${postUuid}/related`, { params });
  return response.data;
};

/**
 * Get posts by category
 * @param {number} categoryId - Category ID
 * @param {object} params - Pagination/filter params
 * @returns {Promise<object>} Posts list
 */
export const getPostsByCategory = async (categoryId, params = {}) => {
  const clientParams = { ...params, category_id: categoryId, published: true };
  const response = await axiosPublic.get('/posts/', { params: clientParams });
  return response.data;
};

/**
 * Get posts by author
 * @param {string} authorId - Author ID/UUID
 * @param {object} params - Pagination/filter params
 * @returns {Promise<object>} Posts list
 */
export const getPostsByAuthor = async (authorId, params = {}) => {
  const clientParams = { ...params, author_id: authorId, published: true };
  const response = await axiosPublic.get('/posts/', { params: clientParams });
  return response.data;
};

/**
 * Get post statistics
 * @returns {Promise<object>} Post stats
 */
export const getPostStats = async () => {
  const response = await axiosPublic.get('/posts/stats/');
  return response.data;
};

// ===== AUTHENTICATED POST ENDPOINTS =====

/**
 * Toggle like on a post
 * @param {string} postUuid - Post UUID
 * @returns {Promise<object>} Updated like status
 */
export const togglePostLike = async (postUuid) => {
  const response = await axiosPrivate.post(`/posts/${postUuid}/like`);
  return response.data;
};

/**
 * Bookmark/unbookmark a post
 * @param {string} postUuid - Post UUID
 * @returns {Promise<object>} Bookmark status
 */
export const bookmarkPost = async (postUuid) => {
  const response = await axiosPrivate.post(`/posts/${postUuid}/bookmark`);
  return response.data;
};

/**
 * Get user's bookmarked posts
 * @param {object} params - Pagination params
 * @returns {Promise<object>} Bookmarked posts
 */
export const getUserBookmarks = async (params = {}) => {
  const response = await axiosPrivate.get('/posts/users/me/bookmarks', { params });
  return response.data;
};

/**
 * Report a post
 * @param {string} postUuid - Post UUID
 * @param {object} reportData - { reason, details }
 * @returns {Promise<object>} Report response
 */
export const reportPost = async (postUuid, reportData) => {
  const response = await axiosPrivate.post(`/posts/${postUuid}/report`, reportData);
  return response.data;
};

// ===== POST CREATION & MANAGEMENT =====

/**
 * Create a new post
 * @param {object} postData - Post data (supports FormData for file uploads)
 * @returns {Promise<object>} Created post
 */
export const createPost = async (postData) => {
  const isFormData = postData instanceof FormData;
  const headers = isFormData ? { 'Content-Type': 'multipart/form-data' } : {};
  
  // If not FormData, convert to FormData for file support
  let formData = postData;
  if (!isFormData) {
    formData = new FormData();
    
    if (postData.title) formData.append('title', postData.title);
    if (postData.content) formData.append('content', postData.content);
    if (postData.excerpt) formData.append('excerpt', postData.excerpt);
    if (postData.slug) formData.append('slug', postData.slug);
    if (postData.meta_title) formData.append('meta_title', postData.meta_title);
    if (postData.meta_description) formData.append('meta_description', postData.meta_description);
    if (postData.category_id) formData.append('category_id', postData.category_id);
    if (postData.reading_time) formData.append('reading_time', postData.reading_time);
    
    // Content blocks as JSON
    if (postData.content_blocks) {
      const cb = Array.isArray(postData.content_blocks)
        ? { blocks: postData.content_blocks }
        : postData.content_blocks;
      formData.append('content_blocks', JSON.stringify(cb));
    }
    
    // Tags as comma-separated
    if (postData.tag_ids?.length) {
      formData.append('tag_ids', postData.tag_ids.join(','));
    }
    
    // Featured image
    if (postData.featured_image instanceof File) {
      formData.append('featured_image', postData.featured_image);
    }
    
    formData.append('is_published', postData.is_published || false);
  }
  
  const response = await axiosPrivate.post('/posts/', formData, { headers });
  return response.data;
};

/**
 * Update an existing post
 * @param {string} postUuid - Post UUID
 * @param {object} postData - Post data to update
 * @returns {Promise<object>} Updated post
 */
export const updatePost = async (postUuid, postData) => {
  const isFormData = postData instanceof FormData;
  const headers = isFormData ? { 'Content-Type': 'multipart/form-data' } : {};
  
  const response = await axiosPrivate.put(`/posts/${postUuid}`, postData, { headers });
  return response.data;
};

/**
 * Delete a post
 * @param {string} postUuid - Post UUID
 * @returns {Promise<object>} Delete response
 */
export const deletePost = async (postUuid) => {
  const response = await axiosPrivate.delete(`/posts/${postUuid}`);
  return response.data;
};

/**
 * Publish a draft post
 * @param {string} postUuid - Post UUID
 * @returns {Promise<object>} Published post
 */
export const publishPost = async (postUuid) => {
  const response = await axiosPrivate.put(`/posts/${postUuid}/publish`);
  return response.data;
};

/**
 * Unpublish a post
 * @param {string} postUuid - Post UUID
 * @returns {Promise<object>} Unpublished post
 */
export const unpublishPost = async (postUuid) => {
  const response = await axiosPrivate.put(`/posts/${postUuid}/unpublish`);
  return response.data;
};

/**
 * Feature/unfeature a post
 * @param {string} postUuid - Post UUID
 * @param {boolean} feature - True to feature, false to unfeature
 * @returns {Promise<object>} Updated post
 */
export const featurePost = async (postUuid, feature = true) => {
  const response = await axiosPrivate.put(`/posts/${postUuid}/feature?feature=${feature}`);
  return response.data;
};

/**
 * Get user's draft posts
 * @param {object} params - Pagination params
 * @returns {Promise<object>} Draft posts
 */
export const getUserDraftPosts = async (params = {}) => {
  const response = await axiosPrivate.get('/posts/drafts', { params });
  return response.data;
};
