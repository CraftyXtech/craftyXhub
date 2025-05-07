<script setup>
import { Head, Link } from '@inertiajs/vue3';
import AuthenticatedLayout from '@/Layouts/AuthenticatedLayout.vue';
import PrimaryButton from '@/Components/PrimaryButton.vue';
import SecondaryButton from '@/Components/SecondaryButton.vue';

const props = defineProps({
    post: Object,
    canEdit: Boolean,
    canPublish: Boolean
});

// Format date to readable format
const formatDate = (dateString) => {
    if (!dateString) return 'Not published';
    
    const date = new Date(dateString);
    return new Intl.DateTimeFormat('en-US', {
        year: 'numeric',
        month: 'long',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    }).format(date);
};

// Get status badge
const getStatusBadge = (status) => {
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
</script>

<template>
    <Head :title="post.title" />

    <AuthenticatedLayout>
        <template #header>
            <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between space-y-2 sm:space-y-0">
                <div>
                    <h2 class="font-semibold text-xl text-gray-800 dark:text-gray-200 leading-tight">
                        {{ post.title }}
                    </h2>
                    <div class="flex items-center mt-1 space-x-2">
                        <span 
                            class="px-2.5 py-0.5 rounded-full text-xs font-medium"
                            :class="getStatusBadge(post.status)"
                        >
                            {{ formatStatus(post.status) }}
                        </span>
                        <span class="text-sm text-gray-500 dark:text-gray-400">
                            {{ post.category ? post.category.name : 'Uncategorized' }}
                        </span>
                    </div>
                </div>
                <div class="flex space-x-2">
                    <SecondaryButton 
                        as="a" 
                        :href="route('editor.posts.index')"
                    >
                        Back to Posts
                    </SecondaryButton>
                    <PrimaryButton 
                        v-if="canEdit"
                        as="a" 
                        :href="route('editor.posts.edit', { post: post.slug })"
                    >
                        Edit Post
                    </PrimaryButton>
                    <PrimaryButton 
                        v-if="post.status === 'published'"
                        as="a" 
                        :href="`/posts/${post.slug}`"
                        target="_blank"
                        class="bg-green-600 hover:bg-green-700"
                    >
                        View Live
                    </PrimaryButton>
                </div>
            </div>
        </template>

        <div class="py-12">
            <div class="max-w-7xl mx-auto sm:px-6 lg:px-8 space-y-6">
                <!-- Post Meta -->
                <div class="bg-white dark:bg-gray-800 overflow-hidden shadow-sm sm:rounded-lg">
                    <div class="p-6 text-gray-900 dark:text-gray-100">
                        <div class="flex flex-wrap gap-y-4">
                            <div class="w-full md:w-1/3 space-y-1">
                                <h3 class="text-sm font-semibold text-gray-500 dark:text-gray-400">Publication Info</h3>
                                <div class="grid grid-cols-2">
                                    <div class="text-sm font-medium">Status:</div>
                                    <div>
                                        <span 
                                            class="px-2 py-0.5 rounded-full text-xs font-medium"
                                            :class="getStatusBadge(post.status)"
                                        >
                                            {{ formatStatus(post.status) }}
                                        </span>
                                    </div>
                                    
                                    <div class="text-sm font-medium">Created:</div>
                                    <div class="text-sm">{{ formatDate(post.created_at) }}</div>
                                    
                                    <div class="text-sm font-medium">Updated:</div>
                                    <div class="text-sm">{{ formatDate(post.updated_at) }}</div>
                                    
                                    <div class="text-sm font-medium">Published:</div>
                                    <div class="text-sm">{{ formatDate(post.published_at) }}</div>
                                </div>
                            </div>
                            
                            <div class="w-full md:w-1/3 space-y-1">
                                <h3 class="text-sm font-semibold text-gray-500 dark:text-gray-400">Categorization</h3>
                                <div class="grid grid-cols-2">
                                    <div class="text-sm font-medium">Category:</div>
                                    <div class="text-sm">{{ post.category ? post.category.name : 'Uncategorized' }}</div>
                                    
                                    <div class="text-sm font-medium">Tags:</div>
                                    <div class="text-sm">
                                        <span v-if="post.tags && post.tags.length > 0">
                                            <span 
                                                v-for="(tag, index) in post.tags" 
                                                :key="tag.id"
                                                class="inline-block bg-gray-100 dark:bg-gray-700 rounded-full px-2.5 py-0.5 text-xs font-medium text-gray-800 dark:text-gray-200 mr-1"
                                            >
                                                {{ tag.name }}{{ index < post.tags.length - 1 ? '' : '' }}
                                            </span>
                                        </span>
                                        <span v-else>No tags</span>
                                    </div>
                                </div>
                            </div>
                            
                            <div class="w-full md:w-1/3 space-y-1">
                                <h3 class="text-sm font-semibold text-gray-500 dark:text-gray-400">SEO Information</h3>
                                <div class="grid grid-cols-2">
                                    <div class="text-sm font-medium">Slug:</div>
                                    <div class="text-sm">{{ post.slug }}</div>
                                    
                                    <div class="text-sm font-medium">Meta Title:</div>
                                    <div class="text-sm">{{ post.meta_title || post.title }}</div>
                                    
                                    <div class="text-sm font-medium">Meta Description:</div>
                                    <div class="text-sm">{{ post.meta_description || post.excerpt || 'Not set' }}</div>
                                </div>
                            </div>
                        </div>
                        
                        <!-- Feedback (if rejected) -->
                        <div v-if="post.feedback && post.status === 'rejected'" class="mt-6 p-4 border border-red-300 rounded-md bg-red-50 dark:bg-red-900/20 dark:border-red-800">
                            <h3 class="text-sm font-medium text-red-800 dark:text-red-300">Feedback from Reviewer</h3>
                            <div class="mt-2 text-sm text-red-700 dark:text-red-400">
                                {{ post.feedback }}
                            </div>
                        </div>
                    </div>
                </div>
                
                <!-- Featured Image -->
                <div v-if="post.featured_image_url" class="bg-white dark:bg-gray-800 overflow-hidden shadow-sm sm:rounded-lg">
                    <div class="p-6">
                        <h3 class="text-lg font-medium text-gray-900 dark:text-gray-100 mb-4">Featured Image</h3>
                        <img 
                            :src="post.featured_image_url" 
                            :alt="post.title" 
                            class="max-w-full h-auto rounded-lg shadow-lg max-h-[400px] object-contain mx-auto"
                        />
                    </div>
                </div>
                
                <!-- Content -->
                <div class="bg-white dark:bg-gray-800 overflow-hidden shadow-sm sm:rounded-lg">
                    <div class="p-6">
                        <h3 class="text-lg font-medium text-gray-900 dark:text-gray-100 mb-4">Content</h3>
                        
                        <!-- Excerpt -->
                        <div class="mb-6 p-4 border-l-4 border-gray-300 dark:border-gray-600 bg-gray-50 dark:bg-gray-700">
                            <h4 class="text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Excerpt</h4>
                            <p class="text-gray-600 dark:text-gray-400 italic">{{ post.excerpt || 'No excerpt provided' }}</p>
                        </div>
                        
                        <!-- Main Content -->
                        <div class="prose dark:prose-invert max-w-none" v-html="post"></div>
                    </div>
                </div>
                
                <!-- Action Buttons -->
                <div class="flex justify-between items-center">
                    <div>
                        <Link 
                            :href="route('editor.posts.index')" 
                            class="inline-flex items-center px-4 py-2 bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-600 rounded-md font-semibold text-xs text-gray-700 dark:text-gray-300 uppercase tracking-widest shadow-sm hover:bg-gray-50 dark:hover:bg-gray-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 dark:focus:ring-offset-gray-800 disabled:opacity-25 transition ease-in-out duration-150"
                        >
                            Back to Posts
                        </Link>
                    </div>
                    <div class="flex space-x-2">
                        <Link 
                            v-if="canEdit"
                            :href="route('editor.posts.edit', { post: post.slug })" 
                            class="inline-flex items-center px-4 py-2 bg-indigo-600 border border-transparent rounded-md font-semibold text-xs text-white uppercase tracking-widest hover:bg-indigo-700 focus:bg-indigo-700 active:bg-indigo-900 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 dark:focus:ring-offset-gray-800 transition ease-in-out duration-150"
                        >
                            Edit Post
                        </Link>
                        <Link 
                            v-if="post.status === 'published'"
                            :href="`/posts/${post.slug}`"
                            target="_blank"
                            class="inline-flex items-center px-4 py-2 bg-green-600 border border-transparent rounded-md font-semibold text-xs text-white uppercase tracking-widest hover:bg-green-700 focus:bg-green-700 active:bg-green-900 focus:outline-none focus:ring-2 focus:ring-green-500 focus:ring-offset-2 dark:focus:ring-offset-gray-800 transition ease-in-out duration-150"
                        >
                            View Live
                        </Link>
                    </div>
                </div>
            </div>
        </div>
    </AuthenticatedLayout>
</template> 