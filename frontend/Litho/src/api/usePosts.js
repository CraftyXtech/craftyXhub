import { useState, useEffect, useCallback } from 'react';
import {
    getPosts,
    getPost,
    getPostImage,
    togglePostLike,
    getPostStats,
    getPostsByCategory,
    getPostsByAuthor,
    getPopularPosts,
    getRecentPosts,
    getRelatedPosts,
    getCategories,
    getTags,
    getProfile,
    createProfile,
    updateProfile,
    deleteProfile,
    getComments,
    getComment,
    createComment,
    updateComment,
    deleteComment,
    toggleCommentLike,
    reportComment
} from './postsService';

// Hook to get all posts with optional filters
export const usePosts = (params = {}) => {
    const [posts, setPosts] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    const fetchPosts = useCallback(async () => {
        try {
            setLoading(true);
            const data = await getPosts(params);
            setPosts(Array.isArray(data.posts) ? data.posts : []);
            setError(null);
        } catch (err) {
            setError(err.response?.data?.detail || err.message);
            setPosts([]);
        } finally {
            setLoading(false);
        }
    }, [JSON.stringify(params)]);

    useEffect(() => {
        fetchPosts();
    }, [fetchPosts]);

    return { posts, loading, error, refetch: fetchPosts };
};

// Hook to get a single post
export const usePost = (postUuid) => {
    const [post, setPost] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        if (!postUuid) {
            setPost(null);
            setLoading(false);
            return;
        }

        const fetchPost = async () => {
            try {
                setLoading(true);
                const data = await getPost(postUuid);
                setPost(data);
                setError(null);
            } catch (err) {
                setError(err.response?.data?.detail || err.message);
                setPost(null);
            } finally {
                setLoading(false);
            }
        };

        fetchPost();
    }, [postUuid]);

    return { post, loading, error };
};

// Hook to get posts by category
export const usePostsByCategory = (categoryId, params = {}) => {
    const [posts, setPosts] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    const fetchPostsByCategory = useCallback(async () => {
        if (!categoryId) {
            setPosts([]);
            setLoading(false);
            return;
        }

        try {
            setLoading(true);
            const data = await getPostsByCategory(categoryId, params);
            setPosts(Array.isArray(data.posts) ? data.posts : []);
            setError(null);
        } catch (err) {
            setError(err.response?.data?.detail || err.message);
            setPosts([]);
        } finally {
            setLoading(false);
        }
    }, [categoryId, JSON.stringify(params)]);

    useEffect(() => {
        fetchPostsByCategory();
    }, [fetchPostsByCategory]);

    return { posts, loading, error, refetch: fetchPostsByCategory };
};

// Hook to get posts by author
export const usePostsByAuthor = (authorId, params = {}) => {
    const [posts, setPosts] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    const fetchPostsByAuthor = useCallback(async () => {
        if (!authorId) {
            setPosts([]);
            setLoading(false);
            return;
        }

        try {
            setLoading(true);
            const data = await getPostsByAuthor(authorId, params);
            setPosts(Array.isArray(data.posts) ? data.posts : []);
            setError(null);
        } catch (err) {
            setError(err.response?.data?.detail || err.message);
            setPosts([]);
        } finally {
            setLoading(false);
        }
    }, [authorId, JSON.stringify(params)]);

    useEffect(() => {
        fetchPostsByAuthor();
    }, [fetchPostsByAuthor]);

    return { posts, loading, error, refetch: fetchPostsByAuthor };
};

// Hook to get post statistics
export const usePostStats = () => {
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
                setStats(null);
            } finally {
                setLoading(false);
            }
        };

        fetchStats();
    }, []);

    return { stats, loading, error };
};

// Hook to get popular posts
export const usePopularPosts = (params = {}) => {
    const [posts, setPosts] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    const fetchPopularPosts = useCallback(async () => {
        try {
            setLoading(true);
            const data = await getPopularPosts(params);
            setPosts(Array.isArray(data.posts) ? data.posts : []);
            setError(null);
        } catch (err) {
            setError(err.response?.data?.detail || err.message);
            setPosts([]);
        } finally {
            setLoading(false);
        }
    }, [JSON.stringify(params)]);

    useEffect(() => {
        fetchPopularPosts();
    }, [fetchPopularPosts]);

    return { posts, loading, error, refetch: fetchPopularPosts };
};

export const useCategories = () => {
    const [categories, setCategories] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    const fetchCategories = useCallback(async () => {
        try {
            setLoading(true);
            const data = await getCategories();
            setCategories(data.categories || []);
            setError(null);
        } catch (err) {
            setError(err.response?.data?.detail || err.message);
            setCategories([]);
        } finally {
            setLoading(false);
        }
    }, []);

    useEffect(() => {
        fetchCategories();
    }, [fetchCategories]);

    return { categories, loading, error, refetch: fetchCategories };
};

export const useTags = () => {
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
            setTags([]);
        } finally {
            setLoading(false);
        }
    }, []);

    useEffect(() => {
        fetchTags();
    }, [fetchTags]);

    return { tags, loading, error, refetch: fetchTags };
};

export const useRecentPosts = (params = {}) => {
    const [posts, setPosts] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    const fetchRecentPosts = useCallback(async () => {
        try {
            setLoading(true);
            const data = await getRecentPosts(params);
            setPosts(data.posts || []);
            setError(null);
        } catch (err) {
            setError(err.response?.data?.detail || err.message);
            setPosts([]);
        } finally {
            setLoading(false);
        }
    }, [JSON.stringify(params)]);

    useEffect(() => {
        fetchRecentPosts();
    }, [fetchRecentPosts]);

    return { posts, loading, error, refetch: fetchRecentPosts };
};

