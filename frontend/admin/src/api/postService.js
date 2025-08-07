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

// Enhanced hook to fetch categories with better error handling
export const useGetCategories = () => {
  const axiosPrivate = useAxiosPrivate();
  const [categories, setCategories] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchCategories = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await axiosPrivate.get('/posts/categories/');
      setCategories(response.data.categories || []);
    } catch (err) {
      setError(err.response?.data?.detail || err.message);
      console.error('Error fetching categories:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchCategories();
  }, [axiosPrivate]);

  return { 
    categories, 
    loading, 
    error, 
    refetch: fetchCategories,
    // Helper functions
    getParentCategories: () => categories.filter(cat => !cat.parent_id),
    getSubcategories: () => categories.filter(cat => cat.parent_id),
    getCategoryById: (id) => categories.find(cat => cat.id === id),
    getCategoryBySlug: (slug) => categories.find(cat => cat.slug === slug)
  };
};

// Enhanced hook to create a category with validation
export const useCreateCategory = () => {
  const axiosPrivate = useAxiosPrivate();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const createCategory = async (categoryData) => {
    try {
      setLoading(true);
      setError(null);
      
      // Validate required fields
      if (!categoryData.name || !categoryData.name.trim()) {
        throw new Error('Category name is required');
      }

      // Normalize parent_id
      const payload = {
        ...categoryData,
        parent_id: categoryData.parent_id ? parseInt(categoryData.parent_id, 10) : null,
      };

      const response = await axiosPrivate.post('/posts/categories/', payload);
      return response.data;
    } catch (err) {
      const errorMessage = err.response?.data?.detail || err.message || 'Failed to create category';
      setError(errorMessage);
      throw new Error(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  return { createCategory, loading, error, clearError: () => setError(null) };
};

// Enhanced hook to update a category with validation
export const useUpdateCategory = () => {
  const axiosPrivate = useAxiosPrivate();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const updateCategory = async (categoryId, categoryData) => {
    try {
      setLoading(true);
      setError(null);
      
      // Validate required fields
      if (!categoryData.name || !categoryData.name.trim()) {
        throw new Error('Category name is required');
      }

      // Prevent circular reference
      if (categoryData.parent_id && parseInt(categoryData.parent_id, 10) === categoryId) {
        throw new Error('Category cannot be its own parent');
      }

      const payload = {
        ...categoryData,
        parent_id: categoryData.parent_id ? parseInt(categoryData.parent_id, 10) : null,
      };

      const response = await axiosPrivate.put(`/posts/categories/${categoryId}`, payload);
      return response.data;
    } catch (err) {
      const errorMessage = err.response?.data?.detail || err.message || 'Failed to update category';
      setError(errorMessage);
      throw new Error(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  return { updateCategory, loading, error, clearError: () => setError(null) };
};

// Enhanced hook to delete a category with validation
export const useDeleteCategory = () => {
  const axiosPrivate = useAxiosPrivate();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const deleteCategory = async (categoryId) => {
    try {
      setLoading(true);
      setError(null);

      // Directly request deletion; backend enforces constraints and returns proper errors
      await axiosPrivate.delete(`/posts/categories/${categoryId}`);
    } catch (err) {
      const errorMessage = err.response?.data?.detail || err.message || 'Failed to delete category';
      setError(errorMessage);
      throw new Error(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  return { deleteCategory, loading, error, clearError: () => setError(null) };
};

// New hook to get category statistics
export const useGetCategoryStats = () => {
  const axiosPrivate = useAxiosPrivate();
  const [stats, setStats] = useState({
    totalCategories: 0,
    parentCategories: 0,
    subcategories: 0,
    totalPosts: 0
  });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchStats = async () => {
    try {
      setLoading(true);
      setError(null);
      
      // Get categories to calculate stats
      const response = await axiosPrivate.get('/posts/categories/');
      const categories = response.data.categories || [];
      
      const parentCategories = categories.filter(cat => !cat.parent_id);
      const subcategories = categories.filter(cat => cat.parent_id);
      const totalPosts = categories.reduce((sum, cat) => sum + (cat.post_count || 0), 0);
      
      setStats({
        totalCategories: categories.length,
        parentCategories: parentCategories.length,
        subcategories: subcategories.length,
        totalPosts
      });
    } catch (err) {
      setError(err.response?.data?.detail || err.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchStats();
  }, [axiosPrivate]);

  return { stats, loading, error, refetch: fetchStats };
};

// New hook to validate category slug
export const useValidateCategorySlug = () => {
  const axiosPrivate = useAxiosPrivate();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const validateSlug = async (slug, excludeId = null) => {
    try {
      setLoading(true);
      setError(null);
      
      // Check if slug exists
      const response = await axiosPrivate.get(`/posts/categories/`);
      const categories = response.data.categories || [];
      
      const existingCategory = categories.find(cat => 
        cat.slug === slug && cat.id !== excludeId
      );
      
      return {
        isValid: !existingCategory,
        exists: !!existingCategory,
        message: existingCategory ? 'Slug already exists' : 'Slug is available'
      };
    } catch (err) {
      setError(err.response?.data?.detail || err.message);
      return { isValid: false, exists: false, message: 'Error validating slug' };
    } finally {
      setLoading(false);
    }
  };

  return { validateSlug, loading, error, clearError: () => setError(null) };
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