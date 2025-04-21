<script setup>
import { computed, ref, watch } from 'vue';
import { Link, router, useForm } from '@inertiajs/vue3';
import PrimaryButton from '@/Components/PrimaryButton.vue';
import SecondaryButton from '@/Components/SecondaryButton.vue';
import DangerButton from '@/Components/DangerButton.vue';
import Pagination from '@/Components/Pagination.vue';
import LoadingIndicator from '@/Components/LoadingIndicator.vue';
import ErrorMessage from '@/Components/ErrorMessage.vue';

const props = defineProps({
    posts: Object,
    filters: Object,
});

const emit = defineEmits(['update:filters']);

// Loading and error states
const loading = ref(false);
const error = ref(null);
const deletingPostId = ref(null);
const deleteError = ref(null);

const selectedItems = ref([]);
const searchQuery = ref(props.filters?.search || '');
const statusFilter = ref(props.filters?.status || 'all');

// Watch for changes in filter values
watch(searchQuery, (value) => {
    updateFilters({ search: value });
});

watch(statusFilter, (value) => {
    updateFilters({ status: value });
});

// Update filters and emit to parent
const updateFilters = (newFilters) => {
    emit('update:filters', { 
        ...props.filters, 
        ...newFilters,
        page: newFilters.page || 1 // Reset to page 1 when filters change
    });
};

// Format date
const formatDate = (dateString) => {
    if (!dateString) return 'N/A';
    const date = new Date(dateString);
    return new Intl.DateTimeFormat('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
    }).format(date);
};

// Get status badge class
const getStatusClass = (status) => {
    switch (status) {
        case 'published':
            return 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200';
        case 'draft':
            return 'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-200';
        case 'under_review':
            return 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200';
        case 'scheduled':
            return 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200';
        case 'rejected':
            return 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200';
        default:
            return 'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-200';
    }
};

// Format status text
const formatStatus = (status) => {
    switch (status) {
        case 'published':
            return 'Published';
        case 'draft':
            return 'Draft';
        case 'under_review':
            return 'Under Review';
        case 'scheduled':
            return 'Scheduled';
        case 'rejected':
            return 'Rejected';
        default:
            return status.charAt(0).toUpperCase() + status.slice(1);
    }
};

// Toggle selection of all items
const toggleSelectAll = () => {
    if (selectedItems.value.length === props.posts.data.length) {
        selectedItems.value = [];
    } else {
        selectedItems.value = props.posts.data.map(post => post.id);
    }
};

// Toggle selection of a single item
const toggleSelectItem = (postId) => {
    const index = selectedItems.value.indexOf(postId);
    if (index === -1) {
        selectedItems.value.push(postId);
    } else {
        selectedItems.value.splice(index, 1);
    }
};

// Check if an item is selected
const isSelected = (postId) => {
    return selectedItems.value.includes(postId);
};

// --- Refactored Delete Post (using Inertia link/router) --- 
const confirmAndDeletePost = (postId) => {
    if (!confirm('Are you sure you want to delete this post?')) {
        return;
    }
    router.delete(route('editor.posts.destroy', postId), { // Use the correct route name (likely from resource)
        preserveScroll: true,
        onStart: () => { deletingPostId.value = postId; deleteError.value = null; },
        onError: (errors) => { 
            deleteError.value = errors.message || 'Failed to delete post';
            console.error("Delete error:", errors);
        },
        onFinish: () => { deletingPostId.value = null; },
        onSuccess: () => { selectedItems.value = selectedItems.value.filter(id => id !== postId); } // Remove from selection
    });
};

// --- Refactored Bulk Actions (using useForm) --- 
const bulkActionForm = useForm({
    action: '', // Bound to the select dropdown
    ids: [],    // Will be populated before submit
});

const bulkActionsOptions = [
    { value: '', label: 'Bulk Actions' },
    { value: 'delete', label: 'Delete Selected' },
    { value: 'publish', label: 'Publish Selected' },
    { value: 'draft', label: 'Move to Draft' },
    { value: 'review', label: 'Submit for Review' },
    { value: 'reject', label: 'Reject Selected' }, // Add reject if implemented
];

