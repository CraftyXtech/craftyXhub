<template>
  <div v-if="(category && category.name) || (tags && tags.length)" class="mt-8 p-4 bg-gray-100 dark:bg-gray-800 rounded-lg shadow">
    <h3 class="text-lg font-semibold mb-3 text-gray-800 dark:text-gray-200">Explore Topics</h3>
    <div class="flex flex-wrap gap-2">
      <!-- Display Category -->
      <Link 
        v-if="category && category.slug"
        :href="route('home', { category: category.slug })" 
        class="px-3 py-1 bg-blue-200 text-blue-800 rounded-full text-sm font-medium hover:bg-blue-300 transition duration-150 ease-in-out"
      >
        {{ category.name }}
      </Link>

      <!-- Display Tags -->
      <Link 
        v-for="tag in tags" 
        :key="tag.id" 
        :href="route('home', { tag: tag.slug })" 
        class="px-3 py-1 bg-gray-200 text-gray-700 rounded-full text-sm font-medium hover:bg-gray-300 dark:bg-gray-700 dark:text-gray-200 dark:hover:bg-gray-600 transition duration-150 ease-in-out"
      >
        #{{ tag.name }}
      </Link>
    </div>
  </div>
</template>

<script setup>
import { Link } from '@inertiajs/vue3';

defineProps({
  category: {
    type: Object,
    default: () => null
  },
  tags: {
    type: Array,
    default: () => []
  }
});
</script> 