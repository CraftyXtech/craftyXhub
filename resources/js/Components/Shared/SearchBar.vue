<script setup>
import { ref, watch } from 'vue';

const props = defineProps({
  modelValue: {
    type: String,
    default: ''
  }
});

const emit = defineEmits(['update:modelValue', 'search', 'clear']);

// Use a local ref that stays in sync with the modelValue prop
const searchQuery = ref(props.modelValue);

// Watch for changes to modelValue from parent
watch(() => props.modelValue, (newValue) => {
  searchQuery.value = newValue;
});

// Update the parent whenever the local value changes
watch(searchQuery, (newValue) => {
  emit('update:modelValue', newValue);
});

const handleSearch = () => {
  // Only emit if there's actual content to search
  if (searchQuery.value.trim()) {
    emit('search', searchQuery.value.trim());
  }
};

const clearSearch = () => {
  searchQuery.value = '';
  emit('update:modelValue', '');
  emit('clear');
};

const handleKeyPress = (event) => {
  if (event.key === 'Enter') {
    handleSearch();
  }
};
</script>

<template>
  <div class="relative max-w-md mx-auto">
    <input
      v-model="searchQuery"
      type="search"
      placeholder="Search for projects and tutorials"
      class="w-full pl-4 pr-10 py-2 border border-gray-300 dark:border-gray-600 rounded-full bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-200 focus:outline-none focus:ring-2 focus:ring-primary dark:focus:ring-primary-light focus:border-primary dark:focus:border-primary-light"
      @keypress="handleKeyPress"
    >
    <button
      class="absolute right-2 top-1/2 transform -translate-y-1/2 text-gray-500 hover:text-primary dark:text-gray-400 dark:hover:text-primary-light"
      @click="handleSearch"
    >
      <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
      </svg>
    </button>
    <button 
      v-if="searchQuery"
      class="absolute right-8 top-1/2 transform -translate-y-1/2 text-gray-500 hover:text-primary dark:text-gray-400 dark:hover:text-primary-light"
      @click="clearSearch"
    >
      <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
      </svg>
    </button>
  </div>
</template>