import { useState, useEffect, useCallback } from 'react';
import { 
    getPosts, 
    getPost, 
    getPostImage,
    togglePostLike, 
    getPostStats,
    getPostsByCategory,
    getPostsByAuthor,
    getPopularPosts
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
            // Extract the posts array from the paginated response
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
            // Extract the posts array from the paginated response
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
            // Extract the posts array from the paginated response
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
            // Extract the posts array from the paginated response
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