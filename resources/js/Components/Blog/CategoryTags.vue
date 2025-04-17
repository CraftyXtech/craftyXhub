<script setup>
import { ref } from 'vue';

const props = defineProps({
    categories: {
        type: Array,
        required: true // Expect categories to be passed in now
        // Expected structure: [{ id: Number|String, name: String, slug: String }]
    },
    initialActiveSlug: {
        type: String,
        default: 'all' // Default to the 'all' slug
    }
});

const emit = defineEmits(['filter']);

// Track the active category *slug*
const activeCategorySlug = ref(props.initialActiveSlug);

const selectCategory = (categorySlug) => {
    activeCategorySlug.value = categorySlug;
    emit('filter', categorySlug);
};
</script>

<template>
    <div class="flex justify-center items-center gap-2 flex-wrap mb-8">
        <button
            v-for="category in categories"
            :key="category.slug" 
            :class="[
                'px-4 py-2 text-sm border rounded-full transition duration-200',
                activeCategorySlug === category.slug 
                    ? 'bg-primary text-white border-primary dark:bg-primary-light dark:text-gray-900 dark:border-primary-light'
                    : 'bg-white text-gray-600 border-gray-200 hover:bg-gray-50 dark:bg-gray-700 dark:text-gray-300 dark:border-gray-600 dark:hover:bg-gray-600'
            ]"
            @click="selectCategory(category.slug)" 
        >
            {{ category.name }}
        </button>
    </div>
</template> 