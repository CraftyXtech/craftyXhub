import { useState, useEffect, useCallback } from 'react';
import useAxiosPrivate from './useAxiosPrivate';
import { getCategories, getCategoryStats, validateCategorySlug } from '../services/categoryService';

/**
 * Hook to fetch categories
 */
export const useGetCategories = () => {
  const axiosPrivate = useAxiosPrivate();
  const [categories, setCategories] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchCategories = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await getCategories();
      setCategories(data.categories || []);
    } catch (err) {
      setError(err.response?.data?.detail || err.message);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchCategories();
  }, [fetchCategories]);

  // Helper functions
  const getParentCategories = () => categories.filter(cat => !cat.parent_id);
  const getSubcategories = () => categories.filter(cat => cat.parent_id);
  const getCategoryById = (id) => categories.find(cat => cat.id === id);
  const getCategoryBySlug = (slug) => categories.find(cat => cat.slug === slug);

  return { 
    categories, 
    loading, 
    error, 
    refetch: fetchCategories,
    getParentCategories,
    getSubcategories,
    getCategoryById,
    getCategoryBySlug,
  };
};

/**
 * Hook to create a category
 */
export const useCreateCategory = () => {
  const axiosPrivate = useAxiosPrivate();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const createCategory = async (categoryData) => {
    try {
      setLoading(true);
      setError(null);
      
      if (!categoryData.name?.trim()) {
        throw new Error('Category name is required');
      }
      
      const payload = {
        ...categoryData,
        parent_id: categoryData.parent_id ? parseInt(categoryData.parent_id, 10) : null,
      };
      
      const response = await axiosPrivate.post('/posts/categories/', payload);
      return response.data;
    } catch (err) {
      const errorMessage = err.response?.data?.detail || err.message;
      setError(errorMessage);
      throw new Error(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  return { createCategory, loading, error, clearError: () => setError(null) };
};

/**
 * Hook to update a category
 */
export const useUpdateCategory = () => {
  const axiosPrivate = useAxiosPrivate();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const updateCategory = async (categoryId, categoryData) => {
    try {
      setLoading(true);
      setError(null);
      
      if (!categoryData.name?.trim()) {
        throw new Error('Category name is required');
      }
      
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
      const errorMessage = err.response?.data?.detail || err.message;
      setError(errorMessage);
      throw new Error(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  return { updateCategory, loading, error, clearError: () => setError(null) };
};

/**
 * Hook to delete a category
 */
export const useDeleteCategory = () => {
  const axiosPrivate = useAxiosPrivate();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const deleteCategory = async (categoryId) => {
    try {
      setLoading(true);
      setError(null);
      await axiosPrivate.delete(`/posts/categories/${categoryId}`);
    } catch (err) {
      const errorMessage = err.response?.data?.detail || err.message;
      setError(errorMessage);
      throw new Error(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  return { deleteCategory, loading, error, clearError: () => setError(null) };
};

/**
 * Hook to get category statistics
 */
export const useGetCategoryStats = () => {
  const [stats, setStats] = useState({
    totalCategories: 0,
    parentCategories: 0,
    subcategories: 0,
    totalPosts: 0,
  });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchStats = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await getCategoryStats();
      setStats(data);
    } catch (err) {
      setError(err.response?.data?.detail || err.message);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchStats();
  }, [fetchStats]);

  return { stats, loading, error, refetch: fetchStats };
};

/**
 * Hook to validate category slug
 */
export const useValidateCategorySlug = () => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const validateSlug = async (slug, excludeId = null) => {
    try {
      setLoading(true);
      setError(null);
      return await validateCategorySlug(slug, excludeId);
    } catch (err) {
      setError(err.response?.data?.detail || err.message);
      return { isValid: false, exists: false, message: 'Error validating slug' };
    } finally {
      setLoading(false);
    }
  };

  return { validateSlug, loading, error, clearError: () => setError(null) };
};
