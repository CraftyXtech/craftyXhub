<template>

    <Head title="CraftyXhub - Discover, Create & Connect" />

    <Navbar />

    <main class="bg-gray-50 dark:bg-gray-800">
        <section class="py-16 border-b border-gray-100 dark:border-gray-700 bg-white dark:bg-gray-900">
            <div class="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
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

                <CategoryTags @filter="filterByCategory" :categories="props.categories" />

                <SearchBar :modelValue="searchQuery" @update:modelValue="searchQuery = $event" @search="handleSearch"
                    @clear="clearSearch" class="mt-6" />
                <p v-if="props.filters.query" class="mt-2 text-sm text-gray-500 dark:text-gray-400">
                    Showing results for: "{{ props.filters.query }}".
                    <button @click="clearSearch" class="text-blue-500 dark:text-blue-400 hover:underline">Clear
                        search</button>
                </p>
            </div>
        </section>

        <section class="py-16 bg-white dark:bg-gray-900">
            <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                <div class="text-center mb-10">
                    <h2 class="text-2xl font-semibold text-gray-800 dark:text-gray-200 relative inline-block">
                        Popular Topics
                        <span
                            class="block h-1 w-24 mx-auto mt-2 bg-gradient-to-r from-blue-500 to-blue-700 rounded-full"></span>
                    </h2>
                    <p class="mt-4 text-gray-600 dark:text-gray-400 text-base max-w-2xl mx-auto">
                        Explore the most engaging discussions, trending insights, and community favorites that everyone
                        is talking about right now. Stay informed and inspired by the latest updates.
                    </p>
                </div>

                <div style="cursor: pointer;" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                    <TrendingCard v-for="post in trendingPosts" :key="'trending-' + post.id" :post="post" />
                </div>
            </div>
        </section>

        <section v-if="isAuthenticated && props.posts.data.length > 0"
            class="py-16 bg-gray-50 dark:bg-gray-800">
            <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                <div class="text-center mb-10">
                    <h2 class="text-2xl font-semibold text-gray-800 dark:text-gray-200 relative inline-block">
                        Recommended Articles
                        <span
                            class="block h-1 w-24 mx-auto mt-2 bg-gradient-to-r from-blue-500 to-blue-700 rounded-full"></span>
                    </h2>
                    <p class="mt-4 text-gray-600 dark:text-gray-400 text-base max-w-2xl mx-auto">
                        Curated just for you based on your interests and reading history. Discover content that aligns
                        with your preferences.
                    </p>
                </div>

                <RecommendedArticles :posts="props.recommendedPosts.data" />
            </div>
        </section>

        <section class="py-16 bg-gray-50 dark:bg-gray-800">
            <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                <div class="text-center mb-10">
                    <h2 v-if="!props.filters.query"
                        class="text-2xl font-semibold text-gray-800 dark:text-gray-200 relative inline-block">
                        Top Rated Articles
                        <span
                            class="block h-1 w-24 mx-auto mt-2 bg-gradient-to-r from-blue-500 to-blue-700 rounded-full"></span>
                    </h2>
                    <h2 v-else class="text-2xl font-semibold text-gray-800 dark:text-gray-200 relative inline-block">
                        Search Results
                        <span
                            class="block h-1 w-24 mx-auto mt-2 bg-gradient-to-r from-blue-500 to-blue-700 rounded-full"></span>
                    </h2>
                    <p class="mt-4 text-gray-600 dark:text-gray-400 text-base max-w-2xl mx-auto">
                        <span v-if="!props.filters.query">
                            Explore the highest rated content shared by our community—carefully selected for its value
                            and insight.
                        </span>
                        <span v-else>
                            Browse the articles that match your search criteria. We’ve fetched the most relevant content
                            for you.
                        </span>
                    </p>
                </div>

                <div v-if="isLoading" class="flex justify-center items-center py-16">
                    <div class="animate-spin rounded-full h-10 w-10 border-b-2 border-gray-400"></div>
                </div>

                <div v-else-if="props.posts?.data?.length > 0"
                    class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
                    <BlogPostCard v-for="post in props.posts.data" :key="post.id" :post="post" />
                </div>

                <div v-else class="text-center py-16 text-gray-500 dark:text-gray-400">
                    <p v-if="props.filters.query">No posts found matching your search "{{ props.filters.query }}".</p>
                    <p v-else-if="props.filters.category">No posts found in the category "{{ props.filters.category }}".
                    </p>
                    <p v-else>No posts available yet.</p>
                </div>

                <div v-if="props.posts?.links?.length > 3" class="mt-12 flex justify-center">
                    <div class="flex flex-wrap -mb-1">
                        <template v-for="(link, key) in props.posts.links" :key="key">
                            <div v-if="link.url === null"
                                class="mr-1 mb-1 px-4 py-2 text-sm leading-5 text-gray-400 border rounded"
                                v-html="link.label" />
                            <Link v-else
                                class="mr-1 mb-1 px-4 py-2 text-sm leading-5 border rounded hover:bg-gray-50 focus:border-gray-400 focus:text-gray-700 dark:hover:bg-gray-700 dark:focus:border-gray-500 dark:focus:text-gray-300"
                                :class="{ 'bg-gray-50 dark:bg-gray-700': link.active }" :href="link.url"
                                v-html="link.label" preserve-state preserve-scroll />
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
import TrendingCard from '../../Components/Blog/TrendingCard.vue';

