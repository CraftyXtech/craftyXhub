import React, { useState, useEffect } from 'react';
import { useCategories } from '../../api/usePosts';

export const DashboardMenuData = {
    title: 'Dashboard',
    dropdown: [
        {
            title: 'Overview',
            link: '/dashboard'
        },
        {
            title: 'My Posts',
            link: '/user/posts'
        },
        {
            title: 'Media Library',
            link: '/user/media'
        },
        {
            title: 'Bookmarks',
            link: '/user/bookmarks'
        },
        {
            title: 'Create Post',
            link: '/posts/create'
        },
        {
            title: 'Profile Settings',
            link: '/user/profile'
        }
    ]
};

export const useDynamicHeaderData = () => {
    const { categories, loading, error } = useCategories();
    const [headerData, setHeaderData] = useState([]);

    useEffect(() => {
        if (!loading && !error && categories.length > 0) {
            setHeaderData(categories);
        } else if (!loading) {
            setHeaderData([]);
        }
    }, [categories, loading, error]);

    return {
        headerData,
        loading,
        error,
        isUsingFallback: error || categories.length === 0
    };
};

const HeaderData = [];
export default HeaderData;