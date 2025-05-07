<script setup>
import AuthenticatedLayout from '@/Layouts/AuthenticatedLayout.vue';
import { Head, router, Link } from '@inertiajs/vue3';
import { ref } from 'vue';
import PrimaryButton from '@/Components/PrimaryButton.vue';
import SecondaryButton from '@/Components/SecondaryButton.vue';
import DangerButton from '@/Components/DangerButton.vue';
import TextareaInput from '@/Components/TextareaInput.vue';
import InputLabel from '@/Components/InputLabel.vue';
import Modal from '@/Components/Modal.vue';

const props = defineProps({
    post: Object,
});

// Modal states
const showApproveModal = ref(false);
const showRejectModal = ref(false);
const feedback = ref('');
const feedbackError = ref('');

// Get direct URL that works across namespaces
const getDirectUrl = (path) => {
    return window.location.origin + path;
};

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

// Open approve modal
const openApproveModal = () => {
    showApproveModal.value = true;
    feedback.value = '';
    feedbackError.value = '';
};

// Open reject modal
const openRejectModal = () => {
    showRejectModal.value = true;
    feedback.value = '';
    feedbackError.value = '';
};

// Close modals
const closeModals = () => {
    showApproveModal.value = false;
    showRejectModal.value = false;
    feedback.value = '';
    feedbackError.value = '';
};

// Approve post
const approvePost = () => {
    // Use route() instead of getDirectUrl
    const approveUrl = route('admin.posts.approve', { post: props.post.slug });
    console.log('Route URL used for approve:', approveUrl);
    
    router.patch(approveUrl, { 
        feedback: feedback.value 
    }, {
        onSuccess: () => {
            // Redirect to the pending posts page using route()
            router.visit(route('admin.posts.pending'));
        },
        onError: (errors) => {
            if (errors.feedback) {
                feedbackError.value = errors.feedback;
            }
            console.error('Approve failed:', errors);
        }
    });
};

// Reject post
const rejectPost = () => {
    if (!feedback.value.trim()) {
        feedbackError.value = 'Feedback is required when rejecting a post.';
        return;
    }
    
    // Use route() instead of getDirectUrl
    const rejectUrl = route('admin.posts.reject', { post: props.post.slug });
    console.log('Route URL used for reject:', rejectUrl);
    
    router.patch(rejectUrl, { 
        feedback: feedback.value 
    }, {
        onSuccess: () => {
            // Redirect to the pending posts page using route()
            router.visit(route('admin.posts.pending'));
        },
        onError: (errors) => {
            if (errors.feedback) {
                feedbackError.value = errors.feedback;
            }
            console.error('Reject failed:', errors);
        }
    });
};
</script>