const props = defineProps({
    posts: { type: Object, required: true },
    categories: { type: Object, required: true },
    filters: { type: Object, default: () => ({ query: null, category: null }) },
    recentlyRead: { type: Object, default: () => ({ data: [] }) },
    followedTopics: { type: Array, default: () => [] },
    suggestedTopics: { type: Array, default: () => [] },
    recommendedPosts: { type: Object, default: () => ({ data: [] }) }
});

const searchQuery = ref(props.filters.query || '');
const selectedCategory = ref(props.filters.category || null);
const isLoading = ref(false);
const isSearching = ref(!!props.filters.query);
const page = usePage();
const isAuthenticated = computed(() => !!page.props.auth.user);

const trendingPosts = computed(() => {
    return props.posts?.data?.slice(0, 3) || [];
});


const executeSearch = (query) => {
    router.get(route('home'), {
        query: query,
        category: selectedCategory.value || undefined
    }, {
        preserveState: true,
        replace: true,
        onStart: () => isLoading.value = true,
        onFinish: () => isLoading.value = false,
    });
};

const clearSearch = () => {
    searchQuery.value = '';
    router.get(route('home'), {
        category: selectedCategory.value || undefined
    }, {
        preserveState: true,
        replace: true,
        onStart: () => isLoading.value = true,
        onFinish: () => isLoading.value = false,
    });
};

const handleSearch = (query) => {
    executeSearch(query);
};

const filterByCategory = (categorySlug) => {
    const newCategory = categorySlug === 'all' ? null : categorySlug;
    selectedCategory.value = newCategory;
    searchQuery.value = '';

    router.get(route('home'), {
        category: newCategory || undefined
    }, {
        preserveState: true,
        replace: true,
        onStart: () => isLoading.value = true,
        onFinish: () => isLoading.value = false,
    });
};

const fetchRecommendations = () => {
    if (!isAuthenticated.value || !route().has('recommendations.index')) return;
    router.get(route('recommendations.index'), {}, {
        only: ['recommendedPosts'],
        preserveState: true,
        preserveScroll: true,
    });
};

watch(isAuthenticated, (newValue) => {
    if (newValue) {
        fetchRecommendations();
    }
}, { immediate: true });

watch(() => props.filters, (newFilters) => {
    searchQuery.value = newFilters.query || '';
    selectedCategory.value = newFilters.category || null;
    isSearching.value = !!newFilters.query;
}, { deep: true });

</script>