<template>
    <div class="flex flex-wrap justify-center items-center gap-3 mb-8 p-2">
      <button
        v-for="category in categories"
        :key="category.slug"
        :class="[
          'px-4 py-2 rounded-full transition-all duration-300 font-medium text-sm focus:outline-none focus:ring-2 focus:ring-offset-2',
          activeCategorySlug === category.slug
            ? 'bg-primary text-white shadow-md transform scale-105 focus:ring-primary/50'
            : 'bg-white text-gray-700 border border-gray-200 hover:bg-gray-50 hover:text-primary hover:border-primary/30 focus:ring-gray-400 dark:bg-gray-800 dark:text-gray-200 dark:border-gray-700 dark:hover:bg-gray-700 dark:hover:border-primary-light/40'
        ]"
        @click="selectCategory(category.slug)"
        :aria-pressed="activeCategorySlug === category.slug"
        :aria-label="`Filter by ${category.name} category`"
      >
        <span class="flex items-center gap-2">
          <span v-if="category.icon" class="text-lg">{{ category.icon }}</span>
          {{ category.name }}
          <span class="inline-flex items-center justify-center px-2 py-1 text-xs font-bold leading-none rounded-full bg-gray-100 text-gray-600 dark:bg-gray-700 dark:text-gray-300">
            {{ category.posts_count }}
          </span>
        </span>
      </button>
    </div>
  </template>
  
  <script setup>
  import { ref, watch } from 'vue';
  
  const props = defineProps({
    categories: {
      type: Array,
      required: true
    },
    initialActiveSlug: {
      type: String,
      default: 'all'
    },
    showCounts: {
      type: Boolean,
      default: false
    },
    persistSelection: {
      type: Boolean,
      default: false
    }
  });
  
  const emit = defineEmits(['filter', 'change']);
  
  const activeCategorySlug = ref(props.initialActiveSlug);
  
  if (props.persistSelection) {
    const storedCategory = localStorage.getItem('activeCategorySlug');
    if (storedCategory && props.categories.some(c => c.slug === storedCategory)) {
      activeCategorySlug.value = storedCategory;
    }
  }
  
  const selectCategory = (categorySlug) => {
    const button = event.currentTarget;
    button.style.transform = 'scale(0.95)';
    setTimeout(() => {
      button.style.transform = '';
    }, 150);
    
    activeCategorySlug.value = categorySlug;
    emit('filter', categorySlug);
    emit('change', categorySlug);
    
    if (props.persistSelection) {
      localStorage.setItem('activeCategorySlug', categorySlug);
    }
  };
  
  watch(() => props.initialActiveSlug, (newSlug) => {
    if (newSlug !== activeCategorySlug.value) {
      activeCategorySlug.value = newSlug;
    }
  });
  </script>