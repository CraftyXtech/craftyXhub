<script setup>
defineProps({
    message: {
        type: String,
        default: 'An error occurred.'
    },
    showRetry: {
        type: Boolean,
        default: false
    }
});

const emit = defineEmits(['retry']);

const handleRetry = () => {
    emit('retry');
};
</script>

<template>
    <div class="bg-red-50 dark:bg-red-900/20 p-4 rounded-md my-4">
        <div class="flex">
            <div class="flex-shrink-0">
                <svg class="h-5 w-5 text-red-400 dark:text-red-500" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" aria-hidden="true">
                    <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd" />
                </svg>
            </div>
            <div class="ml-3">
                <h3 class="text-sm font-medium text-red-800 dark:text-red-200">
                    Error
                </h3>
                <div class="mt-2 text-sm text-red-700 dark:text-red-300">
                    <p>{{ message }}</p>
                </div>
                <div v-if="showRetry" class="mt-4">
                    <button
                        type="button"
                        class="inline-flex items-center px-3 py-2 border border-transparent text-sm leading-4 font-medium rounded-md text-white bg-red-600 hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500 dark:focus:ring-offset-gray-800"
                        @click="handleRetry"
                    >
                        Retry
                    </button>
                </div>
            </div>
        </div>
    </div>
</template> 