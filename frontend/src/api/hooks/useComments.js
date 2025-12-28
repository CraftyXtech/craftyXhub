import { useState, useEffect, useCallback } from 'react';
import useAxiosPrivate from './useAxiosPrivate';
import { getComments } from '../services/commentService';

/**
 * Hook to fetch comments for a post
 */
export const useGetPostComments = (postUuid, params = {}) => {
  const axiosPrivate = useAxiosPrivate();
  const [comments, setComments] = useState([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchComments = useCallback(async () => {
    if (!postUuid) return;
    
    try {
      setLoading(true);
      const data = await getComments(postUuid, params);
      setComments(data.comments || []);
      setTotal(data.total || data.comments?.length || 0);
      setError(null);
    } catch (err) {
      setError(err.response?.data?.detail || err.message);
    } finally {
      setLoading(false);
    }
  }, [postUuid, JSON.stringify(params)]);

  useEffect(() => {
    fetchComments();
  }, [fetchComments]);

  return { comments, total, loading, error, refetch: fetchComments };
};

/**
 * Hook to create a comment
 */
export const useCreateComment = () => {
  const axiosPrivate = useAxiosPrivate();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const createComment = async (postUuid, commentData) => {
    try {
      setLoading(true);
      setError(null);
      const response = await axiosPrivate.post(`/comments/${postUuid}/comments`, commentData);
      return response.data;
    } catch (err) {
      setError(err.response?.data?.detail || err.message);
      throw err;
    } finally {
      setLoading(false);
    }
  };

  return { createComment, loading, error };
};

/**
 * Hook to update a comment
 */
export const useUpdateComment = () => {
  const axiosPrivate = useAxiosPrivate();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const updateComment = async (commentUuid, commentData) => {
    try {
      setLoading(true);
      setError(null);
      const response = await axiosPrivate.put(`/comments/${commentUuid}`, commentData);
      return response.data;
    } catch (err) {
      setError(err.response?.data?.detail || err.message);
      throw err;
    } finally {
      setLoading(false);
    }
  };

  return { updateComment, loading, error };
};

/**
 * Hook to delete a comment
 */
export const useDeleteComment = () => {
  const axiosPrivate = useAxiosPrivate();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const deleteComment = async (commentUuid) => {
    try {
      setLoading(true);
      setError(null);
      const response = await axiosPrivate.delete(`/comments/${commentUuid}`);
      return response.data;
    } catch (err) {
      setError(err.response?.data?.detail || err.message);
      throw err;
    } finally {
      setLoading(false);
    }
  };

  return { deleteComment, loading, error };
};

/**
 * Hook to approve a comment (admin only)
 */
export const useApproveComment = () => {
  const axiosPrivate = useAxiosPrivate();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const approveComment = async (commentUuid) => {
    try {
      setLoading(true);
      setError(null);
      const response = await axiosPrivate.put(`/comments/${commentUuid}/approve`);
      return response.data;
    } catch (err) {
      setError(err.response?.data?.detail || err.message);
      throw err;
    } finally {
      setLoading(false);
    }
  };

  return { approveComment, loading, error };
};
