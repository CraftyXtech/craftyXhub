<script setup>
import AuthenticatedLayout from '@/Layouts/AuthenticatedLayout.vue';
import { Head, Link, router, usePage } from '@inertiajs/vue3';
import { ref, computed } from 'vue';
import PrimaryButton from '@/Components/PrimaryButton.vue';
import SecondaryButton from '@/Components/SecondaryButton.vue';
import DangerButton from '@/Components/DangerButton.vue';
import Dropdown from '@/Components/Dropdown.vue';
import DropdownLink from '@/Components/DropdownLink.vue';
import TextInput from '@/Components/TextInput.vue';
import InputLabel from '@/Components/InputLabel.vue';
import Pagination from '@/Components/Pagination.vue';
import Modal from '@/Components/Modal.vue';

const props = defineProps({
    drafts: Object,
    filters: Object,
    categories: Array,
});

const page = usePage();
const currentUserRole = computed(() => page.props.auth.user.role);
const isAdmin = computed(() => currentUserRole.value === 'admin');

// Add this function to get direct URLs that work across namespaces
const getDirectUrl = (path) => {
    return window.location.origin + path;
};

// Search functionality
const search = ref(props.filters.search || '');
const showDeleteModal = ref(false);
const draftToDelete = ref(null);

// Track which draft is being hovered
const hoveredDraftId = ref(null);

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

// Handle search input
const handleSearch = (e) => {
    router.get(
        route('editor.posts.drafts'),
        { search: e.target.value },
        { preserveState: true, replace: true, preserveScroll: true }
    );
};

// Handle delete post
const confirmDelete = (draft) => {
    draftToDelete.value = draft;
    showDeleteModal.value = true;
};

const deletePost = () => {
    if (!draftToDelete.value) return;
    
    router.delete(route('editor.posts.destroy', { post: draftToDelete.value.slug }), {
        onSuccess: () => {
            showDeleteModal.value = false;
            draftToDelete.value = null;
        },
        onError: (errors) => {
            console.error('Delete failed:', errors);
            // Keep modal open on error
        }
    });
};

const cancelDelete = () => {
    showDeleteModal.value = false;
    draftToDelete.value = null;
};

// Add the function to handle submit for review
const submitForReview = (postSlug) => {
    // Use direct URL approach instead of relying on the route helper
    const submitUrl = route('editor.posts.submit', { post: postSlug });
    
    router.post(submitUrl, {}, {
        onSuccess: () => {
            // Update directly in UI if needed
            router.reload({ only: ['drafts'] });
        },
        onError: (errors) => {
            console.error('Submit failed:', errors);
        }
    });
};

// Helper to handle row hover
const setHoveredDraft = (draftId) => {
    hoveredDraftId.value = draftId;
};

const clearHoveredDraft = () => {
    hoveredDraftId.value = null;
};
</script>

