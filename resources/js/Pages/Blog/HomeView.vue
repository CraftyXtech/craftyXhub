<template>
    <Head title="CraftyXhub - Discover, Create & Connect" />
    
    <Navbar />
    
    <main class="bg-gray-50 dark:bg-gray-800">
        <!-- Hero Section - Simplified and refined -->
        <section class="py-16 border-b border-gray-100 dark:border-gray-700 bg-white dark:bg-gray-900">
            <div class="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
                <p class="text-gray-600 dark:text-gray-400 text-sm font-medium mb-3">
                    <span class="bg-blue-50 text-blue-500 p-2 rounded-2xl">
                        Explore Ideas, Insights & Inspiration
                    </span>
                </p>
                
                <h1 class="text-3xl md:text-4xl font-semibold mb-4 text-gray-900 dark:text-gray-100">
                    Discover, Learn & Stay Inspired
                </h1>
                
                <p class="max-w-8xl mx-auto text-[#535454] dark:text-gray-400 mb-10">
                    Join thousands exploring the latest trends, expert tips, and engaging stories across various fields. 
                    Find resources, share insights, and connect with like-minded individuals.
                </p>
                
                <CategoryTags @filter="filterByCategory" :categories="categoryMapForTags" />
                
                <SearchBar 
                    :modelValue="searchQuery" 
                    @update:modelValue="searchQuery = $event" 
                    @search="handleSearch"
                    @clear="clearSearch"
                    class="mt-6"
                 />
                 <p v-if="props.filters.query" class="mt-2 text-sm text-gray-500 dark:text-gray-400">
                    Showing results for: "{{ props.filters.query }}". 
                    <button @click="clearSearch" class="text-indigo-500 dark:text-indigo-400 hover:underline">Clear search</button>
                </p>
            </div>
        </section>
        
        <!-- Trending Now Section - Cleaner design -->
        <section class="py-16 bg-white dark:bg-gray-900">
             <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                <h2 class="text-2xl font-semibold mb-10 text-center text-gray-800 dark:text-gray-200">Trending Now</h2>
                <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
                    <BlogPostCard
                        v-for="post in trendingPosts"
                        :key="'trending-'+post.id"
                        :post="post"
                    />
                </div>
            </div>
        </section>
        
        <!-- Recommended For You Section - More subtle -->
        <section v-if="isAuthenticated && props.recommendedPosts.data.length > 0" class="py-16 bg-gray-50 dark:bg-gray-800">
             <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                 <RecommendedArticles :posts="props.recommendedPosts.data" />
            </div>
        </section>


        <section class="py-16 bg-gray-50 dark:bg-gray-800">
            <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                <h2 v-if="!props.filters.query" class="text-2xl font-semibold mb-10 text-center text-gray-800 dark:text-gray-200">Latest Articles</h2>
                <h2 v-else class="text-2xl font-semibold mb-10 text-center text-gray-800 dark:text-gray-200">Search Results</h2>
                
                <div v-if="isLoading" class="flex justify-center items-center py-16">
                    <div class="animate-spin rounded-full h-10 w-10 border-b-2 border-gray-400"></div>
                </div>
                <div v-else-if="props.posts?.data?.length > 0" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
                    <BlogPostCard 
                        v-for="post in props.posts.data" 
                        :key="post.id" 
                        :post="post" 
                    />
                </div>
                <div v-else class="text-center py-16 text-gray-500 dark:text-gray-400">
                     <p v-if="props.filters.query">No posts found matching your search "{{ props.filters.query }}".</p>
                     <p v-else-if="props.filters.category">No posts found in the category "{{ props.filters.category }}".</p>
                    <p v-else>No posts available yet.</p>
                </div>
                
                <!-- Pagination - Refined design -->
                <div v-if="props.posts?.links?.length > 3" class="mt-12 flex justify-center">
                     <div class="flex flex-wrap -mb-1">
                        <template v-for="(link, key) in props.posts.links" :key="key">
                             <div 
                                v-if="link.url === null" 
                                class="mr-1 mb-1 px-4 py-2 text-sm leading-5 text-gray-400 border rounded"
                                v-html="link.label"
                            />
                            <Link 
                                v-else 
                                class="mr-1 mb-1 px-4 py-2 text-sm leading-5 border rounded hover:bg-gray-50 focus:border-gray-400 focus:text-gray-700 dark:hover:bg-gray-700 dark:focus:border-gray-500 dark:focus:text-gray-300"
                                :class="{ 'bg-gray-50 dark:bg-gray-700': link.active }" 
                                :href="link.url" 
                                v-html="link.label" 
                                preserve-state 
                                preserve-scroll
                             />
                        </template>
                    </div>
                 </div>
            </div>
        </section>
        
        <SubscribeBanner />
    </main>
    
    <Footer />
