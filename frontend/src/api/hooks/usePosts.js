import { useState, useEffect, useCallback } from 'react';
import useAxiosPrivate from './useAxiosPrivate';
import { 
  getPosts, getPost, getPopularPosts, getRecentPosts, 
  getTrendingPosts, getFeaturedPosts, getRelatedPosts,
  getPostsByCategory, getPostsByAuthor, getPostStats,
  getImageUrl 
} from '../services/postService';

/**
 * Hook to fetch posts with pagination and filters
 */
export const useGetPosts = (params = {}) => {
  const axiosPrivate = useAxiosPrivate();
  const [posts, setPosts] = useState([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [size, setSize] = useState(10);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchPosts = useCallback(async () => {
    try {
      setLoading(true);
      const data = await getPosts(params);
      setPosts(data.posts || []);
      setTotal(data.total || 0);
      setPage(data.page || 1);
      setSize(data.size || 10);
      setError(null);
    } catch (err) {
      setError(err.response?.data?.detail || err.message);
    } finally {
      setLoading(false);
    }
  }, [JSON.stringify(params)]);

  useEffect(() => {
    fetchPosts();
  }, [fetchPosts]);

  return { posts, total, page, size, loading, error, refetch: fetchPosts };
};

/**
 * Hook to fetch a single post
 */
export const useGetPost = (postId) => {
  const [post, setPost] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (!postId) return;

    const fetchPost = async () => {
      try {
        setLoading(true);
        const data = await getPost(postId);
        setPost(data);
        setError(null);
      } catch (err) {
        setError(err.response?.data?.detail || err.message);
      } finally {
        setLoading(false);
      }
    };

    fetchPost();
  }, [postId]);

  return { post, loading, error };
};

/**
 * Hook to create a new post
 */
export const useCreatePost = () => {
  const axiosPrivate = useAxiosPrivate();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const createPost = async (formData) => {
    try {
      setLoading(true);
      setError(null);
      
      const isFormData = formData instanceof FormData;
      const headers = isFormData ? { 'Content-Type': 'multipart/form-data' } : {};
      
      const response = await axiosPrivate.post('/posts/', formData, { headers });
      return response.data;
    } catch (err) {
      setError(err.response?.data?.detail || err.message);
      throw err;
    } finally {
      setLoading(false);
    }
  };

  return { createPost, loading, error };
};

/**
 * Hook to update a post
 */
export const useUpdatePost = () => {
  const axiosPrivate = useAxiosPrivate();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const updatePost = async (postId, formData) => {
    try {
      setLoading(true);
      setError(null);
      
      const isFormData = formData instanceof FormData;
      const headers = isFormData ? { 'Content-Type': 'multipart/form-data' } : {};
      
      const response = await axiosPrivate.put(`/posts/${postId}`, formData, { headers });
      return response.data;
    } catch (err) {
      setError(err.response?.data?.detail || err.message);
      throw err;
    } finally {
      setLoading(false);
    }
  };

  return { updatePost, loading, error };
};

/**
 * Hook to delete a post
 */
export const useDeletePost = () => {
  const axiosPrivate = useAxiosPrivate();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const deletePost = async (postId) => {
    try {
      setLoading(true);
      setError(null);
      await axiosPrivate.delete(`/posts/${postId}`);
      return true;
    } catch (err) {
      setError(err.response?.data?.detail || err.message);
      throw err;
    } finally {
      setLoading(false);
    }
  };

  return { deletePost, loading, error };
};

/**
 * Hook to toggle post like
 */
export const useTogglePostLike = () => {
  const axiosPrivate = useAxiosPrivate();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const toggleLike = async (postId) => {
    try {
      setLoading(true);
      setError(null);
      const response = await axiosPrivate.post(`/posts/${postId}/like`);
      return response.data;
    } catch (err) {
      setError(err.response?.data?.detail || err.message);
      throw err;
    } finally {
      setLoading(false);
    }
  };

  return { toggleLike, loading, error };
};

/**
 * Hook to publish a post
 */
export const usePublishPost = () => {
  const axiosPrivate = useAxiosPrivate();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const publishPost = async (postId) => {
    try {
      setLoading(true);
      setError(null);
      const response = await axiosPrivate.put(`/posts/${postId}/publish`);
      return response.data;
    } catch (err) {
      setError(err.response?.data?.detail || err.message);
      throw err;
    } finally {
      setLoading(false);
    }
  };

  return { publishPost, loading, error };
};

/**
 * Hook to unpublish a post
 */
export const useUnpublishPost = () => {
  const axiosPrivate = useAxiosPrivate();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const unpublishPost = async (postId) => {
    try {
      setLoading(true);
      setError(null);
      const response = await axiosPrivate.put(`/posts/${postId}/unpublish`);
      return response.data;
    } catch (err) {
      setError(err.response?.data?.detail || err.message);
      throw err;
    } finally {
      setLoading(false);
    }
  };

  return { unpublishPost, loading, error };
};

/**
 * Hook to feature/unfeature a post
 */
export const useFeaturePost = () => {
  const axiosPrivate = useAxiosPrivate();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const featurePost = async (postId, feature = true) => {
    try {
      setLoading(true);
      setError(null);
      const response = await axiosPrivate.put(`/posts/${postId}/feature?feature=${feature}`);
      return response.data;
    } catch (err) {
      setError(err.response?.data?.detail || err.message);
      throw err;
    } finally {
      setLoading(false);
    }
  };

  return { featurePost, loading, error };
};

/**
 * Hook to fetch post statistics
 */
export const useGetPostStats = () => {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchStats = async () => {
      try {
        setLoading(true);
        const data = await getPostStats();
        setStats(data);
        setError(null);
      } catch (err) {
        setError(err.response?.data?.detail || err.message);
      } finally {
        setLoading(false);
      }
    };

    fetchStats();
  }, []);

  return { stats, loading, error };
};

/**
 * Hook to get image URL
 */
export const useImageUrl = () => {
  return { getImageUrl };
};
