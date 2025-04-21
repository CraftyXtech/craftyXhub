<script setup>
defineProps({
    message: {
        type: String,
        required: true
    },
    dismissible: {
        type: Boolean,
        default: false
    }
});

const emit = defineEmits(['dismiss']);
</script>

<template>
    <div 
        class="bg-red-50 dark:bg-red-900/50 border border-red-200 dark:border-red-800 rounded-lg p-4 mb-4 flex items-start justify-between"
        role="alert"
    >
        <div class="flex items-start">
            <div class="flex-shrink-0">
                <span class="material-icons text-red-600 dark:text-red-400">error</span>
            </div>
            <div class="ml-3">
                <p class="text-sm text-red-700 dark:text-red-200">{{ message }}</p>
            </div>
        </div>
        <button 
            v-if="dismissible"
            type="button"
            class="ml-auto -mx-1.5 -my-1.5 bg-red-50 dark:bg-red-900/50 text-red-500 dark:text-red-400 rounded-lg focus:ring-2 focus:ring-red-400 p-1.5 hover:bg-red-100 dark:hover:bg-red-800 inline-flex items-center justify-center h-8 w-8"
            @click="emit('dismiss')"
        >
            <span class="sr-only">Dismiss</span>
            <span class="material-icons text-sm">close</span>
        </button>
    </div>
</template> 