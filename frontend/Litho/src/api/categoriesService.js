import { axiosInstance } from './axios';


export const getCategories = async () => {
    try {
        const response = await axiosInstance.get('/posts/categories/');
        return response.data;
    } catch (error) {
        throw error;
    }
};

// Get subcategories for a specific category (placeholder - implement if API supports it)
export const getSubcategories = async (categoryId) => {
    try {
        // TODO: Implement when backend API supports subcategories        
        return [];
    } catch (error) {
        throw error;
    }
}; 