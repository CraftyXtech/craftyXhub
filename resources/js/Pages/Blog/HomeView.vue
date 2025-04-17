<script setup>
import { ref, onMounted, computed, watch } from 'vue';
import { Head, Link, usePage } from '@inertiajs/vue3';
import axios from 'axios';
import TheHeader from '@/Components/Layout/TheHeader.vue';
import TheFooter from '@/Components/Layout/TheFooter.vue';
import BlogPostCard from '@/Components/Blog/BlogPostCard.vue';
import CategoryTags from '@/Components/Blog/CategoryTags.vue';
import SearchBar from '@/Components/Shared/SearchBar.vue';
import SubscribeBanner from '@/Components/Shared/SubscribeBanner.vue';
import RecommendedArticles from '@/Components/RecommendedArticles.vue';

// Reactive state
const displayedPosts = ref([]);
const paginationData = ref(null);
const searchQuery = ref('');
const currentSearchTerm = ref('');
const selectedCategory = ref(null);
const isLoading = ref(false);
const isSearching = ref(false);
const recommendedPosts = ref([]);
const isLoadingRecommendations = ref(false);

const page = usePage();

// Check if user is authenticated
const isAuthenticated = computed(() => !!page.props.auth.user);

// Define a simple map for categories used in the CategoryTags component
// In a real app, this might be fetched or passed from the backend
const categoryMapForTags = ref([
    { id: 'all', name: 'All', slug: 'all' }, // Use 'all' slug for clearing filter
    { id: 1, name: 'Technology', slug: 'technology' },
    { id: 2, name: 'Finance', slug: 'finance' },
    { id: 3, name: 'Health', slug: 'health' },
    { id: 4, name: 'Education', slug: 'education' },
    { id: 5, name: 'Sports', slug: 'sports' },
    { id: 6, name: 'Travel', slug: 'travel' },
    { id: 7, name: 'Lifestyle', slug: 'lifestyle' },
    { id: 8, name: 'Community', slug: 'community' }
]);

// Computed properties
const trendingPosts = computed(() => {
    const initialPosts = paginationData.value?.data || displayedPosts.value;
    return initialPosts.slice(0, 3);
});

const featuredAuthor = ref({
    name: 'Alex Thompson',
    bio: 'Alex is a passionate full-stack developer and tech writer, focused on making complex topics accessible. He loves exploring new frameworks and sharing his findings with the community.',
    imageUrl: 'https://via.placeholder.com/150/073B4C/FFFFFF?text=Alex+T',
    profileLink: '#'
});

// Methods
const fetchPosts = async (page = 1, preserveScroll = false) => {
    if (isSearching.value) return;
    
    isLoading.value = true;
    try {
        let params = { page: page };
        if (selectedCategory.value) {
            params.category = selectedCategory.value;
        }

        const response = await axios.get('/api/posts', { params });

        if (page === 1) {
            displayedPosts.value = response.data.data;
        } else {
            displayedPosts.value = [...displayedPosts.value, ...response.data.data];
        }
        paginationData.value = response.data.meta;

    } catch (error) {
        console.error("Error fetching posts:", error);
        displayedPosts.value = [];
        paginationData.value = null;
    } finally {
        isLoading.value = false;
        if (!preserveScroll) {
            window.scrollTo({ top: 0, behavior: 'smooth' });
        }
    }
};

const executeSearch = async (query) => {
    if (!query || query.length < 3) {
        clearSearch();
        return;
    }
    
    isLoading.value = true;
    isSearching.value = true;
    currentSearchTerm.value = query;
    displayedPosts.value = [];
    paginationData.value = null;

    try {
        const response = await axios.get('/api/search', { 
            params: { query: query, limit: 12 }
        });
        displayedPosts.value = response.data.data;
    } catch (error) {
        console.error("Error executing search:", error);
        displayedPosts.value = [];
    } finally {
        isLoading.value = false;
    }
};

