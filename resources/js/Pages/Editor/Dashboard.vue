<template>
    <Head title="Editor Dashboard" />

    <AuthenticatedLayout>
        <template #header>
            <h2 class="font-semibold text-xl text-gray-800 dark:text-gray-200 leading-tight">
                Editor Dashboard
            </h2>
        </template>

        <div class="py-12">
            <div class="max-w-7xl mx-auto sm:px-6 lg:px-8">
                <!-- Welcome Banner -->
                <div class="bg-indigo-600 dark:bg-indigo-800 shadow-sm sm:rounded-lg mb-6">
                    <div class="px-4 py-6 sm:px-6">
                        <h2 class="text-2xl font-bold text-white">Welcome to your Editor Dashboard</h2>
                        <p class="mt-1 text-indigo-100">Create, manage, and track your content from here.</p>
                        
                        <div class="mt-4 flex flex-wrap gap-3">
                            <Link :href="route('editor.posts.create')" class="inline-flex items-center px-4 py-2 bg-white dark:bg-gray-800 border border-transparent rounded-md font-semibold text-xs text-indigo-700 dark:text-indigo-300 uppercase tracking-widest hover:bg-indigo-50 dark:hover:bg-gray-700 focus:outline-none focus:ring-2 focus:ring-white focus:ring-offset-2 focus:ring-offset-indigo-600 dark:focus:ring-offset-indigo-800 transition ease-in-out duration-150">
                                Create New Post
                            </Link>
                            <Link :href="route('editor.posts.index')" class="inline-flex items-center px-4 py-2 bg-indigo-700 dark:bg-indigo-900 border border-transparent rounded-md font-semibold text-xs text-white uppercase tracking-widest hover:bg-indigo-800 dark:hover:bg-indigo-950 focus:outline-none focus:ring-2 focus:ring-white focus:ring-offset-2 focus:ring-offset-indigo-600 dark:focus:ring-offset-indigo-800 transition ease-in-out duration-150">
                                Manage Posts
                            </Link>
                        </div>
                    </div>
                </div>

                <!-- Error Message (Global) -->
                <ErrorMessage 
                    v-if="errors.analytics" 
                    :message="errors.analytics"
                    :retry="retryLoadData"
                />

                <!-- Analytics Overview -->
                <div v-if="loading.analytics && !analytics">
                    <LoadingIndicator />
                </div>

                <div v-else class="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
                    <div class="bg-white dark:bg-gray-800 overflow-hidden shadow-sm sm:rounded-lg">
                        <div class="p-6">
                            <h3 class="text-lg font-medium text-gray-900 dark:text-gray-100 mb-2">
                                Published Posts
                            </h3>
                            <p class="text-3xl font-semibold text-gray-900 dark:text-gray-100">
                                {{ formatNumber(analytics?.publishedCount) }}
                            </p>
                        </div>
                    </div>

                    <div class="bg-white dark:bg-gray-800 overflow-hidden shadow-sm sm:rounded-lg">
                        <div class="p-6">
                            <h3 class="text-lg font-medium text-gray-900 dark:text-gray-100 mb-2">
                                Total Views
                            </h3>
                            <p class="text-3xl font-semibold text-gray-900 dark:text-gray-100">
                                {{ formatNumber(analytics?.totalViews) }}
                            </p>
                        </div>
                    </div>

                    <div class="bg-white dark:bg-gray-800 overflow-hidden shadow-sm sm:rounded-lg">
                        <div class="p-6">
                            <h3 class="text-lg font-medium text-gray-900 dark:text-gray-100 mb-2">
                                Pending Reviews
                            </h3>
                            <p class="text-3xl font-semibold text-gray-900 dark:text-gray-100">
                                {{ formatNumber(analytics?.pendingReviewCount) }}
                            </p>
                        </div>
                    </div>
                </div>

                <!-- View Trends Chart (if provided) -->
                <div v-if="viewTrends && viewTrends.labels && viewTrends.labels.length > 0" class="mb-6 bg-white dark:bg-gray-800 overflow-hidden shadow-sm sm:rounded-lg">
                    <div class="p-6">
                        <h3 class="text-lg font-medium text-gray-900 dark:text-gray-100 mb-4">
                            View Trends
                        </h3>
                        <!-- Simplified chart visualization (can be replaced with a proper chart component) -->
                        <div class="h-40 flex items-end space-x-1">
                            <div 
                                v-for="(count, index) in viewTrends.data" 
                                :key="index" 
                                :style="`height: ${Math.max(10, (count / Math.max(...viewTrends.data)) * 100)}%`"
                                class="bg-indigo-500 dark:bg-indigo-600 w-full rounded-t"
                            ></div>
                        </div>
                        <div class="mt-2 flex justify-between text-xs text-gray-500 dark:text-gray-400">
                            <span>{{ viewTrends.labels[0] }}</span>
                            <span>{{ viewTrends.labels[Math.floor(viewTrends.labels.length / 2)] }}</span>
                            <span>{{ viewTrends.labels[viewTrends.labels.length - 1] }}</span>
                        </div>
                        
                        <div class="mt-4">
                            <Link 
                                :href="route('editor.stats')" 
                                class="text-sm text-indigo-600 dark:text-indigo-400 hover:underline"
                            >
                                View detailed statistics →
                            </Link>
                        </div>
                    </div>
                </div>

                <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
                    <!-- Recent Posts -->
                    <div class="bg-white dark:bg-gray-800 overflow-hidden shadow-sm sm:rounded-lg">
                        <div class="p-6">
                            <div class="flex justify-between items-center mb-4">
                                <h3 class="text-lg font-medium text-gray-900 dark:text-gray-100">
                                    Recent Posts
                                </h3>
                                <Link 
                                    :href="route('editor.posts.index')" 
                                    class="text-sm text-indigo-600 dark:text-indigo-400 hover:underline"
                                >
                                    View All
                                </Link>
                            </div>
                            
                            <div v-if="loading.posts && !recentPosts">
                                <LoadingIndicator />
                            </div>
                            
                            <ErrorMessage 
                                v-else-if="errors.posts" 
                                :message="errors.posts"
                                :retry="retryLoadData" 
                            />
                            
                            <div v-else-if="recentPosts && recentPosts.length > 0" class="space-y-4">
                                <div 
                                    v-for="post in recentPosts" 
                                    :key="post.id" 
                                    class="border-b border-gray-200 dark:border-gray-700 pb-4 last:border-b-0 last:pb-0"
                                >
                                    <div class="flex justify-between items-start">
                                        <div>
                                            <h4 class="font-medium text-gray-900 dark:text-gray-100">
                                                {{ post.title }}
                                            </h4>
                                            <div class="mt-1 flex items-center gap-2 text-sm text-gray-500 dark:text-gray-400">
                                                <span>{{ formatDate(post.updated_at) }}</span>
                                                <span>•</span>
                                                <span class="px-2 py-0.5 rounded-full text-xs" :class="getStatusClass(post.status)">
                                                    {{ formatStatus(post.status) }}
                                                </span>
                                            </div>
                                        </div>
                                        <Link 
                                            :href="route('editor.posts.edit', post.id)" 
                                            class="text-sm text-indigo-600 dark:text-indigo-400 hover:underline"
                                        >
                                            Edit
                                        </Link>
                                    </div>
                                </div>
                            </div>
                            
                            <div v-else class="text-gray-500 dark:text-gray-400 py-4 text-center">
                                No posts yet. <Link :href="route('editor.posts.create')" class="text-indigo-600 dark:text-indigo-400 hover:underline">Create your first post</Link>.
                            </div>
                        </div>
                    </div>

                    <!-- Pending Reviews -->
                    <div class="bg-white dark:bg-gray-800 overflow-hidden shadow-sm sm:rounded-lg">
                        <div class="p-6">
                            <div class="flex justify-between items-center mb-4">
                                <h3 class="text-lg font-medium text-gray-900 dark:text-gray-100">
                                    Pending Reviews
                                </h3>
                            </div>
                            
                            <div v-if="loading.posts && !pendingReviews">
                                <LoadingIndicator />
                            </div>
                            
                            <div v-else-if="pendingReviews && pendingReviews.length > 0" class="space-y-4">
                                <div 
                                    v-for="post in pendingReviews" 
                                    :key="post.id" 
                                    class="border-b border-gray-200 dark:border-gray-700 pb-4 last:border-b-0 last:pb-0"
                                >
                                    <div class="flex justify-between items-start">
                                        <div>
                                            <h4 class="font-medium text-gray-900 dark:text-gray-100">
                                                {{ post.title }}
                                            </h4>
                                            <div class="mt-1 flex items-center gap-2 text-sm text-gray-500 dark:text-gray-400">
                                                <span>Submitted: {{ formatDate(post.updated_at) }}</span>
                                                <span v-if="post.feedback" class="text-red-500 dark:text-red-400">
                                                    Has feedback
                                                </span>
                                            </div>
                                        </div>
                                        <Link 
                                            :href="route('editor.posts.edit', post.id)" 
                                            class="text-sm text-indigo-600 dark:text-indigo-400 hover:underline"
                                        >
                                            View
                                        </Link>
                                    </div>
                                    <div v-if="post.feedback" class="mt-2">
                                        <div class="text-sm bg-red-50 dark:bg-red-900/20 border border-red-100 dark:border-red-900/30 rounded-md p-3 text-red-800 dark:text-red-300">
                                            {{ post.feedback }}
                                        </div>
                                    </div>
                                </div>
                            </div>
                            
                            <div v-else class="text-gray-500 dark:text-gray-400 py-4 text-center">
                                No posts pending review.
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </AuthenticatedLayout>
</template> 


<script setup>
import AuthenticatedLayout from '@/Layouts/AuthenticatedLayout.vue';
import { Head, Link, router } from '@inertiajs/vue3';
import { ref, computed, onMounted } from 'vue';
import PrimaryButton from '@/Components/PrimaryButton.vue';
import SecondaryButton from '@/Components/SecondaryButton.vue';
import LoadingIndicator from '@/Components/LoadingIndicator.vue';
import ErrorMessage from '@/Components/ErrorMessage.vue';
import axios from 'axios';

const props = defineProps({
    analytics: Object,
    recentPosts: Array,
    pendingReviews: Array,
    viewTrends: Object,
});

// Loading and error states
const loading = ref({
    analytics: false,
    posts: false,
});
const errors = ref({
    analytics: null,
    posts: null,
});

// Format date to readable format
const formatDate = (dateString) => {
    if (!dateString) return 'N/A';
    const date = new Date(dateString);
    return new Intl.DateTimeFormat('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit',
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

// Function to retry loading data after an error
const retryLoadData = () => {
    router.visit(route('editor.dashboard'), { preserveScroll: true });
};

// Format numbers for display
const formatNumber = (num) => {
    if (num === undefined || num === null) return '0';
    return new Intl.NumberFormat().format(num);
};
</script>