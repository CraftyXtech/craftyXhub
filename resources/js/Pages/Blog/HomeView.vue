<script setup>
import { ref, onMounted } from 'vue';
import { Head } from '@inertiajs/vue3';
import TheHeader from '@/Components/Layout/TheHeader.vue';
import TheFooter from '@/Components/Layout/TheFooter.vue';
import BlogPostCard from '@/Components/Blog/BlogPostCard.vue';
import CategoryTags from '@/Components/Blog/CategoryTags.vue';
import SearchBar from '@/Components/Shared/SearchBar.vue';
import SubscribeBanner from '@/Components/Shared/SubscribeBanner.vue';

// Mock data for blog posts
const allPosts = [
    {
        id: 1,
        title: 'Essential Knitting Tips for Beginners',
        slug: 'essential-knitting-tips-for-beginners',
        excerpt: 'Learn the basics of knitting with these helpful tips and tricks. From choosing the right yarn to mastering different stitches, get started on your knitting journey today!',
        category: 'Crafts',
        categoryId: 2,
        readTime: '3 min',
        imageUrl: 'https://via.placeholder.com/800x600/FF6B6B/FFFFFF?text=Knitting+Basics',
        date: '2023-05-15'
    },
    {
        id: 2,
        title: 'Creating Beautiful Polymer Clay Jewelry',
        slug: 'creating-beautiful-polymer-clay-jewelry',
        excerpt: 'Discover how to make stunning polymer clay jewelry from home. This beginner-friendly guide covers materials, techniques, and design tips for creating unique pieces.',
        category: 'Jewelry',
        categoryId: 5,
        readTime: '5 min',
        imageUrl: 'https://via.placeholder.com/800x600/4ECDC4/FFFFFF?text=Polymer+Clay',
        date: '2023-06-02'
    },
    {
        id: 3,
        title: 'DIY Home Decor Projects Under $50',
        slug: 'diy-home-decor-projects-under-50',
        excerpt: 'Transform your space with these budget-friendly DIY home decor ideas. Get a designer look without breaking the bank using simple materials and techniques.',
        category: 'DIY',
        categoryId: 3,
        readTime: '4 min',
        imageUrl: 'https://via.placeholder.com/800x600/FFD166/000000?text=Home+Decor',
        date: '2023-07-11'
    },
    {
        id: 4,
        title: 'Digital Art Fundamentals for Craft Businesses',
        slug: 'digital-art-fundamentals-for-craft-businesses',
        excerpt: 'Level up your craft business with digital art. Learn how to create digital designs for products, marketing, and online presence to boost your craft sales.',
        category: 'Art',
        categoryId: 4,
        readTime: '7 min',
        imageUrl: 'https://via.placeholder.com/800x600/6A0572/FFFFFF?text=Digital+Art',
        date: '2023-08-05'
    },
    {
        id: 5,
        title: 'Sustainable Crafting: Eco-Friendly Materials Guide',
        slug: 'sustainable-crafting-eco-friendly-materials-guide',
        excerpt: 'Make your crafting more environmentally friendly with this guide to sustainable materials and practices. Reduce waste while creating beautiful handmade items.',
        category: 'Crafts',
        categoryId: 2,
        readTime: '4 min',
        imageUrl: 'https://via.placeholder.com/800x600/1B9AAA/FFFFFF?text=Sustainable+Crafts',
        date: '2023-09-15'
    },
    {
        id: 6,
        title: 'Building a Supportive Crafting Community',
        slug: 'building-a-supportive-crafting-community',
        excerpt: 'Learn how to connect with fellow artisans and build a supportive community around your craft. Networking tips, collaboration ideas, and community-building strategies.',
        category: 'Community',
        categoryId: 7,
        readTime: '5 min',
        imageUrl: 'https://via.placeholder.com/800x600/F78764/FFFFFF?text=Craft+Community',
        date: '2023-10-07'
    },
    {
        id: 7,
        title: 'Handmade Candle Making at Home',
        slug: 'handmade-candle-making-at-home',
        excerpt: 'Start your own candle-making hobby or business with this comprehensive guide. Learn about different waxes, fragrances, and techniques for beautiful homemade candles.',
        category: 'Handmade',
        categoryId: 6,
        readTime: '6 min',
        imageUrl: 'https://via.placeholder.com/800x600/06D6A0/FFFFFF?text=Candle+Making',
        date: '2023-11-12'
    },
    {
        id: 8,
        title: 'Tech Solutions for Managing Your Craft Business',
        slug: 'tech-solutions-for-managing-your-craft-business',
        excerpt: 'Streamline your craft business with the right technology. From inventory management to online marketing, discover tools that will help you grow and scale your creative venture.',
        category: 'Technology',
        categoryId: 1,
        readTime: '8 min',
        imageUrl: 'https://via.placeholder.com/800x600/118AB2/FFFFFF?text=Craft+Tech',
        date: '2023-12-01'
    },
    {
        id: 9,
        title: 'Seasonal Craft Ideas for Winter Holidays',
        slug: 'seasonal-craft-ideas-for-winter-holidays',
        excerpt: 'Get inspired with these winter holiday craft projects. Perfect for gifts, decorations, or selling at seasonal markets. Includes step-by-step tutorials and material lists.',
        category: 'DIY',
        categoryId: 3,
        readTime: '4 min',
        imageUrl: 'https://via.placeholder.com/800x600/073B4C/FFFFFF?text=Winter+Crafts',
        date: '2024-01-05'
    }
];

