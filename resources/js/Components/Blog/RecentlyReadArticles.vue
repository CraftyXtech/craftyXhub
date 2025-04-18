<script setup>
import { ref, computed } from 'vue';
import { Link } from '@inertiajs/vue3';
import BlogPostCard from '@/Components/Blog/BlogPostCard.vue';

const props = defineProps({
    articles: {
        type: Array,
        default: () => []
    },
    isLoading: {
        type: Boolean,
        default: false
    }
});

// Check if there are any articles to display
const hasArticles = computed(() => props.articles && props.articles.length > 0);
</script>

<template>
    <div class="bg-white dark:bg-gray-900 rounded-lg shadow-sm overflow-hidden">
        <div class="p-6">
            <h2 class="text-2xl font-bold mb-6 text-gray-900 dark:text-gray-100">
                Recently Read Articles
            </h2>
            
            <div v-if="isLoading" class="flex justify-center items-center py-12">
                <div class="animate-spin rounded-full h-10 w-10 border-b-2 border-primary dark:border-primary-light"></div>
            </div>
            
            <div v-else-if="hasArticles" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                <BlogPostCard 
                    v-for="article in articles" 
                    :key="article.id" 
                    :post="article"
                />
            </div>
            
            <div v-else class="text-center py-8">
                <p class="text-gray-500 dark:text-gray-400 mb-4">
                    You haven't read any articles yet.
                </p>
                <p class="text-gray-600 dark:text-gray-300">
                    Explore our latest articles to see them appear here.
                </p>
            </div>
            
            <div v-if="hasArticles" class="mt-8 text-center">
                <Link 
                    :href="route('profile.view')" 
                    class="inline-flex items-center px-4 py-2 bg-indigo-600 border border-transparent rounded-md font-semibold text-xs text-white uppercase tracking-widest hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 dark:focus:ring-offset-gray-800 transition ease-in-out duration-150"
                >
                    View All Reading History
                </Link>
            </div>
        </div>
    </div>
</template> 