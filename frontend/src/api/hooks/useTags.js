import { useState, useEffect, useCallback } from 'react';
import useAxiosPrivate from './useAxiosPrivate';
import { getTags } from '../services/tagService';

/**
 * Hook to fetch tags
 */
export const useGetTags = () => {
  const axiosPrivate = useAxiosPrivate();
  const [tags, setTags] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchTags = useCallback(async () => {
    try {
      setLoading(true);
      const data = await getTags();
      setTags(data.tags || []);
      setError(null);
    } catch (err) {
      setError(err.response?.data?.detail || err.message);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchTags();
  }, [fetchTags]);

  return { tags, loading, error, refetch: fetchTags };
};

/**
 * Hook to create a tag
 */
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

/**
 * Hook to update a tag
 */
export const useUpdateTag = () => {
  const axiosPrivate = useAxiosPrivate();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const updateTag = async (tagId, tagData) => {
    try {
      setLoading(true);
      setError(null);
      const response = await axiosPrivate.put(`/posts/tags/${tagId}`, tagData);
      return response.data;
    } catch (err) {
      setError(err.response?.data?.detail || err.message);
      throw err;
    } finally {
      setLoading(false);
    }
  };

  return { updateTag, loading, error };
};

/**
 * Hook to delete a tag
 */
export const useDeleteTag = () => {
  const axiosPrivate = useAxiosPrivate();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const deleteTag = async (tagId) => {
    try {
      setLoading(true);
      setError(null);
      await axiosPrivate.delete(`/posts/tags/${tagId}`);
    } catch (err) {
      setError(err.response?.data?.detail || err.message);
      throw err;
    } finally {
      setLoading(false);
    }
  };

  return { deleteTag, loading, error };
};
