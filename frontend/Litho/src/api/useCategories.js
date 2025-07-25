import { useState, useEffect, useCallback } from 'react';
import { getCategories, getSubcategories } from './categoriesService';

export const useCategories = () => {
    const [categories, setCategories] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    const fetchCategories = useCallback(async () => {
        try {
            setLoading(true);
            const data = await getCategories();
            // Extract the categories array from the response
            setCategories(Array.isArray(data.categories) ? data.categories : []);
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

export const useSubcategories = (categoryId) => {
    const [subcategories, setSubcategories] = useState([]);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);

    useEffect(() => {
        if (!categoryId) {
            setSubcategories([]);
            return;
        }

        const fetchSubcategories = async () => {
            try {
                setLoading(true);
                const data = await getSubcategories(categoryId);
                // Extract subcategories array if it exists in the response
                setSubcategories(Array.isArray(data.subcategories) ? data.subcategories : Array.isArray(data) ? data : []);
                setError(null);
            } catch (err) {
                setError(err.response?.data?.detail || err.message);
                setSubcategories([]);
            } finally {
                setLoading(false);
            }
        };

        fetchSubcategories();
    }, [categoryId]);

    return { subcategories, loading, error };
}; 