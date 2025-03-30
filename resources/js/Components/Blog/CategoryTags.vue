<script setup>
import { ref } from 'vue';

const props = defineProps({
    categories: {
        type: Array,
        default: () => [
            { id: 0, name: 'All' },
            { id: 1, name: 'Technology' },
            { id: 2, name: 'Crafts' },
            { id: 3, name: 'DIY' },
            { id: 4, name: 'Art' },
            { id: 5, name: 'Jewelry' },
            { id: 6, name: 'Handmade' },
            { id: 7, name: 'Community' }
        ]
    },
    initialActive: {
        type: Number,
        default: 0 // 'All' category by default
    }
});

const emit = defineEmits(['filter']);

// Track the active category
const activeCategory = ref(props.initialActive);

const selectCategory = (categoryId) => {
    activeCategory.value = categoryId;
    emit('filter', categoryId);
};
</script>

<template>
    <div class="flex justify-center items-center gap-2 flex-wrap mb-8">
        <button 
            v-for="category in categories" 
            :key="category.id"
            :class="[
                'px-4 py-2 text-sm border rounded-full transition duration-200',
                activeCategory === category.id 
                    ? 'bg-primary text-white border-primary' 
                    : 'bg-white text-gray-600 border-gray-200 hover:bg-gray-50'
            ]"
            @click="selectCategory(category.id)"
        >
            {{ category.name }}
        </button>
    </div>
</template> 