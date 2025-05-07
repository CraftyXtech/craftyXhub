<script setup>
import AuthenticatedLayout from '@/Layouts/AuthenticatedLayout.vue';
import { Head, Link, router } from '@inertiajs/vue3';
import { ref, computed } from 'vue';
import PrimaryButton from '@/Components/PrimaryButton.vue';
import SecondaryButton from '@/Components/SecondaryButton.vue';
import DangerButton from '@/Components/DangerButton.vue';
import TextInput from '@/Components/TextInput.vue';
import InputLabel from '@/Components/InputLabel.vue';
import TextareaInput from '@/Components/TextareaInput.vue';
import Pagination from '@/Components/Pagination.vue';
import Modal from '@/Components/Modal.vue';

const props = defineProps({
    pendingPosts: Object,
});

// Modal states
const showReviewModal = ref(false);
const showApproveModal = ref(false);
const showRejectModal = ref(false);
const selectedPost = ref(null);
const feedback = ref('');
const feedbackError = ref('');

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

// Get direct URL that works across namespaces
const getDirectUrl = (path) => {
    return window.location.origin + path;
};

// Open review modal
const openReviewModal = (post) => {
    selectedPost.value = post;
    showReviewModal.value = true;
    feedback.value = '';
    feedbackError.value = '';
};

// Open approve modal
const openApproveModal = (post) => {
    selectedPost.value = post;
    showApproveModal.value = true;
    feedback.value = '';
    feedbackError.value = '';
};

// Open reject modal
const openRejectModal = (post) => {
    selectedPost.value = post;
    showRejectModal.value = true;
    feedback.value = '';
    feedbackError.value = '';
};

// Close modals
const closeModals = () => {
    showReviewModal.value = false;
    showApproveModal.value = false;
    showRejectModal.value = false;
    selectedPost.value = null;
    feedback.value = '';
    feedbackError.value = '';
};

// Approve post
const approvePost = () => {
    if (!selectedPost.value) return;
    
    console.log('Approving post with ID:', selectedPost.value.id);
    
    // Changed to use route() instead of direct URL
    const approveUrl = route('admin.posts.approve', { post: selectedPost.value.slug });
    console.log('Route URL used:', approveUrl);
    
    router.patch(approveUrl, { 
        feedback: feedback.value 
    }, {
        onSuccess: () => {
            closeModals();
        },
        onError: (errors) => {
            console.error('Approve failed:', errors);
            if (errors.feedback) {
                feedbackError.value = errors.feedback;
            }
        }
    });
};

// Reject post
const rejectPost = () => {
    if (!selectedPost.value) return;
    
    console.log('Rejecting post with ID:', selectedPost.value.id);
    
    // Changed to use route() instead of direct URL
    const rejectUrl = route('admin.posts.reject', { post: selectedPost.value.slug });
    console.log('Route URL used:', rejectUrl);
    
    if (!feedback.value.trim()) {
        feedbackError.value = 'Feedback is required when rejecting a post.';
        return;
    }
    
    router.patch(rejectUrl, { 
        feedback: feedback.value 
    }, {
        onSuccess: () => {
            closeModals();
        },
        onError: (errors) => {
            console.error('Reject failed:', errors);
            if (errors.feedback) {
                feedbackError.value = errors.feedback;
            }
        }
    });
};
</script>

