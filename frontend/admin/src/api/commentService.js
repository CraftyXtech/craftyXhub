import { useState, useEffect } from 'react';
import useAxiosPrivate from './useAxiosPrivate';

// Hook to fetch comments for a specific post
export const useGetPostComments = (postUuid, params = {}) => {
  const axiosPrivate = useAxiosPrivate();
  const [comments, setComments] = useState([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (!postUuid) return;

    const fetchComments = async () => {
      try {
        setLoading(true);
        const response = await axiosPrivate.get(`/comments/${postUuid}/comments`, { params });
        setComments(response.data.comments);
        setTotal(response.data.total || response.data.comments?.length || 0);
        setError(null);
      } catch (err) {
        setError(err.response?.data?.detail || err.message);
      } finally {
        setLoading(false);
      }
    };

    fetchComments();
  }, [axiosPrivate, postUuid, JSON.stringify(params)]);

  const refetch = () => {
    const fetchComments = async () => {
      try {
        setLoading(true);
        const response = await axiosPrivate.get(`/comments/${postUuid}/comments`, { params });
        setComments(response.data.comments);
        setTotal(response.data.total || response.data.comments?.length || 0);
        setError(null);
      } catch (err) {
        setError(err.response?.data?.detail || err.message);
      } finally {
        setLoading(false);
      }
    };
    fetchComments();
  };

  return { comments, total, loading, error, refetch };
};

// Hook to approve a comment (admin only)
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

// Hook to create a comment
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

// Hook to update a comment
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

// Hook to delete a comment
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

// Hook to get all pending comments (admin moderation queue)
export const useGetPendingComments = (params = {}) => {
  const axiosPrivate = useAxiosPrivate();
  const [comments, setComments] = useState([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchPendingComments = async () => {
      try {
        setLoading(true);
        // Get all posts to gather their comments and filter pending ones
        // Note: This is a workaround since we don't have a direct pending comments endpoint
        const postsResponse = await axiosPrivate.get('/posts/', { 
          params: { skip: 0, limit: 100, published: true }
        });
        
        const allComments = [];
        
        // Fetch comments for each post
        if (postsResponse.data.posts && postsResponse.data.posts.length > 0) {
          const commentPromises = postsResponse.data.posts.map(async (post) => {
            try {
              const commentsResponse = await axiosPrivate.get(`/comments/${post.uuid}/comments`, {
                params: { skip: 0, limit: 50 }
              });
              return commentsResponse.data.comments?.map(comment => ({
                ...comment,
                post_title: post.title,
                post_uuid: post.uuid
              })) || [];
            } catch (err) {
              return [];
            }
          });
          
          const commentsArrays = await Promise.all(commentPromises);
          commentsArrays.forEach(comments => {
            allComments.push(...comments);
          });
        }
        
        // Filter pending comments (not approved)
        const pendingComments = allComments.filter(comment => !comment.is_approved);
        
        setComments(pendingComments);
        setTotal(pendingComments.length);
        setError(null);
      } catch (err) {
        setError(err.response?.data?.detail || err.message);
      } finally {
        setLoading(false);
      }
    };

    fetchPendingComments();
  }, [axiosPrivate, JSON.stringify(params)]);

  const refetch = () => {
    const fetchPendingComments = async () => {
      try {
        setLoading(true);
        const postsResponse = await axiosPrivate.get('/posts/', { 
          params: { skip: 0, limit: 100, published: true }
        });
        
        const allComments = [];
        
        if (postsResponse.data.posts && postsResponse.data.posts.length > 0) {
          const commentPromises = postsResponse.data.posts.map(async (post) => {
            try {
              const commentsResponse = await axiosPrivate.get(`/comments/${post.uuid}/comments`, {
                params: { skip: 0, limit: 50 }
              });
              return commentsResponse.data.comments?.map(comment => ({
                ...comment,
                post_title: post.title,
                post_uuid: post.uuid
              })) || [];
            } catch (err) {
              return [];
            }
          });
          
          const commentsArrays = await Promise.all(commentPromises);
          commentsArrays.forEach(comments => {
            allComments.push(...comments);
          });
        }
        
        const pendingComments = allComments.filter(comment => !comment.is_approved);
        
        setComments(pendingComments);
        setTotal(pendingComments.length);
        setError(null);
      } catch (err) {
        setError(err.response?.data?.detail || err.message);
      } finally {
        setLoading(false);
      }
    };
    fetchPendingComments();
  };

  return { comments, total, loading, error, refetch };
};