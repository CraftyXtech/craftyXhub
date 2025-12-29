import { useState, useCallback } from 'react';
import useSWR from 'swr';
import {
  getReadingLists,
  getReadingList,
  createReadingList,
  updateReadingList,
  deleteReadingList,
  addPostToList,
  removePostFromList,
  getReadingHistory,
  recordPostView,
  clearReadingHistory,
  getHighlights,
  createHighlight,
  deleteHighlight,
  getUserComments
} from '../services/collectionService';

/**
 * Hook to fetch user's reading lists
 */
export const useReadingLists = () => {
  const { data, error, isLoading, mutate } = useSWR(
    'collection-lists',
    getReadingLists
  );

  return {
    lists: data?.lists || [],
    total: data?.total || 0,
    loading: isLoading,
    error: error?.message,
    refetch: mutate
  };
};

/**
 * Hook to fetch a single reading list with items
 */
export const useReadingList = (uuid) => {
  const { data, error, isLoading, mutate } = useSWR(
    uuid ? `collection-list-${uuid}` : null,
    () => getReadingList(uuid)
  );

  return {
    list: data,
    items: data?.items || [],
    loading: isLoading,
    error: error?.message,
    refetch: mutate
  };
};

/**
 * Hook for reading list operations (create, update, delete)
 */
export const useListOperations = () => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const create = useCallback(async (data) => {
    try {
      setLoading(true);
      setError(null);
      const result = await createReadingList(data);
      return result;
    } catch (err) {
      setError(err.response?.data?.detail || err.message);
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  const update = useCallback(async (uuid, data) => {
    try {
      setLoading(true);
      setError(null);
      const result = await updateReadingList(uuid, data);
      return result;
    } catch (err) {
      setError(err.response?.data?.detail || err.message);
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  const remove = useCallback(async (uuid) => {
    try {
      setLoading(true);
      setError(null);
      await deleteReadingList(uuid);
    } catch (err) {
      setError(err.response?.data?.detail || err.message);
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  const addPost = useCallback(async (listUuid, postUuid, note = null) => {
    try {
      setLoading(true);
      setError(null);
      const result = await addPostToList(listUuid, postUuid, note);
      return result;
    } catch (err) {
      setError(err.response?.data?.detail || err.message);
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  const removePost = useCallback(async (listUuid, postUuid) => {
    try {
      setLoading(true);
      setError(null);
      await removePostFromList(listUuid, postUuid);
    } catch (err) {
      setError(err.response?.data?.detail || err.message);
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  return {
    create,
    update,
    remove,
    addPost,
    removePost,
    loading,
    error
  };
};

/**
 * Hook to fetch reading history
 */
export const useReadingHistory = (skip = 0, limit = 20) => {
  const { data, error, isLoading, mutate } = useSWR(
    `collection-history-${skip}-${limit}`,
    () => getReadingHistory({ skip, limit })
  );

  return {
    entries: data?.entries || [],
    total: data?.total || 0,
    loading: isLoading,
    error: error?.message,
    refetch: mutate
  };
};

/**
 * Hook for reading history operations
 */
export const useHistoryOperations = () => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const record = useCallback(async (postUuid, progress = 0) => {
    try {
      setLoading(true);
      setError(null);
      const result = await recordPostView(postUuid, progress);
      return result;
    } catch (err) {
      setError(err.response?.data?.detail || err.message);
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  const clear = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      await clearReadingHistory();
    } catch (err) {
      setError(err.response?.data?.detail || err.message);
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  return { record, clear, loading, error };
};

/**
 * Hook to fetch highlights
 */
export const useHighlights = (skip = 0, limit = 20) => {
  const { data, error, isLoading, mutate } = useSWR(
    `collection-highlights-${skip}-${limit}`,
    () => getHighlights({ skip, limit })
  );

  return {
    highlights: data?.highlights || [],
    total: data?.total || 0,
    loading: isLoading,
    error: error?.message,
    refetch: mutate
  };
};

/**
 * Hook for highlight operations
 */
export const useHighlightOperations = () => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const create = useCallback(async (data) => {
    try {
      setLoading(true);
      setError(null);
      const result = await createHighlight(data);
      return result;
    } catch (err) {
      setError(err.response?.data?.detail || err.message);
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  const remove = useCallback(async (uuid) => {
    try {
      setLoading(true);
      setError(null);
      await deleteHighlight(uuid);
    } catch (err) {
      setError(err.response?.data?.detail || err.message);
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  return { create, remove, loading, error };
};

/**
 * Hook to fetch user's comments
 */
export const useUserComments = (skip = 0, limit = 20) => {
  const { data, error, isLoading, mutate } = useSWR(
    `user-comments-${skip}-${limit}`,
    () => getUserComments({ skip, limit })
  );

  return {
    comments: data?.comments || [],
    total: data?.total || data?.comments?.length || 0,
    loading: isLoading,
    error: error?.message,
    refetch: mutate
  };
};