const clearSearch = () => {
    searchQuery.value = '';
    currentSearchTerm.value = '';
    if (isSearching.value) {
        isSearching.value = false;
        fetchPosts();
    }
};

const handleSearch = (query) => {
    searchQuery.value = query;
    executeSearch(query);
};

const filterByCategory = (categorySlug) => {
    clearSearch();
    selectedCategory.value = categorySlug === 'all' ? null : categorySlug;
    fetchPosts();
};

const fetchRecommendations = async () => {
    if (!isAuthenticated.value) return;
    
    isLoadingRecommendations.value = true;
    try {
        const response = await axios.get('/api/posts/recommendations');
        recommendedPosts.value = response.data.data;
    } catch (error) {
        if (error.response && error.response.status !== 401) {
             console.error("Error fetching recommendations:", error);
        }
        recommendedPosts.value = [];
    } finally {
        isLoadingRecommendations.value = false;
    }
};

const loadMore = () => {
    if (!isSearching.value && paginationData.value && paginationData.value.current_page < paginationData.value.last_page) {
        fetchPosts(paginationData.value.current_page + 1, true);
    }
};

const getPageNumberFromUrl = (url) => {
    if (!url) return null;
    try {
        const urlParams = new URLSearchParams(new URL(url).search);
        return urlParams.get('page');
    } catch (e) {
        console.error("Error parsing pagination URL:", e);
        return null;
    }
}

onMounted(() => {
    fetchPosts();
    fetchRecommendations();
});
</script>