</template> 


<script setup>
import { ref, computed, watch } from 'vue';
import { Head, Link, usePage, router } from '@inertiajs/vue3';
import Navbar from '@/Components/Layout/Navbar.vue';
import Footer from '@/Components/Layout/Footer.vue';
import BlogPostCard from '@/Components/Blog/BlogPostCard.vue';
import CategoryTags from '@/Components/Blog/CategoryTags.vue';
import SearchBar from '@/Components/Shared/SearchBar.vue';
import SubscribeBanner from '@/Components/Shared/SubscribeBanner.vue';
import RecommendedArticles from '@/Components/RecommendedArticles.vue';
import RecentlyReadArticles from '@/Components/Blog/RecentlyReadArticles.vue';
import FollowedTopics from '@/Components/Blog/FollowedTopics.vue';

// --- Define Props --- 
const props = defineProps({
  posts: { type: Object, required: true }, // Laravel Paginator
  filters: { type: Object, default: () => ({ query: null, category: null }) }, // Contains query, category
  // Conditionally loaded props (ensure controller passes these if needed)
  recentlyRead: { type: Object, default: () => ({ data: [] }) },
  followedTopics: { type: Array, default: () => [] },
  suggestedTopics: { type: Array, default: () => [] },
  recommendedPosts: { type: Object, default: () => ({ data: [] }) } // For partial reload
});

// Reactive state (mostly for UI control, not primary data)
const searchQuery = ref(props.filters.query || '');
const selectedCategory = ref(props.filters.category || null);
const isLoading = ref(false); // Router events can manage this
const isSearching = ref(!!props.filters.query);

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

// Computed properties using props
const trendingPosts = computed(() => {
    return props.posts?.data?.slice(0, 3) || [];
});

const featuredAuthor = ref({
    name: 'Alex Thompson',
    bio: 'Alex is a passionate full-stack developer and tech writer, focused on making complex topics accessible. He loves exploring new frameworks and sharing his findings with the community.',
    imageUrl: 'https://via.placeholder.com/150/073B4C/FFFFFF?text=Alex+T',
    profileLink: '#'
});

// --- Methods using Inertia Router --- 

const executeSearch = (query) => {
    // Use router.get for searching, passing current category filter
    router.get(route('home'), { 
        query: query, 
        category: selectedCategory.value || undefined // Keep category filter
    }, {
        preserveState: true, 
        replace: true, // Avoid adding duplicate history entries for searches
        onStart: () => isLoading.value = true,
        onFinish: () => isLoading.value = false,
    });
};

const clearSearch = () => {
    searchQuery.value = '';
    // Go back to non-search state by removing the query param
    router.get(route('home'), { 
        category: selectedCategory.value || undefined // Keep category filter
    }, {
        preserveState: true, 
        replace: true,
        onStart: () => isLoading.value = true,
        onFinish: () => isLoading.value = false,
    });
};

const handleSearch = (query) => {
    // Optional: Add debounce or length check
    executeSearch(query);
};

const filterByCategory = (categorySlug) => {
    const newCategory = categorySlug === 'all' ? null : categorySlug;
    selectedCategory.value = newCategory;
    searchQuery.value = ''; // Clear search when changing category
    
    // Use router.get for category filtering
    router.get(route('home'), { 
        category: newCategory || undefined 
    }, {
        preserveState: true, 
        replace: true, 
        onStart: () => isLoading.value = true,
        onFinish: () => isLoading.value = false,
    });
};

// Fetch recommendations using partial reload
const fetchRecommendations = () => {
    if (!isAuthenticated.value || !route().has('recommendations.index')) return; // Check if route exists
    router.get(route('recommendations.index'), {}, {
        only: ['recommendedPosts'],
        preserveState: true,
        preserveScroll: true, 
    });
};

// Watch for authentication status to fetch recommendations
watch(isAuthenticated, (newValue) => {
    if (newValue) {
        fetchRecommendations();
    }
}, { immediate: true });

// Watch for changes in filters from URL to update local state if needed
watch(() => props.filters, (newFilters) => {
    searchQuery.value = newFilters.query || '';
    selectedCategory.value = newFilters.category || null;
    isSearching.value = !!newFilters.query;
}, { deep: true });

</script>