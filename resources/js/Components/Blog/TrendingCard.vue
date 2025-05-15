<template>
    <div class="relative rounded-lg overflow-hidden group h-96 shadow-md transition-all duration-300 hover:shadow-xl">
      <div class="absolute inset-0">
        <img 
          :src="post.image_url || '/default.jpeg'" 
          :alt="post.title"
          class="w-full h-full object-cover transition-transform duration-300 group-hover:scale-105"
        />
        <div class="absolute inset-0 bg-gradient-to-t from-black/80 via-black/50 to-black/20"></div>
      </div>
      
      <div class="absolute inset-0 flex flex-col justify-between p-6 text-white">
        <div class="flex justify-between items-start">
          <span 
            class="px-3 py-1 bg-blue-600/80 text-white text-xs font-medium rounded-full"
          >
            {{ post.category?.name || 'Uncategorized' }}
          </span>
          
          <span class="text-xs text-gray-200">
            {{ post.published_at_human || formatDate(post.created_at) }}
          </span>
        </div>
        
        <div>
          <h3 class="text-xl font-bold mb-2 line-clamp-2">{{ post.title }}</h3>
          
          <p class="text-sm text-gray-200 mb-4 line-clamp-2">{{ post.excerpt }}</p>
          
          <div class="flex items-center">
            <div class="h-8 w-8 rounded-full bg-gray-300 overflow-hidden mr-3">
              <img 
                v-if="post.author && post.author.avatar" 
                :src="post.author.avatar" 
                :alt="post.author.name"
                class="h-full w-full object-cover"
              />
              <div v-else class="h-full w-full flex items-center justify-center bg-gray-400 text-white text-xs">
                {{ getInitials(post.author?.name || '') }}
              </div>
            </div>
            <div>
              <p class="text-sm font-medium">{{ post.author?.name }}</p>
              <p class="text-xs text-gray-300">{{ formatReadTime(post.read_time || 5) }}</p>
            </div>
          </div>
        </div>
      </div>      
    </div>
  </template>
  
  <script setup>
  import { computed } from 'vue';
  
  const props = defineProps({
    post: {
      type: Object,
      required: true
    }
  });
  
  // Log the post prop when the component is created/mounted
  console.log('TrendingCard received post (ID: ' + props.post.id + '):', JSON.parse(JSON.stringify(props.post)));
  if (props.post.id === 4) { // Or whatever ID corresponds to "trending-4" if not literal
      console.log('TrendingCard (ID: 4) - post.category:', JSON.parse(JSON.stringify(props.post.category)));
  }
  
  // Format date function (can be expanded based on requirements)
  const formatDate = (dateString) => {
    if (!dateString) return '';
    const date = new Date(dateString);
    return new Intl.DateTimeFormat('en-US', { 
      month: 'short', 
      day: 'numeric',
      year: 'numeric'
    }).format(date);
  };
  
  // Format read time
  const formatReadTime = (minutes) => {
    return `${minutes} min read`;
  };
  
  // Get initials for avatar fallback
  const getInitials = (name) => {
    if (!name) return '';
    return name
      .split(' ')
      .map(part => part.charAt(0))
      .join('')
      .toUpperCase()
      .substring(0, 2);
  };
  </script>