<template>
    <Head title="CraftyXhub - Discover, Create & Connect" />
    
    <TheHeader />
    
    <main class="bg-gray-50 dark:bg-gray-800">
        <!-- Hero Section -->
        <section class="py-12 border-b border-gray-200 dark:border-gray-700 mb-8 bg-white dark:bg-gray-900">
            <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
                <p class="text-primary dark:text-primary-light text-sm font-medium mb-2">
                    Explore Ideas, Insights & Inspiration That Matter
                </p>
                
                <h1 class="text-3xl md:text-4xl font-bold mb-2 flex items-center justify-center gap-2 text-gray-900 dark:text-gray-100">
                    <span>🚀</span>
                    <span>Discover Knowledge & Connect</span>
                </h1>
                
                <p class="max-w-2xl mx-auto text-gray-600 dark:text-gray-400 mb-8">
                    Join thousands exploring the latest trends, expert tips, and engaging stories across various fields. 
                    Find resources, share insights, and connect with like-minded individuals.
                </p>
                
                <CategoryTags @filter="filterByCategory" :categories="categoryMapForTags" />
                
                <SearchBar 
                    :modelValue="searchQuery" 
                    @update:modelValue="searchQuery = $event" 
                    @search="handleSearch" 
                    @clear="clearSearch" 
                 />
                 <p v-if="isSearching" class="mt-2 text-sm text-gray-600 dark:text-gray-400">
                    Showing semantic search results for: "{{ currentSearchTerm }}". 
                    <button @click="clearSearch" class="text-indigo-600 dark:text-indigo-400 hover:underline">Clear search</button>
                </p>
            </div>
        </section>
        
        <!-- Trending Now Section -->
        <section class="py-12 bg-white dark:bg-gray-900">
             <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                <h2 class="text-2xl font-bold mb-8 text-center text-gray-900 dark:text-gray-100">Trending Now 🔥</h2>
                <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
                    <BlogPostCard
                        v-for="post in trendingPosts"
                        :key="'trending-'+post.id"
                        :post="post"
                    />
                </div>
            </div>
        </section>
        
        <!-- Recommended For You Section -->
        <section v-if="isAuthenticated && recommendedPosts.length > 0" class="py-12 bg-gray-50 dark:bg-gray-800">
             <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                 <RecommendedArticles :posts="recommendedPosts" />
            </div>
        </section>

        <!-- Blog Grid Section -->
        <section class="py-12">
            <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                <h2 v-if="!isSearching" class="text-2xl font-bold mb-8 text-center text-gray-900 dark:text-gray-100">Latest Articles</h2>
                <h2 v-else class="text-2xl font-bold mb-8 text-center text-gray-900 dark:text-gray-100">Search Results</h2>
                
                <div v-if="isLoading" class="flex justify-center items-center py-16">
                    <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-primary dark:border-primary-light"></div>
                </div>
                <div v-else-if="displayedPosts.length > 0" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
                    <BlogPostCard 
                        v-for="post in displayedPosts" 
                        :key="post.id" 
                        :post="post" 
                    />
                </div>
                <div v-else-if="isSearching" class="text-center text-gray-500 dark:text-gray-400 py-16">
                    <p>No relevant articles found for "{{ currentSearchTerm }}". Try different keywords.</p>
                </div>
                <div v-else class="text-center text-gray-500 dark:text-gray-400 py-16">
                    <p>No articles found matching your criteria. Try adjusting your category.</p>
                </div>
                
                <div v-if="!isSearching">
                    <div class="text-center mt-12" v-if="paginationData && paginationData.current_page < paginationData.last_page">
                        <button @click="loadMore" :disabled="isLoading" class="bg-primary hover:bg-primary-dark text-white font-bold py-2 px-6 rounded-full transition duration-300 disabled:opacity-50 dark:bg-primary-light dark:hover:bg-primary dark:text-gray-900">
                            {{ isLoading ? 'Loading...' : 'Load More' }}
                        </button>
                    </div>
                    
                    <div class="flex justify-center mt-8 space-x-1" v-else-if="paginationData && paginationData.last_page > 1">
                        <button 
                            v-for="pageLink in paginationData.links" 
                            :key="pageLink.label" 
                            @click="fetchPosts(getPageNumberFromUrl(pageLink.url), true)" 
                            :disabled="!pageLink.url || pageLink.active || isLoading"
                            v-html="pageLink.label"
                            :class="[
                                'px-3 py-1 border rounded transition duration-150 text-sm',
                                pageLink.active ? 'bg-primary text-white border-primary dark:bg-primary-light dark:text-gray-900 dark:border-primary-light z-10' : 'bg-white hover:bg-gray-100 text-gray-600 border-gray-300 dark:bg-gray-700 dark:hover:bg-gray-600 dark:text-gray-300 dark:border-gray-600',
                                !pageLink.url ? 'opacity-50 cursor-not-allowed' : ''
                            ]"
                        >
                        </button>
                    </div>
                </div>
            </div>
        </section>
        
        <!-- Featured Author Section -->
        <section class="py-12 bg-gray-100 dark:bg-gray-800">
            <div class="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
                <h2 class="text-2xl font-bold mb-8 text-gray-900 dark:text-gray-100">Featured Author ✨</h2>
                <div class="flex flex-col sm:flex-row items-center gap-6 bg-white dark:bg-gray-700 p-6 rounded-lg shadow-md">
                    <img :src="featuredAuthor.imageUrl" :alt="featuredAuthor.name" class="w-24 h-24 rounded-full flex-shrink-0 border-4 border-primary dark:border-primary-light">
                    <div class="text-left">
                        <h3 class="text-xl font-semibold text-gray-900 dark:text-gray-100 mb-1">{{ featuredAuthor.name }}</h3>
                        <p class="text-gray-600 dark:text-gray-400 mb-3">{{ featuredAuthor.bio }}</p>
                        <Link :href="featuredAuthor.profileLink" class="font-medium text-sm text-primary hover:text-primary-dark dark:text-primary-light dark:hover:text-primary">
                            View Profile
                        </Link>
                    </div>
                </div>
            </div>
        </section>
        
        <SubscribeBanner />
    </main>
    
    <TheFooter />
</template> 