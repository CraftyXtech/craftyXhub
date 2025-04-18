<template>
  <div class="space-y-8 p-6 bg-gray-50 dark:bg-gray-900 rounded-lg">
    <h2 class="text-xl font-semibold">Loading Indicator Examples</h2>
    
    <!-- Default LoadingIndicator (medium size with default text) -->
    <div class="p-4 border border-gray-200 dark:border-gray-700 rounded-lg">
      <h3 class="text-sm font-medium mb-2">Default (Medium)</h3>
      <LoadingIndicator />
    </div>
    
    <!-- Small LoadingIndicator with custom text -->
    <div class="p-4 border border-gray-200 dark:border-gray-700 rounded-lg">
      <h3 class="text-sm font-medium mb-2">Small with Custom Text</h3>
      <LoadingIndicator size="small" text="Fetching data..." />
    </div>
    
    <!-- Large LoadingIndicator with custom text -->
    <div class="p-4 border border-gray-200 dark:border-gray-700 rounded-lg">
      <h3 class="text-sm font-medium mb-2">Large with Custom Text</h3>
      <LoadingIndicator size="large" text="Processing your request..." />
    </div>
    
    <!-- Extra Large LoadingIndicator without text -->
    <div class="p-4 border border-gray-200 dark:border-gray-700 rounded-lg">
      <h3 class="text-sm font-medium mb-2">Extra Large without Text</h3>
      <LoadingIndicator size="xl" text="" />
    </div>
    
    <!-- Loading indicator in a real-world scenario -->
    <div class="p-4 border border-gray-200 dark:border-gray-700 rounded-lg">
      <h3 class="text-sm font-medium mb-2">In a Data Loading Context</h3>
      <button 
        @click="fetchData" 
        class="mb-4 px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 transition"
      >
        Fetch Data
      </button>
      
      <div v-if="loading" class="bg-white dark:bg-gray-800 p-6 rounded-lg shadow">
        <LoadingIndicator size="medium" text="Fetching report data..." />
      </div>
      
      <div v-else class="bg-white dark:bg-gray-800 p-6 rounded-lg shadow">
        <p>{{ data || 'Click "Fetch Data" to load content' }}</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import LoadingIndicator from '@/Components/LoadingIndicator.vue';

const loading = ref(false);
const data = ref(null);

const fetchData = () => {
  loading.value = true;
  data.value = null;
  
  // Simulate API call with setTimeout
  setTimeout(() => {
    data.value = 'Data loaded successfully! This is your report data.';
    loading.value = false;
  }, 2000); // 2 second delay to show loading state
};
</script> 