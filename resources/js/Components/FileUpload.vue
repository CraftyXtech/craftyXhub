<template>
  <div>
    <input 
      type="file" 
      :accept="accept"
      @change="handleFileChange"
      ref="fileInput"
      class="block w-full text-sm text-gray-500 dark:text-gray-400 file:mr-4 file:py-2 file:px-4 file:rounded-md file:border-0 file:text-sm file:font-semibold file:bg-indigo-50 dark:file:bg-indigo-900 file:text-indigo-700 dark:file:text-indigo-300 hover:file:bg-indigo-100 dark:hover:file:bg-indigo-800 cursor-pointer border border-gray-300 dark:border-gray-700 rounded-md p-1"
    />
    <p v-if="error" class="mt-1 text-sm text-red-600 dark:text-red-400">{{ error }}</p>
  </div>
</template>

<script setup>
import { ref } from 'vue';

const props = defineProps({
    accept: {
        type: String,
        default: '*/*'
    }
});

const emit = defineEmits(['file-selected']);

const fileInput = ref(null);
const error = ref(null);

const handleFileChange = (event) => {
    error.value = null;
    const file = event.target.files[0];
    if (file) {
        // Basic validation example (can be expanded)
        if (!props.accept.includes('*') && !props.accept.includes(file.type.split('/')[0]) && !props.accept.includes(file.type)) {
             error.value = `Invalid file type. Please select a file of type: ${props.accept}`;
             event.target.value = null; // Clear the input
             return;
        }
        emit('file-selected', file);
    } else {
        emit('file-selected', null);
    }
};

// Expose a method to trigger the file input click programmatically if needed
const triggerFileInput = () => {
    fileInput.value?.click();
};
defineExpose({ triggerFileInput });

</script>

<style scoped>
/* Add any specific styles if needed */
</style> 