// Reactive state
const displayedPosts = ref([...allPosts]);
const searchQuery = ref('');
const selectedCategory = ref(0); // Default: All
const isLoading = ref(false);

// Methods
const filterByCategory = (categoryId) => {
    selectedCategory.value = categoryId;
    applyFilters();
};

const handleSearch = (query) => {
    searchQuery.value = query;
    applyFilters();
};

const applyFilters = () => {
    isLoading.value = true;
    
    // Simulate API call/loading
    setTimeout(() => {
        // First filter by category (if not "All")
        let filtered = [...allPosts];
        
        if (selectedCategory.value !== 0) {
            filtered = filtered.filter(post => post.categoryId === selectedCategory.value);
        }
        
        // Then filter by search query if present
        if (searchQuery.value) {
            const query = searchQuery.value.toLowerCase();
            filtered = filtered.filter(post => 
                post.title.toLowerCase().includes(query) || 
                post.excerpt.toLowerCase().includes(query) ||
                post.category.toLowerCase().includes(query)
            );
        }
        
        displayedPosts.value = filtered;
        isLoading.value = false;
    }, 300);
};

const loadMore = () => {
    // In a real app, this would load the next page of results
    // For this demo, we'll just simulate a loading state
    isLoading.value = true;
    
    setTimeout(() => {
        isLoading.value = false;
        // You might add more posts here in a real application
    }, 1000);
};

// Initialize
onMounted(() => {
    // Simulate initial data fetch
    isLoading.value = true;
    setTimeout(() => {
        isLoading.value = false;
    }, 300);
});
</script>

<template>
    <Head title="CraftyXhub - Discover, Create & Connect" />
    
    <TheHeader />
    
    <main>
        <!-- Hero Section -->
        <section class="py-12 border-b border-gray-200 mb-8">
            <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
                <p class="text-primary text-sm font-medium mb-2">
                    Explore Ideas, Crafts & Inspiration That Matter
                </p>
                
                <h1 class="text-3xl md:text-4xl font-bold mb-2 flex items-center justify-center gap-2">
                    <span>🚀</span> <!-- Placeholder for icon -->
                    <span>Discover, Create & Connect</span>
                </h1>
                
                <p class="max-w-2xl mx-auto text-gray-600 mb-8">
                    Join 24K+ artisans exploring the latest crafting techniques, expert tips, and engaging stories. 
                    Showcase your creations, find resources, and connect with like-minded creators.
                </p>
                
                <CategoryTags @filter="filterByCategory" />
                
                <SearchBar @search="handleSearch" />
            </div>
        </section>
        
        <!-- Blog Grid Section -->
        <section class="py-8 mb-16">
            <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                <!-- Loading indicator -->
                <div v-if="isLoading" class="flex justify-center items-center py-12">
                    <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div>
                </div>
                
                <!-- No results message -->
                <div v-else-if="displayedPosts.length === 0" class="text-center py-12">
                    <h3 class="text-xl font-medium text-gray-700 mb-2">No results found</h3>
                    <p class="text-gray-500">
                        Try adjusting your search or filter to find what you're looking for.
                    </p>
                </div>
                
                <!-- Posts grid -->
                <div 
                    v-else 
                    class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8"
                >
                    <BlogPostCard 
                        v-for="post in displayedPosts" 
                        :key="post.id" 
                        :post="post" 
                    />
                </div>
                
                <!-- Load more button -->
                <div class="text-center mt-12">
                    <button 
                        @click="loadMore" 
                        class="px-6 py-3 border border-gray-300 rounded-full text-gray-700 hover:bg-gray-50 inline-flex items-center"
                        :disabled="isLoading"
                    >
                        <span>Load More</span>
                        <span class="ml-1 text-xs">▼</span>
                    </button>
                </div>
            </div>
        </section>
        
        <SubscribeBanner />
    </main>
    
    <TheFooter />
</template> 