<template>
    <Head :title="'Review: ' + post.title" />

    <AuthenticatedLayout>
        <template #header>
            <div class="flex justify-between items-center">
                <h2 class="font-semibold text-xl text-gray-800 dark:text-gray-200 leading-tight">
                    Post Review
                </h2>
                <div class="flex space-x-2">
                    <Link 
                        :href="route('admin.posts.pending')"
                        class="inline-flex items-center px-4 py-2 bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-600 rounded-md font-semibold text-xs text-gray-700 dark:text-gray-300 uppercase tracking-widest shadow-sm hover:bg-gray-50 dark:hover:bg-gray-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 dark:focus:ring-offset-gray-800 disabled:opacity-25 transition ease-in-out duration-150"
                    >
                        Back to Pending
                    </Link>
                    <PrimaryButton 
                        @click="openApproveModal"
                        class="bg-green-600 hover:bg-green-700"
                    >
                        Approve
                    </PrimaryButton>
                    <DangerButton 
                        @click="openRejectModal"
                    >
                        Reject
                    </DangerButton>
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
                
                <div class="bg-white dark:bg-gray-800 overflow-hidden shadow-sm sm:rounded-lg mb-6">
                    <div class="p-6">
                        <!-- Post Metadata -->
                        <div class="border-b border-gray-200 dark:border-gray-700 pb-4 mb-6">
                            <h1 class="text-2xl font-bold text-gray-900 dark:text-gray-100 mb-2">
                                {{ post.title }}
                            </h1>
                            <div class="flex flex-wrap text-sm text-gray-500 dark:text-gray-400 mb-4">
                                <div class="mr-4">
                                    <span class="font-semibold">Author:</span> {{ post.author ? post.author.name : 'Unknown' }}
                                </div>
                                <div class="mr-4">
                                    <span class="font-semibold">Category:</span> {{ post.category ? post.category.name : 'Uncategorized' }}
                                </div>
                                <div class="mr-4">
                                    <span class="font-semibold">Submitted:</span> {{ formatDate(post.updated_at) }}
                                </div>
                                <div class="mr-4">
                                    <span class="font-semibold">Status:</span> 
                                    <span class="px-2 py-1 text-xs font-semibold rounded-full bg-yellow-100 text-yellow-800 dark:bg-yellow-800 dark:text-yellow-100">
                                        Under Review
                                    </span>
                                </div>
                            </div>
                            
                            <!-- Tags -->
                            <div v-if="post.tags && post.tags.length" class="flex flex-wrap gap-2 mb-4">
                                <span 
                                    v-for="tag in post.tags" 
                                    :key="tag.id" 
                                    class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800 dark:bg-blue-800 dark:text-blue-100"
                                >
                                    {{ tag.name }}
                                </span>
                            </div>
                        </div>
                        
                        <!-- Post Content -->
                        <div class="prose prose-slate dark:prose-invert max-w-none">
                            <div v-if="post.excerpt" class="italic border-l-4 border-gray-300 dark:border-gray-600 pl-4 mb-6">
                                {{ post.excerpt }}
                            </div>
                            
                            <div v-html="post.body" class="leading-relaxed"></div>
                        </div>
                    </div>
                </div>
                
                <!-- Decision Buttons -->
                <div class="bg-white dark:bg-gray-800 overflow-hidden shadow-sm sm:rounded-lg">
                    <div class="p-6">
                        <h3 class="text-lg font-medium text-gray-900 dark:text-gray-100 mb-4">
                            Review Decision
                        </h3>
                        
                        <div class="flex justify-center space-x-4">
                            <button 
                                @click="openApproveModal" 
                                class="inline-flex items-center px-5 py-2.5 bg-green-600 border border-transparent rounded-md font-semibold text-sm text-white uppercase tracking-widest hover:bg-green-700 focus:bg-green-700 active:bg-green-900 focus:outline-none focus:ring-2 focus:ring-green-500 focus:ring-offset-2 dark:focus:ring-offset-gray-800 transition ease-in-out duration-150"
                            >
                                <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                                    <path stroke-linecap="round" stroke-linejoin="round" d="M5 13l4 4L19 7" />
                                </svg>
                                Approve & Publish
                            </button>
                            
                            <button 
                                @click="openRejectModal" 
                                class="inline-flex items-center px-5 py-2.5 bg-red-600 border border-transparent rounded-md font-semibold text-sm text-white uppercase tracking-widest hover:bg-red-700 focus:bg-red-700 active:bg-red-900 focus:outline-none focus:ring-2 focus:ring-red-500 focus:ring-offset-2 dark:focus:ring-offset-gray-800 transition ease-in-out duration-150"
                            >
                                <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                                    <path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12" />
                                </svg>
                                Reject
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <!-- Approve Modal -->
        <Modal :show="showApproveModal" @close="closeModals">
            <div class="p-6">
                <h2 class="text-lg font-medium text-gray-900 dark:text-gray-100 mb-4">
                    Approve Post
                </h2>

                <p class="text-gray-600 dark:text-gray-400 mb-6">
                    Are you sure you want to approve this post? This will publish it immediately.
                </p>

                <div class="mb-6">
                    <InputLabel for="approve-feedback" value="Feedback (Optional)" class="mb-1" />
                    <TextareaInput
                        id="approve-feedback"
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
                    <PrimaryButton 
                        @click.prevent="approvePost"
                        class="bg-green-600 hover:bg-green-700"
                    >
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
                    Are you sure you want to reject this post? The author will need to address your feedback before resubmitting.
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