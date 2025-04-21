<script setup>
import { ref, watch, computed } from 'vue';

const props = defineProps({
    modelValue: {
        type: Array,
        default: () => []
    },
    availableTags: {
        type: Array,
        default: () => []
    },
    placeholder: {
        type: String,
        default: 'Select tags...'
    },
    maxTags: {
        type: Number,
        default: 5
    }
});

const emit = defineEmits(['update:modelValue']);

const searchQuery = ref('');
const showDropdown = ref(false);
const selectedTags = ref(props.modelValue);

const filteredTags = computed(() => {
    if (!searchQuery.value) return props.availableTags.filter(tag => !selectedTags.value.includes(tag));
    
    return props.availableTags.filter(tag => 
        tag.name.toLowerCase().includes(searchQuery.value.toLowerCase()) && 
        !selectedTags.value.includes(tag)
    );
});

const addTag = (tag) => {
    if (selectedTags.value.length >= props.maxTags) return;
    selectedTags.value = [...selectedTags.value, tag];
    emit('update:modelValue', selectedTags.value);
    searchQuery.value = '';
    showDropdown.value = false;
};

const removeTag = (tagToRemove) => {
    selectedTags.value = selectedTags.value.filter(tag => tag.id !== tagToRemove.id);
    emit('update:modelValue', selectedTags.value);
};

watch(() => props.modelValue, (newValue) => {
    selectedTags.value = newValue;
}, { deep: true });

const focusInput = () => {
    showDropdown.value = true;
};

const blurInput = () => {
    setTimeout(() => {
        showDropdown.value = false;
    }, 200);
};
</script>

<template>
    <div class="relative">
        <div 
            class="min-h-[42px] p-1 border rounded-md bg-white dark:bg-gray-700 flex flex-wrap gap-2 cursor-text"
            :class="{ 
                'border-red-500 dark:border-red-400': false,
                'border-gray-300 dark:border-gray-600': true
            }"
            @click="focusInput"
        >
            <!-- Selected Tags -->
            <span 
                v-for="tag in selectedTags" 
                :key="tag.id"
                class="inline-flex items-center px-2 py-1 rounded-md text-sm bg-primary-100 text-primary-800 dark:bg-primary-900 dark:text-primary-200"
            >
                {{ tag.name }}
                <button 
                    type="button" 
                    class="ml-1 hover:text-primary-600 dark:hover:text-primary-400"
                    @click.stop="removeTag(tag)"
                >
                    <span class="material-icons text-sm">close</span>
                </button>
            </span>
            
            <!-- Input Field -->
            <input
                type="text"
                v-model="searchQuery"
                :placeholder="selectedTags.length === 0 ? placeholder : ''"
                class="flex-1 min-w-[60px] bg-transparent border-none focus:ring-0 p-1 text-gray-900 dark:text-gray-100"
                @focus="focusInput"
                @blur="blurInput"
            >
        </div>

        <!-- Dropdown -->
        <div 
            v-if="showDropdown && filteredTags.length > 0" 
            class="absolute z-50 w-full mt-1 bg-white dark:bg-gray-700 border border-gray-200 dark:border-gray-600 rounded-md shadow-lg"
        >
            <ul class="py-1 max-h-60 overflow-auto">
                <li 
                    v-for="tag in filteredTags" 
                    :key="tag.id"
                    class="px-3 py-2 hover:bg-gray-100 dark:hover:bg-gray-600 cursor-pointer text-gray-900 dark:text-gray-100"
                    @mousedown.prevent="addTag(tag)"
                >
                    {{ tag.name }}
                </li>
            </ul>
        </div>

        <!-- Max Tags Warning -->
        <p v-if="selectedTags.length >= maxTags" class="mt-1 text-sm text-yellow-600 dark:text-yellow-400">
            Maximum number of tags reached ({{ maxTags }})
        </p>
    </div>
</template> 