import { axiosPublic, axiosPrivate, getApiBaseUrl } from '../axios';

/**
 * Post Service
 * Handles all post-related API operations
 */

// ===== IMAGE UTILITIES =====

/**
 * Get full image URL from path
 * @param {string} imagePath - Image path or URL (e.g., "uploads/images/uuid.jpg" or "uploads/media/uuid.jpg")
 * @param {string} folder - Image folder override (default: auto-detect from path, fallback 'posts')
 * @returns {string|null} Full image URL
 */
export const getImageUrl = (imagePath, folder = null) => {
  if (!imagePath) return null;
  if (imagePath.startsWith('http://') || imagePath.startsWith('https://')) {
    return imagePath;
  }

  const filename = imagePath.split('/').pop();

  // Auto-detect folder from stored path: "uploads/{folder}/filename"
  if (!folder) {
    const parts = imagePath.split('/');
    if (parts.length >= 2) {
      folder = parts[parts.length - 2]; // e.g., "images", "media", "posts"
    } else {
      folder = 'posts';
    }
  }

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
  const clientParams = { published: true, ...params };
  // Remove null/undefined values so they are not sent as query params
  Object.keys(clientParams).forEach(key => {
    if (clientParams[key] === null || clientParams[key] === undefined) {
      delete clientParams[key];
    }
  });
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
 * Record a public view for analytics (IP-deduplicated, works for anonymous visitors)
 * @param {string} postUuid - Post UUID
 * @returns {Promise<object>} { counted: boolean }
 */
export const recordPublicView = async (postUuid) => {
  try {
    const response = await axiosPublic.post(`/posts/${postUuid}/view`);
    return response.data;
  } catch {
    // Silently fail — analytics should never block the user
    return { counted: false };
  }
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
 * Get admin-picked breaking posts
 * @param {object} params - { limit }
 * @returns {Promise<object>} Posts list
 */
export const getBreakingPosts = async (params = {}) => {
  const response = await axiosPublic.get('/posts/breaking', { params });
  return response.data;
};

/**
 * Get admin-picked homepage trending posts
 * @param {object} params - { limit }
 * @returns {Promise<object>} Posts list
 */
export const getHomepageTrendingPosts = async (params = {}) => {
  const response = await axiosPublic.get('/posts/homepage-trending', { params });
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
 * @param {string} postSlug - Post slug
 * @param {object} params - { limit }
 * @returns {Promise<object>} Related posts list
 */
export const getRelatedPosts = async (postSlug, params = {}) => {
  const response = await axiosPublic.get(`/posts/${postSlug}/related`, { params });
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
 * Get recent published posts across multiple categories.
 * @param {number[]} categoryIds - Category IDs to query
 * @param {object} params - { limit }
 * @returns {Promise<object>} { posts, total, page, size }
 */
export const getPostsForCategoryIds = async (categoryIds = [], params = {}) => {
  const ids = [...new Set(categoryIds.filter(Boolean))];
  const limit = params.limit || 12;

  if (ids.length === 0) {
    return { posts: [], total: 0, page: 1, size: limit };
  }

  const responses = await Promise.all(
    ids.map((categoryId) =>
      getPosts({
        ...params,
        category_id: categoryId,
        limit,
      })
    )
  );

  const postsByKey = new Map();
  responses.forEach((response) => {
    (response.posts || []).forEach((post) => {
      const key = post.uuid || post.id || post.slug;
      if (key && !postsByKey.has(key)) {
        postsByKey.set(key, post);
      }
    });
  });

  const posts = Array.from(postsByKey.values())
    .sort((a, b) => {
      const dateA = new Date(a.published_at || a.created_at || 0).getTime();
      const dateB = new Date(b.published_at || b.created_at || 0).getTime();
      return dateB - dateA;
    })
    .slice(0, limit);

  return {
    posts,
    total: posts.length,
    page: 1,
    size: limit,
  };
};

/**
 * Get posts by author
 * @param {string} authorUuid - Author UUID
 * @param {object} params - Pagination/filter params
 * @returns {Promise<object>} Posts list
 */
export const getPostsByAuthor = async (authorUuid, params = {}) => {
  const clientParams = { ...params, author_uuid: authorUuid, published: true };
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
 * Upload a featured image for a post (eager upload).
 * Saves to uploads/posts/ so it resolves correctly in getImageUrl.
 * @param {File} file - Image file to upload
 * @param {function} onProgress - Optional progress callback (0-100)
 * @returns {Promise<object>} { file_path, filename }
 */
export const uploadPostImage = async (file, onProgress = null) => {
  const formData = new FormData();
  formData.append('file', file);

  const config = {
    headers: { 'Content-Type': 'multipart/form-data' },
    onUploadProgress: onProgress
      ? (progressEvent) => {
          const pct = Math.round((progressEvent.loaded * 100) / progressEvent.total);
          onProgress(pct);
        }
      : undefined,
  };

  const response = await axiosPrivate.post('/posts/upload-image', formData, config);
  return response.data;
};

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
export const publishPost = async (postUuid, options = {}) => {
  const response = await axiosPrivate.put(`/posts/${postUuid}/publish`, {
    override_quality_gate: Boolean(options.overrideQualityGate),
    override_reason: options.overrideReason || null,
  });
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
 * Add/remove a post from the admin-picked homepage trending carousel
 * @param {string} postUuid - Post UUID
 * @param {boolean} trending - True to add, false to remove
 * @param {number|null} order - Optional slot order from 1-3
 * @returns {Promise<object>} Updated post
 */
export const setHomepageTrending = async (postUuid, trending = true, order = null) => {
  const params = { trending };
  if (order) params.order = order;
  const response = await axiosPrivate.put(`/posts/${postUuid}/homepage-trending`, null, { params });
  return response.data;
};

/**
 * Add/remove a post from the breaking news ticker
 * @param {string} postUuid - Post UUID
 * @param {boolean} breaking - True to add, false to remove
 * @param {number|null} order - Optional manual order
 * @returns {Promise<object>} Updated post
 */
export const setBreakingNews = async (postUuid, breaking = true, order = null) => {
  const params = { breaking };
  if (order) params.order = order;
  const response = await axiosPrivate.put(`/posts/${postUuid}/breaking`, null, { params });
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