export const useProfile = (userUuid) => {
    const [profile, setProfile] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        if (!userUuid) {
            setProfile(null);
            setLoading(false);
            return;
        }

        const fetchProfile = async () => {
            try {
                setLoading(true);
                const data = await getProfile(userUuid);
                setProfile(data);
                setError(null);
            } catch (err) {
                setError(err.response?.data?.detail || err.message);
                setProfile(null);
            } finally {
                setLoading(false);
            }
        };

        fetchProfile();
    }, [userUuid]);

    return { profile, loading, error };
};

// Hook to get related posts based on current post
export const useRelatedPosts = (postUuid, options = { limit: 3 }) => {
    const [relatedPosts, setRelatedPosts] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        if (!postUuid) {
            console.log('useRelatedPosts: No postUuid provided');
            setLoading(false);
            return;
        }

        const fetchRelatedPosts = async () => {
            try {
                console.log('useRelatedPosts: Fetching related posts for', postUuid);
                setLoading(true);
                setError(null);

                // Use the dedicated related posts endpoint
                const response = await getRelatedPosts(postUuid, { limit: options.limit });
                console.log('useRelatedPosts: Response from /related endpoint', response);
                
                setRelatedPosts(response.posts || []);
                console.log('useRelatedPosts: Set related posts', response.posts || []);
            } catch (err) {
                console.error('useRelatedPosts: Error fetching related posts', err);
                setError(err.response?.data?.detail || err.message || 'Failed to fetch related posts');
                setRelatedPosts([]);
            } finally {
                setLoading(false);
            }
        };

        fetchRelatedPosts();
    }, [postUuid, options.limit]);

    return { relatedPosts, loading, error };
};

// ===== COMMENTS HOOKS =====

// Hook to get comments for a post
export const useComments = (postUuid, params = {}) => {
    const [comments, setComments] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [totalComments, setTotalComments] = useState(0);

    const fetchComments = useCallback(async () => {
        if (!postUuid) {
            setLoading(false);
            return;
        }

        try {
            setLoading(true);
            setError(null);
            
            const response = await getComments({
                post_uuid: postUuid,
                ...params
            });
            
            setComments(response.comments || []);
            setTotalComments(response.total || 0);
        } catch (err) {
            console.error('Error fetching comments:', err);
            setError(err.response?.data?.detail || err.message || 'Failed to fetch comments');
            setComments([]);
        } finally {
            setLoading(false);
        }
    }, [postUuid, params]);

    useEffect(() => {
        fetchComments();
    }, [fetchComments]);

    // Function to refresh comments (useful after creating/updating/deleting)
    const refreshComments = useCallback(() => {
        fetchComments();
    }, [fetchComments]);

    return { comments, loading, error, totalComments, refreshComments };
};

// Hook to create a new comment
export const useCreateComment = () => {
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);

    const createNewComment = useCallback(async (commentData) => {
        try {
            setLoading(true);
            setError(null);
            
            const response = await createComment(commentData);
            return response;
        } catch (err) {
            console.error('Error creating comment:', err);
            const errorMessage = err.response?.data?.detail || err.message || 'Failed to create comment';
            setError(errorMessage);
            throw new Error(errorMessage);
        } finally {
            setLoading(false);
        }
    }, []);

    return { createNewComment, loading, error };
};

// Hook to update a comment
export const useUpdateComment = () => {
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);

    const updateExistingComment = useCallback(async (commentUuid, commentData) => {
        try {
            setLoading(true);
            setError(null);
            
            const response = await updateComment(commentUuid, commentData);
            return response;
        } catch (err) {
            console.error('Error updating comment:', err);
            const errorMessage = err.response?.data?.detail || err.message || 'Failed to update comment';
            setError(errorMessage);
            throw new Error(errorMessage);
        } finally {
            setLoading(false);
        }
    }, []);

    return { updateExistingComment, loading, error };
};

// Hook to delete a comment
export const useDeleteComment = () => {
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);

    const deleteExistingComment = useCallback(async (commentUuid) => {
        try {
            setLoading(true);
            setError(null);
            
            const response = await deleteComment(commentUuid);
            return response;
        } catch (err) {
            console.error('Error deleting comment:', err);
            const errorMessage = err.response?.data?.detail || err.message || 'Failed to delete comment';
            setError(errorMessage);
            throw new Error(errorMessage);
        } finally {
            setLoading(false);
        }
    }, []);

    return { deleteExistingComment, loading, error };
};

// Hook to toggle comment like
export const useCommentLike = () => {
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);

    const toggleLike = useCallback(async (commentUuid) => {
        try {
            setLoading(true);
            setError(null);
            
            const response = await toggleCommentLike(commentUuid);
            return response;
        } catch (err) {
            console.error('Error toggling comment like:', err);
            const errorMessage = err.response?.data?.detail || err.message || 'Failed to toggle like';
            setError(errorMessage);
            throw new Error(errorMessage);
        } finally {
            setLoading(false);
        }
    }, []);

    return { toggleLike, loading, error };
};

// Hook to report a comment
export const useReportComment = () => {
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);

    const reportCommentAction = useCallback(async (commentUuid, reportData) => {
        try {
            setLoading(true);
            setError(null);
            
            const response = await reportComment(commentUuid, reportData);
            return response;
        } catch (err) {
            console.error('Error reporting comment:', err);
            const errorMessage = err.response?.data?.detail || err.message || 'Failed to report comment';
            setError(errorMessage);
            throw new Error(errorMessage);
        } finally {
            setLoading(false);
        }
    }, []);

    return { reportCommentAction, loading, error };
};