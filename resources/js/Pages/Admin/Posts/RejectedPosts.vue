<script setup>
import AuthenticatedLayout from '@/Layouts/AuthenticatedLayout.vue';
import { Head, Link, router } from '@inertiajs/vue3';
import { ref } from 'vue';
import Pagination from '@/Components/Pagination.vue';
import Modal from '@/Components/Modal.vue';
import PrimaryButton from '@/Components/PrimaryButton.vue';

const props = defineProps({
    rejectedPosts: Object,
});

// Modal states
const showFeedbackModal = ref(false);
const selectedPost = ref(null);

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

// Open feedback modal
const openFeedbackModal = (post) => {
    selectedPost.value = post;
    showFeedbackModal.value = true;
};

// Close modals
const closeModals = () => {
    showFeedbackModal.value = false;
    selectedPost.value = null;
};

// Resubmit a rejected post
const resubmitPost = () => {
    if (!selectedPost.value) return;
    
    router.post(route('editor.posts.resubmit', { post: selectedPost.value.slug }), {}, {
        onSuccess: () => {
            closeModals();
        },
        onError: (errors) => {
            console.error('Resubmit failed:', errors);
        }
    });
};

// Check if current user can resubmit the post
const canResubmit = (post) => {
    const user = window?.$page?.props?.auth?.user;
    if (!user) return false;
    
    // User can resubmit if they are the author or an editor/admin
    return post.user_id === user.id || ['editor', 'admin'].includes(user.role);
};
</script>

