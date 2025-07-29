import { useState, useEffect } from 'react';
import useAxiosPrivate from './useAxiosPrivate';  

// Hook to fetch posts with pagination and filters
export const useGetPosts = (params = {}) => {
  const axiosPrivate = useAxiosPrivate(); 
  const [posts, setPosts] = useState([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [size, setSize] = useState(10);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchPosts = async () => {
      try {
        setLoading(true);
        const response = await axiosPrivate.get('/posts/', { params }); 
        setPosts(response.data.posts);
        setTotal(response.data.total);
        setPage(response.data.page);
        setSize(response.data.size);
        setError(null);
      } catch (err) {
        setError(err.response?.data?.detail || err.message);
      } finally {
        setLoading(false);
      }
    };

    fetchPosts();
  }, [axiosPrivate, JSON.stringify(params)]);

  return { posts, total, page, size, loading, error, refetch: () => fetchPosts() };
};

// Hook to fetch a single post by ID
export const useGetPost = (postId) => {
  const axiosPrivate = useAxiosPrivate();
  const [post, setPost] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (!postId) return;

    const fetchPost = async () => {
      try {
        setLoading(true);
        const response = await axiosPrivate.get(`/posts/${postId}`);
        setPost(response.data);
        setError(null);
      } catch (err) {
        setError(err.response?.data?.detail || err.message);
      } finally {
        setLoading(false);
      }
    };

    fetchPost();
  }, [axiosPrivate, postId]);

  return { post, loading, error };
};

// Hook to create a new post
export const useCreatePost = () => {
  const axiosPrivate = useAxiosPrivate();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const createPost = async (formData) => {
      try {
      setLoading(true);
      setError(null);
      
      // Check if formData is FormData object (for file uploads) or regular object
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

// Hook to update a post
export const useUpdatePost = () => {
  const axiosPrivate = useAxiosPrivate();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const updatePost = async (postId, formData) => {
      try {
      setLoading(true);
      setError(null);
      
      // Check if formData is FormData object (for file uploads) or regular object
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

// Hook to delete a post
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

// Hook to toggle post like
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

// Hook to fetch categories
export const useGetCategories = () => {
  const axiosPrivate = useAxiosPrivate();
  const [categories, setCategories] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchCategories = async () => {
      try {
        setLoading(true);
        const response = await axiosPrivate.get('/posts/categories/');
        setCategories(response.data.categories || []);
        setError(null);
      } catch (err) {
        setError(err.response?.data?.detail || err.message);
      } finally {
        setLoading(false);
      }
    };

    fetchCategories();
  }, [axiosPrivate]);

  return { categories, loading, error, refetch: () => fetchCategories() };
};

// Hook to create a category
export const useCreateCategory = () => {
  const axiosPrivate = useAxiosPrivate();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const createCategory = async (categoryData) => {
    try {
      setLoading(true);
      setError(null);
      const response = await axiosPrivate.post('/posts/categories/', categoryData);
        return response.data;
    } catch (err) {
      setError(err.response?.data?.detail || err.message);
      throw err;
    } finally {
      setLoading(false);
      }
  };

  return { createCategory, loading, error };
};

// Hook to fetch tags
export const useGetTags = () => {
  const axiosPrivate = useAxiosPrivate();
  const [tags, setTags] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchTags = async () => {
      try {
        setLoading(true);
        const response = await axiosPrivate.get('/posts/tags/');
        setTags(response.data.tags || []);
        setError(null);
      } catch (err) {
        setError(err.response?.data?.detail || err.message);
      } finally {
        setLoading(false);
      }
    };

    fetchTags();
  }, [axiosPrivate]);

  return { tags, loading, error, refetch: () => fetchTags() };
};

// Hook to create a tag
export const useCreateTag = () => {
  const axiosPrivate = useAxiosPrivate();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const createTag = async (tagData) => {
    try {
      setLoading(true);
      setError(null);
      const response = await axiosPrivate.post('/posts/tags/', tagData);
      return response.data;
    } catch (err) {
      setError(err.response?.data?.detail || err.message);
      throw err;
    } finally {
      setLoading(false);
    }
  };

  return { createTag, loading, error };
};

// Hook to fetch post statistics
export const useGetPostStats = () => {
  const axiosPrivate = useAxiosPrivate();
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchStats = async () => {
      try {
        setLoading(true);
        const response = await axiosPrivate.get('/posts/stats/');
        setStats(response.data);
        setError(null);
      } catch (err) {
        setError(err.response?.data?.detail || err.message);
      } finally {
        setLoading(false);
      }
    };

    fetchStats();
  }, [axiosPrivate]);

  return { stats, loading, error, refetch: () => fetchStats() };
};

// Hook to publish a post
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

// Hook to unpublish a post
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

// Hook to feature/unfeature a post
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

// Hook to get image URL from backend path
export const useImageUrl = () => {
  const getImageUrl = (imagePath) => {
    if (!imagePath) return "";
    if (imagePath.startsWith('http')) return imagePath;
    if (imagePath.startsWith('uploads/images/')) {
      const filename = imagePath.split('/').pop();
      // For image display, we need the full URL
      const baseUrl = import.meta.env.VITE_APP_API_URL || 'http://127.0.0.1:8000/v1';
      return `${baseUrl}/posts/images/${filename}`;
    }
    return imagePath;
  };

  return { getImageUrl };
};