import { axiosPublic, axiosPrivate } from '../axios';

/**
 * Category Service
 * Handles all category-related API operations
 */

/**
 * Get all categories
 * @returns {Promise<object>} { categories }
 */
export const getCategories = async () => {
  const response = await axiosPublic.get('/posts/categories/');
  return response.data.categories || [];
};

/**
 * Get category by slug
 * @param {string} slug - Category slug
 * @returns {Promise<object>} Category with parent info if subcategory
 */
export const getCategoryBySlug = async (slug) => {
  const { data } = await axiosPublic.get('/posts/categories/');
  const categories = data.categories || [];
  
  // Search parents first
  const parent = categories.find((c) => c.slug === slug);
  if (parent) {
    return { ...parent, parent: null, isSubcategory: false };
  }
  
  // Then search subcategories
  for (const c of categories) {
    const match = (c.subcategories || []).find((s) => s.slug === slug);
    if (match) {
      return {
        ...match,
        parent: { id: c.id, name: c.name, slug: c.slug },
        isSubcategory: true,
      };
    }
  }
  
  const err = new Error('Category not found');
  err.status = 404;
  throw err;
};

/**
 * Get category by ID
 * @param {number} categoryId - Category ID
 * @returns {Promise<object|null>} Category or null
 */
export const getCategoryById = async (categoryId) => {
  const { data } = await axiosPublic.get('/posts/categories/');
  const categories = data.categories || [];
  return categories.find((c) => c.id === categoryId) || null;
};

/**
 * Create a new category (admin only)
 * @param {object} categoryData - { name, slug?, description?, parent_id? }
 * @returns {Promise<object>} Created category
 */
export const createCategory = async (categoryData) => {
  if (!categoryData.name?.trim()) {
    throw new Error('Category name is required');
  }
  
  const payload = {
    ...categoryData,
    parent_id: categoryData.parent_id ? parseInt(categoryData.parent_id, 10) : null,
  };
  
  const response = await axiosPrivate.post('/posts/categories/', payload);
  return response.data;
};

/**
 * Update a category (admin only)
 * @param {number} categoryId - Category ID
 * @param {object} categoryData - Category data to update
 * @returns {Promise<object>} Updated category
 */
export const updateCategory = async (categoryId, categoryData) => {
  if (!categoryData.name?.trim()) {
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
};

/**
 * Delete a category (admin only)
 * @param {number} categoryId - Category ID
 * @returns {Promise<void>}
 */
export const deleteCategory = async (categoryId) => {
  await axiosPrivate.delete(`/posts/categories/${categoryId}`);
};

/**
 * Get category statistics
 * @returns {Promise<object>} { totalCategories, parentCategories, subcategories, totalPosts }
 */
export const getCategoryStats = async () => {
  const { data } = await axiosPrivate.get('/posts/categories/');
  const categories = data.categories || [];
  
  const parentCategories = categories.filter(cat => !cat.parent_id);
  const subcategories = categories.filter(cat => cat.parent_id);
  const totalPosts = categories.reduce((sum, cat) => sum + (cat.post_count || 0), 0);
  
  return {
    totalCategories: categories.length,
    parentCategories: parentCategories.length,
    subcategories: subcategories.length,
    totalPosts,
  };
};

/**
 * Validate category slug uniqueness
 * @param {string} slug - Slug to validate
 * @param {number|null} excludeId - Category ID to exclude (for updates)
 * @returns {Promise<object>} { isValid, exists, message }
 */
export const validateCategorySlug = async (slug, excludeId = null) => {
  const { data } = await axiosPublic.get('/posts/categories/');
  const categories = data.categories || [];
  
  const existingCategory = categories.find(
    cat => cat.slug === slug && cat.id !== excludeId
  );
  
  return {
    isValid: !existingCategory,
    exists: !!existingCategory,
    message: existingCategory ? 'Slug already exists' : 'Slug is available',
  };
};
