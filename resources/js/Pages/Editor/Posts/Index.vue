<script setup>
import AuthenticatedLayout from '@/Layouts/AuthenticatedLayout.vue';
import { Head, Link, router } from '@inertiajs/vue3';
import { ref, watch } from 'vue';
import PrimaryButton from '@/Components/PrimaryButton.vue';
import SecondaryButton from '@/Components/SecondaryButton.vue';
import DangerButton from '@/Components/DangerButton.vue';
import Dropdown from '@/Components/Dropdown.vue';
import DropdownLink from '@/Components/DropdownLink.vue';
import InputLabel from '@/Components/InputLabel.vue';
import TextInput from '@/Components/TextInput.vue';
import Pagination from '@/Components/Pagination.vue';
import Modal from '@/Components/Modal.vue';

const props = defineProps({
    posts: Object,
    filters: Object,
    categories: Array,
    canCreate: Boolean,
    canPublish: Boolean
});

const search = ref(props.filters.search || '');
const status = ref(props.filters.status || '');
const category = ref(props.filters.category || '');
const showDeleteModal = ref(false);
const postToDelete = ref(null);

// Format date to readable format
const formatDate = (dateString) => {
    if (!dateString) return 'N/A';
    const date = new Date(dateString);
    return new Intl.DateTimeFormat('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    }).format(date);
};

// Get status badge class
const getStatusClass = (status) => {
    const statusMap = {
        'published': 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200',
        'draft': 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200',
        'scheduled': 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200',
        'rejected': 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200',
        'under_review': 'bg-purple-100 text-purple-800 dark:bg-purple-900 dark:text-purple-200'
    };
    return statusMap[status] || 'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-300';
};

// Format status text
const formatStatus = (status) => {
    return status
        .split('_')
        .map(word => word.charAt(0).toUpperCase() + word.slice(1))
        .join(' ');
};

// Apply filters when they change
watch([search, status, category], ([newSearch, newStatus, newCategory]) => {
    router.get(
        route('editor.posts.index'),
        {
            search: newSearch,
            status: newStatus,
            category: newCategory,
        },
        {
            preserveState: true,
            replace: true,
            preserveScroll: true,
        }
    );
}, { debounce: 300 });

// Debounce search input
let searchTimeout;
const debouncedSearch = (e) => {
    clearTimeout(searchTimeout);
    const value = e.target.value;
    searchTimeout = setTimeout(() => {
        search.value = value;
    }, 300);
};

// Handle delete post
const confirmDelete = (post) => {
    postToDelete.value = post;
    showDeleteModal.value = true;
};

const deletePost = () => {
    router.delete(route('editor.posts.destroy', postToDelete.value.id), {
        onSuccess: () => {
            showDeleteModal.value = false;
            postToDelete.value = null;
        },
    });
};

const cancelDelete = () => {
    showDeleteModal.value = false;
    postToDelete.value = null;
};

// Clear all filters
const clearFilters = () => {
    search.value = '';
    status.value = '';
    category.value = '';
};
</script>

<template>
    <Head title="Manage Posts" />

    <AuthenticatedLayout>
        <template #header>
            <div class="flex justify-between items-center">
                <h2 class="font-semibold text-xl text-gray-800 dark:text-gray-200 leading-tight">
                    Manage Posts
                </h2>
                <Link 
                    v-if="canCreate"
                    :href="route('editor.posts.create')" 
                    class="inline-flex items-center px-4 py-2 bg-indigo-600 border border-transparent rounded-md font-semibold text-xs text-white uppercase tracking-widest hover:bg-indigo-700 focus:bg-indigo-700 active:bg-indigo-900 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 dark:focus:ring-offset-gray-800 transition ease-in-out duration-150"
                >
                    New Post
                </Link>
            </div>
        </template>

        <div class="py-12">
            <div class="max-w-7xl mx-auto sm:px-6 lg:px-8">
                <div class="bg-white dark:bg-gray-800 overflow-hidden shadow-sm sm:rounded-lg">
                    <div class="p-6">
                        <!-- Filters -->
                        <div class="flex flex-col sm:flex-row gap-4 items-end sm:items-center mb-6">
                            <div class="w-full sm:w-1/3">
                                <InputLabel for="search" value="Search" class="mb-1" />
                                <TextInput
                                    id="search"
                                    type="text"
                                    class="w-full"
                                    placeholder="Search by title or content"
                                    :value="search"
                                    @input="debouncedSearch"
                                />
                            </div>
                            <div class="w-full sm:w-1/4">
                                <InputLabel for="status" value="Status" class="mb-1" />
                                <select
                                    id="status"
                                    v-model="status"
                                    class="w-full border-gray-300 dark:border-gray-700 dark:bg-gray-900 dark:text-gray-300 focus:border-indigo-500 dark:focus:border-indigo-600 focus:ring-indigo-500 dark:focus:ring-indigo-600 rounded-md shadow-sm"
                                >
                                    <option value="">All Statuses</option>
                                    <option value="draft">Draft</option>
                                    <option value="under_review">Under Review</option>
                                    <option value="published">Published</option>
                                    <option value="scheduled">Scheduled</option>
                                    <option value="rejected">Rejected</option>
                                </select>
                            </div>
                            <div class="w-full sm:w-1/4">
                                <InputLabel for="category" value="Category" class="mb-1" />
                                <select
                                    id="category"
                                    v-model="category"
                                    class="w-full border-gray-300 dark:border-gray-700 dark:bg-gray-900 dark:text-gray-300 focus:border-indigo-500 dark:focus:border-indigo-600 focus:ring-indigo-500 dark:focus:ring-indigo-600 rounded-md shadow-sm"
                                >
                                    <option value="">All Categories</option>
                                    <option 
                                        v-for="cat in categories" 
                                        :key="cat.id" 
                                        :value="cat.id"
                                    >
                                        {{ cat.name }}
                                    </option>
                                </select>
                            </div>
                            <div class="w-full sm:w-auto sm:ml-auto">
                                <SecondaryButton 
                                    @click="clearFilters"
                                    :disabled="!search && !status && !category"
                                    class="w-full sm:w-auto"
                                >
                                    Clear Filters
                                </SecondaryButton>
                            </div>
                        </div>

                        <!-- Posts Table -->
                        <div class="overflow-x-auto">
                            <table class="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
                                <thead class="bg-gray-50 dark:bg-gray-700">
                                    <tr>
                                        <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                                            Title
                                        </th>
                                        <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                                            Status
                                        </th>
                                        <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                                            Category
                                        </th>
                                        <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                                            Created
                                        </th>
                                        <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                                            Updated
                                        </th>
                                        <th scope="col" class="px-6 py-3 text-right text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                                            Actions
                                        </th>
                                    </tr>
                                </thead>
                                <tbody class="bg-white dark:bg-gray-800 divide-y divide-gray-200 dark:divide-gray-700">
                                    <tr v-if="posts.data.length === 0">
                                        <td colspan="6" class="px-6 py-4 text-center text-gray-500 dark:text-gray-400">
                                            No posts found. 
                                            <Link v-if="canCreate" :href="route('editor.posts.create')" class="text-indigo-600 dark:text-indigo-400 hover:underline">
                                                Create a new post
                                            </Link>
                                        </td>
                                    </tr>
                                    <tr v-for="post in posts.data" :key="post.id" class="hover:bg-gray-50 dark:hover:bg-gray-700">
                                        <td class="px-6 py-4 whitespace-nowrap">
                                            <div class="text-sm font-medium text-gray-900 dark:text-gray-100">
                                                {{ post.title }}
                                            </div>
                                            <div v-if="post.feedback && post.status === 'rejected'" class="text-xs text-red-600 dark:text-red-400 mt-1">
                                                Has feedback
                                            </div>
                                        </td>
                                        <td class="px-6 py-4 whitespace-nowrap">
                                            <span class="px-2 py-1 text-xs rounded-full" :class="getStatusClass(post.status)">
                                                {{ formatStatus(post.status) }}
                                            </span>
                                        </td>
                                        <td class="px-6 py-4 whitespace-nowrap">
                                            <div class="text-sm text-gray-500 dark:text-gray-400">
                                                {{ post.category ? post.category.name : 'Uncategorized' }}
                                            </div>
                                        </td>
                                        <td class="px-6 py-4 whitespace-nowrap">
                                            <div class="text-sm text-gray-500 dark:text-gray-400">
                                                {{ formatDate(post.created_at) }}
                                            </div>
                                        </td>
                                        <td class="px-6 py-4 whitespace-nowrap">
                                            <div class="text-sm text-gray-500 dark:text-gray-400">
                                                {{ formatDate(post.updated_at) }}
                                            </div>
                                        </td>
                                        <td class="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                                            <Dropdown>
                                                <template #trigger>
                                                    <button class="inline-flex items-center text-sm text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300">
                                                        <span class="sr-only">Actions</span>
                                                        <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                                                            <path d="M10 6a2 2 0 110-4 2 2 0 010 4zM10 12a2 2 0 110-4 2 2 0 010 4zM10 18a2 2 0 110-4 2 2 0 010 4z" />
                                                        </svg>
                                                    </button>
                                                </template>

                                                <template #content>
                                                    <DropdownLink :href="route('editor.posts.edit', post.id)">
                                                        Edit
                                                    </DropdownLink>
                                                    <DropdownLink 
                                                        v-if="post.status === 'published'"
                                                        :href="route('posts.show', post.slug)" 
                                                        target="_blank"
                                                    >
                                                        View
                                                    </DropdownLink>
                                                    <DropdownLink 
                                                        v-if="post.status === 'draft'"
                                                        :href="route('editor.posts.submit', post.id)" 
                                                        method="post" 
                                                        as="button"
                                                    >
                                                        Submit for Review
                                                    </DropdownLink>
                                                    <DropdownLink 
                                                        as="button" 
                                                        class="text-red-600 dark:text-red-400" 
                                                        @click="confirmDelete(post)"
                                                    >
                                                        Delete
                                                    </DropdownLink>
                                                </template>
                                            </Dropdown>
                                        </td>
                                    </tr>
                                </tbody>
                            </table>
                        </div>

                        <!-- Pagination -->
                        <div class="mt-6">
                            <Pagination :links="posts.links" />
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <!-- Delete Confirmation Modal -->
        <Modal :show="showDeleteModal" @close="cancelDelete">
            <div class="p-6">
                <h2 class="text-lg font-medium text-gray-900 dark:text-gray-100 mb-4">
                    Delete Post
                </h2>

                <p class="text-gray-600 dark:text-gray-400 mb-6">
                    Are you sure you want to delete this post? This action cannot be undone.
                </p>

                <div class="flex justify-end">
                    <SecondaryButton class="mr-2" @click="cancelDelete">
                        Cancel
                    </SecondaryButton>
                    <DangerButton @click="deletePost">
                        Delete
                    </DangerButton>
                </div>
            </div>
        </Modal>
    </AuthenticatedLayout>
</template> 