<template>
    <Head title="Rejected Posts" />

    <AuthenticatedLayout>
        <template #header>
            <div class="flex justify-between items-center">
                <h2 class="font-semibold text-xl text-gray-800 dark:text-gray-200 leading-tight">
                    Rejected Posts
                </h2>
                <div class="flex space-x-2">
                    <Link 
                        :href="route('admin.posts.index')" 
                        class="inline-flex items-center px-4 py-2 bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-600 rounded-md font-semibold text-xs text-gray-700 dark:text-gray-300 uppercase tracking-widest shadow-sm hover:bg-gray-50 dark:hover:bg-gray-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 dark:focus:ring-offset-gray-800 disabled:opacity-25 transition ease-in-out duration-150"
                    >
                        All Posts
                    </Link>
                    <Link 
                        :href="route('admin.posts.pending')" 
                        class="inline-flex items-center px-4 py-2 bg-indigo-600 border border-transparent rounded-md font-semibold text-xs text-white uppercase tracking-widest hover:bg-indigo-700 focus:bg-indigo-700 active:bg-indigo-900 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 dark:focus:ring-offset-gray-800 transition ease-in-out duration-150"
                    >
                        Pending Approval
                    </Link>
                </div>
            </div>
        </template>

        <div class="py-12">
            <div class="max-w-7xl mx-auto sm:px-6 lg:px-8">
                <!-- Flash Messages -->
                <div v-if="$page.props.flash && $page.props.flash.success" class="mb-4 bg-green-100 border-l-4 border-green-500 text-green-700 p-4 dark:bg-green-900 dark:text-green-100" role="alert">
                    <p>{{ $page.props.flash.success }}</p>
                </div>
                <div v-if="$page.props.flash && $page.props.flash.error" class="mb-4 bg-red-100 border-l-4 border-red-500 text-red-700 p-4 dark:bg-red-900 dark:text-red-100" role="alert">
                    <p>{{ $page.props.flash.error }}</p>
                </div>
                
                <div class="bg-white dark:bg-gray-800 overflow-hidden shadow-sm sm:rounded-lg">
                    <div class="p-6">
                        <!-- No Posts Message -->
                        <div v-if="!rejectedPosts.data || rejectedPosts.data.length === 0" class="text-center py-10">
                            <svg xmlns="http://www.w3.org/2000/svg" class="h-12 w-12 mx-auto text-gray-400 dark:text-gray-500 mb-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                            </svg>
                            <h3 class="text-lg font-medium text-gray-700 dark:text-gray-300 mb-1">No rejected posts</h3>
                            <p class="text-gray-500 dark:text-gray-400">
                                There are currently no rejected posts.
                            </p>
                        </div>

                        <!-- Rejected Posts Table -->
                        <div v-else class="overflow-x-auto">
                            <table class="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
                                <thead class="bg-gray-50 dark:bg-gray-700">
                                    <tr>
                                        <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                                            Title
                                        </th>
                                        <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                                            Author
                                        </th>
                                        <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                                            Category
                                        </th>
                                        <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                                            Rejected On
                                        </th>
                                        <th scope="col" class="px-6 py-3 text-right text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                                            Actions
                                        </th>
                                    </tr>
                                </thead>
                                <tbody class="bg-white dark:bg-gray-800 divide-y divide-gray-200 dark:divide-gray-700">
                                    <tr v-for="post in rejectedPosts.data" :key="post.id" class="hover:bg-gray-50 dark:hover:bg-gray-700">
                                        <td class="px-6 py-4 whitespace-nowrap">
                                            <div class="text-sm font-medium text-gray-900 dark:text-gray-100">
                                                {{ post.title || 'Untitled Post' }}
                                            </div>
                                        </td>
                                        <td class="px-6 py-4 whitespace-nowrap">
                                            <div class="text-sm text-gray-500 dark:text-gray-400">
                                                {{ post.author ? post.author.name : 'Unknown' }}
                                            </div>
                                        </td>
                                        <td class="px-6 py-4 whitespace-nowrap">
                                            <div class="text-sm text-gray-500 dark:text-gray-400">
                                                {{ post.category ? post.category.name : 'Uncategorized' }}
                                            </div>
                                        </td>
                                        <td class="px-6 py-4 whitespace-nowrap">
                                            <div class="text-sm text-gray-500 dark:text-gray-400">
                                                {{ formatDate(post.updated_at) }}
                                            </div>
                                        </td>
                                        <td class="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                                            <div class="flex justify-end space-x-2">
                                                <!-- View Feedback button -->
                                                <button 
                                                    @click="openFeedbackModal(post)" 
                                                    class="font-medium text-blue-600 dark:text-blue-400 hover:underline"
                                                >
                                                    View Feedback
                                                </button>
                                            </div>
                                        </td>
                                    </tr>
                                </tbody>
                            </table>
                        </div>

                        <!-- Pagination -->
                        <div v-if="rejectedPosts.data && rejectedPosts.data.length > 0" class="mt-6">
                            <Pagination :links="rejectedPosts.links" />
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <!-- Feedback Modal -->
        <Modal :show="showFeedbackModal" @close="closeModals">
            <div class="p-6">
                <h2 class="text-lg font-medium text-gray-900 dark:text-gray-100 mb-4">
                    Rejection Feedback
                </h2>

                <div v-if="selectedPost" class="mb-6">
                    <h3 class="text-xl font-semibold mb-2">{{ selectedPost.title }}</h3>
                    <div class="text-sm text-gray-500 dark:text-gray-400 mb-4">
                        By {{ selectedPost.author ? selectedPost.author.name : 'Unknown' }} | 
                        {{ selectedPost.category ? selectedPost.category.name : 'Uncategorized' }} |
                        Rejected on {{ formatDate(selectedPost.updated_at) }}
                    </div>
                    
                    <div class="mt-4 p-4 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-md">
                        <h4 class="font-medium text-red-800 dark:text-red-300 mb-2">Rejection Feedback:</h4>
                        <p class="text-gray-700 dark:text-gray-300">{{ selectedPost.feedback }}</p>
                    </div>
                </div>

                <div class="flex justify-end mt-6">
                    <button 
                        @click="closeModals"
                        class="inline-flex items-center px-4 py-2 bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-600 rounded-md font-semibold text-xs text-gray-700 dark:text-gray-300 uppercase tracking-widest shadow-sm hover:bg-gray-50 dark:hover:bg-gray-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 dark:focus:ring-offset-gray-800 disabled:opacity-25 transition ease-in-out duration-150"
                    >
                        Close
                    </button>
                    <!-- Add this button if the current user is the author or an editor -->
                    <Link 
                        v-if="selectedPost && canResubmit(selectedPost)"
                        :href="route('editor.posts.edit', { post: selectedPost.id })"
                        class="ml-2 inline-flex items-center px-4 py-2 bg-indigo-600 border border-transparent rounded-md font-semibold text-xs text-white uppercase tracking-widest hover:bg-indigo-700 focus:bg-indigo-700 active:bg-indigo-900 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 dark:focus:ring-offset-gray-800 transition ease-in-out duration-150"
                    >
                        Edit & Resubmit
                    </Link>
                    <PrimaryButton 
                        v-if="selectedPost && canResubmit(selectedPost)" 
                        @click="resubmitPost"
                        class="ml-2 bg-green-600 hover:bg-green-700"
                    >
                        Resubmit As Is
                    </PrimaryButton>
                </div>
            </div>
        </Modal>
    </AuthenticatedLayout>
</template> 