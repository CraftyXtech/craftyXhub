<template>
  <div v-if="posts && posts.length > 0">
    <h2 class="text-2xl font-semibold mb-4 dark:text-gray-200">Recommended For You</h2>
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      <div 
        v-for="post in posts" 
        :key="post.id"
        class="bg-white dark:bg-gray-800 rounded-lg shadow-md overflow-hidden hover:shadow-lg transition-shadow duration-300"
      >
        <Link :href="route('posts.show', post.slug)">
          <!-- Placeholder for image if available -->
          <!-- <img :src="post.imageUrl || '/placeholder-image.jpg'" alt="Post image" class="w-full h-48 object-cover"> -->
          <div class="p-4">
            <span class="text-sm text-indigo-600 dark:text-indigo-400 font-medium">{{ post.category?.name || 'Uncategorized' }}</span>
            <h3 class="text-lg font-semibold mt-1 mb-2 dark:text-gray-100 hover:text-indigo-700 dark:hover:text-indigo-300 transition-colors duration-200">{{ post.title }}</h3>
            <p class="text-sm text-gray-600 dark:text-gray-400 mb-3">{{ post.excerpt }}</p>
            <div class="flex items-center text-xs text-gray-500 dark:text-gray-400">
              <span>By {{ post.author?.name || 'Unknown Author' }}</span>
              <span class="mx-2">•</span>
              <span>{{ post.published_at_human }}</span>
               <span class="mx-2">•</span>
              <span>{{ post.likers_count || 0 }} Likes</span>
            </div>
          </div>
        </Link>
      </div>
    </div>
  </div>
</template>

<script setup>
import { Link } from '@inertiajs/vue3';

defineProps({
  posts: {
    type: Array,
    default: () => [],
  },
});
</script> 