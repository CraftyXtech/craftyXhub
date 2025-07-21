import { useState, useEffect, useCallback } from 'react';
import { getTags } from './tagsService';

// Hook to get all tags
export const useTags = () => {
    const [tags, setTags] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    const fetchTags = useCallback(async () => {
        try {
            setLoading(true);
            const data = await getTags();
            setTags(data);
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