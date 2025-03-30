<script setup>
import { ref } from 'vue';

const emit = defineEmits(['search']);
const searchQuery = ref('');

const handleSearch = () => {
    // Only emit if there's actual content to search
    if (searchQuery.value.trim()) {
        emit('search', searchQuery.value.trim());
    }
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
            class="w-full pl-4 pr-10 py-2 border border-gray-300 rounded-full focus:outline-none focus:ring-2 focus:ring-primary focus:border-primary"
            @keypress="handleKeyPress"
        >
        <button 
            class="absolute right-2 top-1/2 transform -translate-y-1/2 text-gray-500 hover:text-primary"
            @click="handleSearch"
        >
            <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
            </svg>
        </button>
    </div>
</template> 