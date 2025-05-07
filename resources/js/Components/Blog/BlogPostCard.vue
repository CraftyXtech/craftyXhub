<script setup>
import { Link, router } from '@inertiajs/vue3';
import { computed } from 'vue';

const props = defineProps({
    post: {
        type: Object,
        required: true,
        // Expected structure of post:
        // {
        //   id: Number,
        //   title: String,
        //   slug: String,
        //   excerpt: String,
        //   category: String,
        //   readTime: String,
        //   imageUrl: String,
        //   date: String (optional)
        // }
    }
});

// Computed property to safely generate the URL
const cardUrl = computed(() => {
    if (props.post && props.post.url) {
        return props.post.url;
    }
    if (props.post && props.post.slug && route().has('posts.show')) { // Check if route exists
        return route('posts.show', props.post.slug);
    }
    return '#'; // Fallback URL if no slug or url is available
});
</script>

<template>
    <div class="bg-white dark:bg-gray-800 rounded-lg shadow-md overflow-hidden hover:shadow-lg transition-shadow duration-300 group">
        <Link :href="cardUrl">
            <div class="aspect-w-16 aspect-h-9 overflow-hidden">
                <img 
                    :src="post.display_image_url || '/images/placeholder-800x450.png'" 
                    :alt="post.title"
                    class="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300 ease-in-out"
                    loading="lazy" 
                />
            </div>
            <div class="p-4">
                <div class="flex justify-between items-center mb-1">
                    <span class="text-xs font-medium text-indigo-600 dark:text-indigo-400 uppercase tracking-wider">{{ post.category?.name || 'Uncategorized' }}</span>
                    <!-- Reading time - assuming it exists on post object -->
                    <span v-if="post.reading_time" class="text-xs text-gray-500 dark:text-gray-400">{{ post.reading_time }} min read</span> 
                </div>
                <h3 class="text-lg font-semibold mt-1 mb-2 text-gray-900 dark:text-gray-100 group-hover:text-indigo-700 dark:group-hover:text-indigo-300 transition-colors duration-200">{{ post.title }}</h3>
                <p class="text-sm text-gray-600 dark:text-gray-400 mb-3 line-clamp-2">{{ post.excerpt }}</p>
                <div class="flex items-center text-xs text-gray-500 dark:text-gray-400 mt-auto pt-2 border-t border-gray-200 dark:border-gray-700">
                    <span>By {{ post.author?.name || 'Unknown Author' }}</span>
                    <span class="mx-2">•</span>
                    <span>{{ post.published_at_human }}</span>
                    <span class="mx-2">•</span>
                    <span>{{ post.likers_count || 0 }} Likes</span>
                </div>
            </div>
        </Link>
    </div>
</template> 