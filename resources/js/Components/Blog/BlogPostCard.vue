<template>
    <div class="bg-white dark:bg-gray-900 rounded-xl shadow-lg overflow-hidden transition-all duration-300 transform hover:-translate-y-2 hover:shadow-2xl group">
      <Link :href="cardUrl" class="block">
        <div class="relative ">
          <div class="">
            <img
              :src="post.image_url || '/default.jpeg'"
              :alt="post.title"
              class="w-full h-full object-cover transition-transform duration-500 group-hover:scale-110"
              loading="lazy"
            />
          </div>
          <div v-if="post.category" class="absolute top-3 left-3 bg-white/80 dark:bg-gray-800/80 px-3 py-1 rounded-full text-xs font-semibold text-gray-800 dark:text-gray-200">
            {{ post.category.name }}
          </div>
        </div>
        
        <div class="p-5">
          <div class="flex items-center justify-between mb-3">
            <span class="text-xs text-gray-500 dark:text-gray-400 flex items-center">
              <svg class="w-4 h-4 mr-2 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"></path>
              </svg>
              {{ post.reading_time }} min read
            </span>
            <div class="flex items-center space-x-2">
              <button @click.prevent="toggleLike" class="text-gray-500 dark:text-gray-400 hover:text-red-500 dark:hover:text-red-400 transition-colors">
                <svg class="w-5 h-5" :class="{ 'text-red-500 dark:text-red-400': post.liked }" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z"></path>
                </svg>
              </button>
              <span class="text-xs text-gray-500 dark:text-gray-400">
                {{ post.likers_count || 0 }}
              </span>
            </div>
          </div>
  
          <h3 class="text-xl font-bold mb-2 text-gray-900 dark:text-gray-100 group-hover:text-blue-600 dark:group-hover:text-blue-400 transition-colors duration-300">
            {{ truncateTitle(post.title) }}
          </h3>
          
          <p class="text-sm text-gray-600 dark:text-gray-400 mb-4 line-clamp-3">
            {{ truncateExcerpt(post.excerpt) }}
          </p>
          
          <div class="flex items-center justify-between border-t border-gray-200 dark:border-gray-700 pt-4">
            <div class="flex items-center space-x-3">
              <img 
                :src="post.author?.avatar || '/default-user.jpeg'" 
                :alt="post.author?.name || 'Author'"
                class="w-8 h-8 rounded-full object-cover"
              />
              <span class="text-sm text-gray-700 dark:text-gray-300">
                {{ post.author?.name || 'Anonymous' }}
              </span>
            </div>
            <span class="text-xs text-gray-500 dark:text-gray-400">
              {{ post.published_at_human }}
            </span>
          </div>
        </div>
      </Link>
    </div>
  </template>
  
  <script setup>
  import { Link, router } from '@inertiajs/vue3';
  import { computed } from 'vue';
  
  const props = defineProps({
    post: {
      type: Object,
      required: true,
    }
  });
  
  const cardUrl = computed(() => {
    if (props.post && props.post.url) {
      return props.post.url;
    }
    if (props.post && props.post.slug && route().has('posts.show')) {
      return route('posts.show', props.post.slug);
    }
    return '#'; 
  });
  
  const truncateTitle = (title, maxLength = 60) => {
    if (!title) return '';
    return title.length > maxLength 
      ? title.substring(0, maxLength) + '...' 
      : title;
  };
  
  const truncateExcerpt = (excerpt, maxLength = 150) => {
    if (!excerpt) return '';
    return excerpt.length > maxLength 
      ? excerpt.substring(0, maxLength) + '...' 
      : excerpt;
  };
  
  const toggleLike = () => {
    console.log('Like toggled for post', props.post.id);
  };
  </script>
  
  <style scoped>
  .aspect-w-16 {
    position: relative;
    width: 100%;
    padding-bottom: 56.25%; /* 16:9 aspect ratio */
  }
  .aspect-h-9 {
    position: absolute;
    top: 0;
    right: 0;
    bottom: 0;
    left: 0;
  }
  </style>