<template>
    <Head title="Posts Pending Approval" />

    <AuthenticatedLayout>
        <template #header>
            <div class="flex justify-between items-center">
                <h2 class="font-semibold text-xl text-gray-800 dark:text-gray-200 leading-tight">
                    Posts Pending Approval
                </h2>
                <div class="flex space-x-2">
                    <Link 
                        :href="route('admin.posts.rejected')" 
                        class="inline-flex items-center px-4 py-2 bg-red-600 border border-transparent rounded-md font-semibold text-xs text-white uppercase tracking-widest hover:bg-red-700 focus:bg-red-700 active:bg-red-900 focus:outline-none focus:ring-2 focus:ring-red-500 focus:ring-offset-2 dark:focus:ring-offset-gray-800 transition ease-in-out duration-150 mr-2"
                    >
                        Rejected Posts
                    </Link>
                    <Link 
                        :href="route('admin.posts.index')" 
                        class="inline-flex items-center px-4 py-2 bg-gray-600 border border-transparent rounded-md font-semibold text-xs text-white uppercase tracking-widest hover:bg-gray-700 focus:bg-gray-700 active:bg-gray-900 focus:outline-none focus:ring-2 focus:ring-gray-500 focus:ring-offset-2 dark:focus:ring-offset-gray-800 transition ease-in-out duration-150"
                    >
                        All Posts
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
                        <div v-if="!pendingPosts.data || pendingPosts.data.length === 0" class="text-center py-10">
                            <svg xmlns="http://www.w3.org/2000/svg" class="h-12 w-12 mx-auto text-gray-400 dark:text-gray-500 mb-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                            </svg>
                            <h3 class="text-lg font-medium text-gray-700 dark:text-gray-300 mb-1">No posts pending approval</h3>
                            <p class="text-gray-500 dark:text-gray-400">
                                All submitted posts have been reviewed!
                            </p>
                        </div>

                        <!-- Pending Posts Table -->
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
                                            Submitted
                                        </th>
                                        <th scope="col" class="px-6 py-3 text-right text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                                            Actions
                                        </th>
                                    </tr>
                                </thead>
                                <tbody class="bg-white dark:bg-gray-800 divide-y divide-gray-200 dark:divide-gray-700">
                                    <tr v-for="post in pendingPosts.data" :key="post.id" class="hover:bg-gray-50 dark:hover:bg-gray-700">
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
                                                <!-- Review button -->
                                                <Link 
                                                    :href="route('admin.posts.review', { post: post.slug })"
                                                    class="font-medium text-blue-600 dark:text-blue-400 hover:underline"
                                                >
                                                    Review
                                                </Link>
                                                
                                                <!-- Quick Approve button -->
                                                <button 
                                                    @click="openApproveModal(post)" 
                                                    class="inline-flex items-center px-3 py-1.5 bg-green-600 border border-transparent rounded-md text-xs text-white uppercase tracking-widest hover:bg-green-700 active:bg-green-900 focus:outline-none focus:ring-2 focus:ring-green-500 focus:ring-offset-2 dark:focus:ring-offset-gray-800 transition ease-in-out duration-150"
                                                >
                                                    Approve
                                                </button>
                                                
                                                <!-- Quick Reject button -->
                                                <button 
                                                    @click="openRejectModal(post)" 
                                                    class="inline-flex items-center px-3 py-1.5 bg-red-600 border border-transparent rounded-md text-xs text-white uppercase tracking-widest hover:bg-red-700 active:bg-red-900 focus:outline-none focus:ring-2 focus:ring-red-500 focus:ring-offset-2 dark:focus:ring-offset-gray-800 transition ease-in-out duration-150"
                                                >
                                                    Reject
                                                </button>
                                            </div>
                                        </td>
                                    </tr>
                                </tbody>
                            </table>
                        </div>

                        <!-- Pagination -->
                        <div v-if="pendingPosts.data && pendingPosts.data.length > 0" class="mt-6">
                            <Pagination :links="pendingPosts.links" />
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <!-- Review Modal -->
        <Modal :show="showReviewModal" @close="closeModals">
            <div class="p-6">
                <h2 class="text-lg font-medium text-gray-900 dark:text-gray-100 mb-4">
                    Post Preview
                </h2>

                <div v-if="selectedPost" class="mb-6">
                    <h3 class="text-xl font-semibold mb-2">{{ selectedPost.title }}</h3>
                    <div class="text-sm text-gray-500 dark:text-gray-400 mb-4">
                        By {{ selectedPost.author ? selectedPost.author.name : 'Unknown' }} | 
                        {{ selectedPost.category ? selectedPost.category.name : 'Uncategorized' }} |
                        Submitted on {{ formatDate(selectedPost.updated_at) }}
                    </div>
                    <div class="text-gray-700 dark:text-gray-300 mt-4 max-h-60 overflow-y-auto">
                        <div v-html="selectedPost.excerpt || selectedPost.body.substring(0, 200) + '...'"></div>
                    </div>

                    <div class="mt-6 text-center">
                        <Link 
                            :href="route('admin.posts.review', { post: selectedPost.slug })" 
                            class="inline-flex items-center px-4 py-2 bg-blue-600 border border-transparent rounded-md font-semibold text-xs text-white uppercase tracking-widest hover:bg-blue-700 focus:bg-blue-700 active:bg-blue-900 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 dark:focus:ring-offset-gray-800 transition ease-in-out duration-150"
                        >
                            Full Review
                        </Link>
                    </div>
                </div>

                <div class="flex justify-end mt-6">
                    <SecondaryButton class="mr-2" @click.prevent="closeModals">
                        Cancel
                    </SecondaryButton>
                </div>
            </div>
        </Modal>

        <!-- Approve Modal -->
        <Modal :show="showApproveModal" @close="closeModals">
            <div class="p-6">
                <h2 class="text-lg font-medium text-gray-900 dark:text-gray-100 mb-4">
                    Approve Post
                </h2>

                <p class="text-gray-600 dark:text-gray-400 mb-6">
                    Are you sure you want to approve "<span class="font-semibold">{{ selectedPost?.title }}</span>"? 
                    This will publish the post immediately.
                </p>

                <div class="mb-6">
                    <InputLabel for="feedback" value="Feedback (Optional)" class="mb-1" />
                    <TextareaInput
                        id="feedback"
                        v-model="feedback"
                        class="w-full"
                        placeholder="Provide any feedback for the author..."
                        rows="4"
                    />
                </div>

                <div class="flex justify-end">
                    <SecondaryButton class="mr-2" @click.prevent="closeModals">
                        Cancel
                    </SecondaryButton>
                    <PrimaryButton @click.prevent="approvePost">
                        Approve & Publish
                    </PrimaryButton>
                </div>
            </div>
        </Modal>

        <!-- Reject Modal -->
        <Modal :show="showRejectModal" @close="closeModals">
            <div class="p-6">
                <h2 class="text-lg font-medium text-gray-900 dark:text-gray-100 mb-4">
                    Reject Post
                </h2>

                <p class="text-gray-600 dark:text-gray-400 mb-6">
                    Are you sure you want to reject "<span class="font-semibold">{{ selectedPost?.title }}</span>"? 
                    The author will need to address your feedback before resubmitting.
                </p>

                <div class="mb-6">
                    <InputLabel for="reject-feedback" value="Feedback" class="mb-1" />
                    <TextareaInput
                        id="reject-feedback"
                        v-model="feedback"
                        class="w-full"
                        placeholder="Provide feedback explaining why the post is being rejected..."
                        rows="4"
                    />
                    <p v-if="feedbackError" class="mt-1 text-red-600 dark:text-red-400 text-sm">
                        {{ feedbackError }}
                    </p>
                </div>

                <div class="flex justify-end">
                    <SecondaryButton class="mr-2" @click.prevent="closeModals">
                        Cancel
                    </SecondaryButton>
                    <DangerButton @click.prevent="rejectPost">
                        Reject
                    </DangerButton>
                </div>
            </div>
        </Modal>
    </AuthenticatedLayout>
</template> 