const applyBulkAction = () => {
    if (!bulkActionForm.action || selectedItems.value.length === 0) {
        return;
    }

    if (bulkActionForm.action === 'delete' && !confirm(`Are you sure you want to delete ${selectedItems.value.length} selected posts?`)) {
        bulkActionForm.reset('action');
        return;
    }

    bulkActionForm.ids = [...selectedItems.value]; // Copy selected items to form

    bulkActionForm.post(route('editor.posts.bulk-action'), { // Use the new route name
        preserveScroll: true,
        onSuccess: () => {
            selectedItems.value = []; // Clear selection on success
            bulkActionForm.reset(); // Reset form fields
            // Post list updates automatically due to redirect
        },
        onError: (errors) => {
            // Validation errors are in bulkActionForm.errors
            error.value = errors.message || 'Failed to apply bulk action.'; // Display general error
            console.error('Bulk action error:', errors);
        },
        onFinish: () => {
            // bulkActionForm.processing resets automatically
        }
    });
};

// Handle retry after error (might need adjustment depending on form state)
const retryAction = () => {
    error.value = null;
    deleteError.value = null;
    // Reloading might still be simplest way to clear potential issues
    router.reload({ only: ['posts'] }); 
};
</script>

<template>
    <div class="bg-white dark:bg-gray-800 overflow-hidden shadow-sm sm:rounded-lg">
        <div class="p-6">
            <div class="mb-6 flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
                <h3 class="text-lg font-medium text-gray-900 dark:text-gray-100">
                    Content Management
                </h3>
                <div class="flex flex-wrap gap-3">
                    <div class="flex items-center space-x-2">
                        <input 
                            v-model="searchQuery"
                            type="text" 
                            placeholder="Search posts..." 
                            class="rounded-md border-gray-300 dark:border-gray-700 dark:bg-gray-900 dark:text-gray-300 focus:border-indigo-500 dark:focus:border-indigo-600 focus:ring-indigo-500 dark:focus:ring-indigo-600 shadow-sm"
                        >
                    </div>
                    
                    <select 
                        v-model="statusFilter"
                        class="rounded-md border-gray-300 dark:border-gray-700 dark:bg-gray-900 dark:text-gray-300 focus:border-indigo-500 dark:focus:border-indigo-600 focus:ring-indigo-500 dark:focus:ring-indigo-600 shadow-sm"
                    >
                        <option value="all">All Status</option>
                        <option value="published">Published</option>
                        <option value="draft">Draft</option>
                        <option value="under_review">Under Review</option>
                        <option value="scheduled">Scheduled</option>
                        <option value="rejected">Rejected</option>
                    </select>
                </div>
            </div>
            
            <!-- Error handling -->
            <ErrorMessage 
                v-if="error || bulkActionForm.hasErrors" 
                :message="error || bulkActionForm.errors.ids || bulkActionForm.errors.action || 'An error occurred.'"
                :retry="retryAction"
            />

            <!-- Bulk actions -->
            <div v-if="selectedItems.length > 0" class="mb-4 flex items-center space-x-2">
                <!-- Bind select to bulkActionForm.action -->
                <select 
                    v-model="bulkActionForm.action"
                    class="rounded-md border-gray-300 dark:border-gray-700 dark:bg-gray-900 dark:text-gray-300 focus:border-indigo-500 dark:focus:border-indigo-600 focus:ring-indigo-500 dark:focus:ring-indigo-600 shadow-sm"
                    :disabled="bulkActionForm.processing"
                >
                    <option 
                        v-for="option in bulkActionsOptions" 
                        :key="option.value" 
                        :value="option.value"
                    >
                        {{ option.label }}
                    </option>
                </select>
                
                <!-- Disable button based on form state -->
                <SecondaryButton 
                    @click="applyBulkAction"
                    :disabled="bulkActionForm.processing || !bulkActionForm.action"
                >
                    <span v-if="bulkActionForm.processing">Processing...</span>
                    <span v-else>Apply</span>
                </SecondaryButton>
                
                <span class="text-sm text-gray-600 dark:text-gray-400">
                    {{ selectedItems.length }} item(s) selected
                </span>
            </div>

            <!-- Loading indicator -->
            <!-- Use router.processing or a dedicated loading ref if needed -->
            <div v-if="loading && !posts"> 
                <LoadingIndicator />
            </div>
            
            <!-- Posts table -->
            <div v-else-if="posts && posts.data.length > 0" class="overflow-x-auto">
                <table class="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
                    <thead class="bg-gray-50 dark:bg-gray-700">
                        <tr>
                            <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                                <div class="flex items-center">
                                    <input 
                                        type="checkbox"
                                        @change="toggleSelectAll"
                                        :checked="selectedItems.length === posts.data.length && posts.data.length > 0"
                                        class="rounded border-gray-300 text-indigo-600 shadow-sm focus:ring-indigo-500 dark:border-gray-700 dark:bg-gray-900 dark:focus:ring-indigo-600"
                                    >
                                </div>
                            </th>
                            <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                                Title
                            </th>
                            <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                                Status
                            </th>
                            <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                                Date
                            </th>
                            <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                                Views
                            </th>
                            <th scope="col" class="px-6 py-3 text-right text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                                Actions
                            </th>
                        </tr>
                    </thead>
                    <tbody class="bg-white dark:bg-gray-800 divide-y divide-gray-200 dark:divide-gray-700">
                        <tr v-for="post in posts.data" :key="post.id" class="hover:bg-gray-50 dark:hover:bg-gray-700/50">
                            <td class="px-6 py-4 whitespace-nowrap">
                                <div class="flex items-center">
                                    <input 
                                        type="checkbox"
                                        :checked="isSelected(post.id)"
                                        @change="toggleSelectItem(post.id)"
                                        class="rounded border-gray-300 text-indigo-600 shadow-sm focus:ring-indigo-500 dark:border-gray-700 dark:bg-gray-900 dark:focus:ring-indigo-600"
                                    >
                                </div>
                            </td>
                            <td class="px-6 py-4">
                                <div class="text-sm font-medium text-gray-900 dark:text-gray-100">
                                    {{ post.title }}
                                </div>
                                <div v-if="post.excerpt" class="text-sm text-gray-500 dark:text-gray-400 truncate max-w-xs">
                                    {{ post.excerpt }}
                                </div>
                            </td>
                            <td class="px-6 py-4 whitespace-nowrap">
                                <span class="px-2 py-1 inline-flex text-xs leading-5 font-semibold rounded-full" :class="getStatusClass(post.status)">
                                    {{ formatStatus(post.status) }}
                                </span>
                            </td>
                            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">
                                {{ formatDate(post.created_at) }}
                            </td>
                            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">
                                {{ post.views || 0 }}
                            </td>
                            <td class="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                                <Link :href="route('editor.posts.edit', post.id)" class="text-indigo-600 hover:text-indigo-900 dark:text-indigo-400 dark:hover:text-indigo-300 mr-3">Edit</Link>
                                
                                <!-- Use refactored delete method -->
                                <button 
                                    @click="confirmAndDeletePost(post.id)" 
                                    class="text-red-600 hover:text-red-900 dark:text-red-400 dark:hover:text-red-300"
                                    :disabled="deletingPostId === post.id"
                                >
                                    <span v-if="deletingPostId === post.id">Deleting...</span>
                                    <span v-else>Delete</span>
                                </button>
                                <div v-if="deleteError && deletingPostId === post.id" class="text-red-500 text-xs mt-1">
                                    {{ deleteError }}
                                </div>
                            </td>
                        </tr>
                    </tbody>
                </table>
            </div>
            <div v-else class="text-center py-8 text-gray-500 dark:text-gray-400">
                No posts found matching your criteria.
            </div>

             <!-- Pagination (Using Inertia links) -->
            <div class="mt-6" v-if="posts?.links?.length > 3">
                 <Pagination :links="posts.links" />
            </div>
        </div>
    </div>
</template> 