<template>
    <Head title="My Drafts" />

    <AuthenticatedLayout>
        <template #header>
            <div class="flex justify-between items-center">
                <h2 class="font-semibold text-xl text-gray-800 dark:text-gray-200 leading-tight">
                    My Draft Posts
                </h2>
                <Link
                    :href="route('editor.posts.create')" 
                    class="inline-flex items-center px-4 py-2 bg-indigo-600 border border-transparent rounded-md font-semibold text-xs text-white uppercase tracking-widest hover:bg-indigo-700 focus:bg-indigo-700 active:bg-indigo-900 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 dark:focus:ring-offset-gray-800 transition ease-in-out duration-150"
                >
                    New Post
                </Link>
            </div>
        </template>

        <div class="py-12">
            <div class="max-w-7xl mx-auto sm:px-6 lg:px-8">
                <!-- Flash Messages -->
                <div v-if="$page.props.flash.success" class="mb-4 bg-green-100 border-l-4 border-green-500 text-green-700 p-4 dark:bg-green-900 dark:text-green-100" role="alert">
                    <p>{{ $page.props.flash.success }}</p>
                </div>
                <div v-if="$page.props.flash.error" class="mb-4 bg-red-100 border-l-4 border-red-500 text-red-700 p-4 dark:bg-red-900 dark:text-red-100" role="alert">
                    <p>{{ $page.props.flash.error }}</p>
                </div>
                
                <div class="bg-white dark:bg-gray-800 overflow-hidden shadow-sm sm:rounded-lg">
                    <div class="p-6">
                        <!-- Search bar -->
                        <div class="mb-6">
                            <InputLabel for="search" value="Search Drafts" class="mb-1" />
                            <TextInput
                                id="search"
                                type="text"
                                class="w-full"
                                placeholder="Search drafts by title or content"
                                :value="search"
                                @input="handleSearch"
                            />
                        </div>

                        <!-- Drafts Table -->
                        <div class="overflow-x-auto">
                            <table class="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
                                <thead class="bg-gray-50 dark:bg-gray-700">
                                    <tr>
                                        <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                                            Title
                                        </th>
                                        <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                                            Category
                                        </th>
                                        <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                                            Created
                                        </th>
                                        <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                                            Last Updated
                                        </th>
                                        <th scope="col" class="px-6 py-3 text-right text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                                            Actions
                                        </th>
                                    </tr>
                                </thead>
                                <tbody class="bg-white dark:bg-gray-800 divide-y divide-gray-200 dark:divide-gray-700">
                                    <tr v-if="!drafts.data || drafts.data.length === 0">
                                        <td colspan="5" class="px-6 py-4 text-center text-gray-500 dark:text-gray-400">
                                            No drafts found. 
                                            <Link :href="route('editor.posts.create')" class="text-indigo-600 dark:text-indigo-400 hover:underline">
                                                Create a new post
                                            </Link>
                                        </td>
                                    </tr>
                                    <tr 
                                        v-for="draft in drafts.data" 
                                        :key="draft.id" 
                                        class="hover:bg-gray-50 dark:hover:bg-gray-700 relative"
                                        @mouseenter="setHoveredDraft(draft.id)" 
                                        @mouseleave="clearHoveredDraft()"
                                    >
                                        <td class="px-6 py-4 whitespace-nowrap">
                                            <div class="text-sm font-medium text-gray-900 dark:text-gray-100">
                                                {{ draft.title || 'Untitled Draft' }}
                                            </div>
                                        </td>
                                        <td class="px-6 py-4 whitespace-nowrap">
                                            <div class="text-sm text-gray-500 dark:text-gray-400">
                                                {{ draft.category ? draft.category.name : 'Uncategorized' }}
                                            </div>
                                        </td>
                                        <td class="px-6 py-4 whitespace-nowrap">
                                            <div class="text-sm text-gray-500 dark:text-gray-400">
                                                {{ formatDate(draft.created_at) }}
                                            </div>
                                        </td>
                                        <td class="px-6 py-4 whitespace-nowrap">
                                            <div class="text-sm text-gray-500 dark:text-gray-400">
                                                {{ formatDate(draft.updated_at) }}
                                            </div>
                                        </td>
                                        <td class="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                                            <!-- Always visible actions -->
                                            <div class="flex justify-end gap-2">
                                                <!-- Action buttons dropdown -->
                                                <Dropdown width="48">
                                                    <template #trigger>
                                                        <button class="inline-flex items-center px-3 py-1.5 bg-white dark:bg-gray-700 border border-gray-300 dark:border-gray-600 rounded-md font-semibold text-xs text-gray-700 dark:text-gray-300 uppercase tracking-widest shadow-sm hover:bg-gray-50 dark:hover:bg-gray-600 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2">
                                                            Actions
                                                            <svg class="ml-2 -mr-0.5 h-4 w-4" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
                                                                <path fill-rule="evenodd" d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z" clip-rule="evenodd" />
                                                            </svg>
                                                        </button>
                                                    </template>

                                                    <template #content>
                                                        <div class="py-1">
                                                            <!-- Edit action -->
                                                            <DropdownLink :href="route('editor.posts.edit', { post: draft.slug })" method="get" as="button">
                                                                Edit
                                                            </DropdownLink>
                                                            
                                                            <!-- Submit for review action -->
                                                            <button 
                                                                @click.prevent="submitForReview(draft.slug)"
                                                                class="w-full text-left block px-4 py-2 text-sm leading-5 text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-800 focus:outline-none focus:bg-gray-100 dark:focus:bg-gray-800 transition duration-150 ease-in-out"
                                                            >
                                                                Submit for Review
                                                            </button>
                                                            
                                                            <!-- Delete action -->
                                                            <button 
                                                                @click.prevent="confirmDelete(draft)"
                                                                class="w-full text-left block px-4 py-2 text-sm leading-5 text-red-600 dark:text-red-400 hover:bg-gray-100 dark:hover:bg-gray-800 focus:outline-none focus:bg-gray-100 dark:focus:bg-gray-800 transition duration-150 ease-in-out"
                                                            >
                                                                Delete
                                                            </button>
                                                        </div>
                                                    </template>
                                                </Dropdown>
                                            </div>
                                            
                                            <!-- Floating action buttons (visible on hover) -->
                                            <div v-if="hoveredDraftId === draft.id" class="absolute top-1/2 right-20 transform -translate-y-1/2 flex gap-2 bg-white dark:bg-gray-800 py-1 px-2 rounded-md shadow-lg z-10 transition-opacity duration-150 ease-in-out">
                                                <!-- Edit button -->
                                                <Link
                                                    :href="route('editor.posts.edit', { post: draft.slug })"
                                                    class="text-blue-600 hover:text-blue-800 dark:text-blue-400 dark:hover:text-blue-300"
                                                    title="Edit"
                                                >
                                                    <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                                                    </svg>
                                                </Link>
                                                
                                                <!-- Submit button -->
                                                <button 
                                                    @click.prevent="submitForReview(draft.slug)"
                                                    class="text-green-600 hover:text-green-800 dark:text-green-400 dark:hover:text-green-300"
                                                    title="Submit for Review"
                                                >
                                                    <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                                                    </svg>
                                                </button>
                                                
                                                <!-- Delete button -->
                                                <button 
                                                    @click.prevent="confirmDelete(draft)"
                                                    class="text-red-600 hover:text-red-800 dark:text-red-400 dark:hover:text-red-300"
                                                    title="Delete"
                                                >
                                                    <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                                                    </svg>
                                                </button>
                                            </div>
                                        </td>
                                    </tr>
                                </tbody>
                            </table>
                        </div>

                        <!-- Pagination -->
                        <div class="mt-6">
                            <Pagination :links="drafts.links" />
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <!-- Delete Confirmation Modal -->
        <Modal :show="showDeleteModal" @close="cancelDelete">
            <div class="p-6">
                <h2 class="text-lg font-medium text-gray-900 dark:text-gray-100 mb-4">
                    Delete Draft
                </h2>

                <p class="text-gray-600 dark:text-gray-400 mb-6">
                    Are you sure you want to delete this draft? This action cannot be undone.
                </p>

                <div class="flex justify-end">
                    <SecondaryButton class="mr-2" @click.prevent="cancelDelete">
                        Cancel
                    </SecondaryButton>
                    <DangerButton @click.prevent="deletePost">
                        Delete
                    </DangerButton>
                </div>
            </div>
        </Modal>
    </AuthenticatedLayout>
</template> 