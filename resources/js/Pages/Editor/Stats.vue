<script setup>
import AuthenticatedLayout from '@/Layouts/AuthenticatedLayout.vue';
import { Head, Link } from '@inertiajs/vue3';

const props = defineProps({
    stats: {
        type: Object,
        default: () => ({}),
    },
});
</script>

<template>
    <Head title="Content Statistics" />

    <AuthenticatedLayout>
        <template #header>
            <div class="flex justify-between items-center">
                <h2 class="font-semibold text-xl text-gray-800 dark:text-gray-200 leading-tight">Content Statistics</h2>
                <Link
                    :href="route('editor.dashboard')"
                    class="px-4 py-2 text-sm text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-md"
                >
                    Back to Dashboard
                </Link>
            </div>
        </template>

        <div class="py-12">
            <div class="max-w-7xl mx-auto sm:px-6 lg:px-8">
                <!-- Stats Overview -->
                <div class="bg-white dark:bg-gray-800 overflow-hidden shadow-sm sm:rounded-lg">
                    <div class="p-6">
                        <h3 class="text-lg font-medium text-gray-900 dark:text-gray-100 mb-6">Post Statistics</h3>
                        
                        <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
                            <!-- Total Posts -->
                            <div class="bg-gray-100 dark:bg-gray-700 rounded-lg p-4 text-center">
                                <div class="text-3xl font-bold text-gray-900 dark:text-gray-100">{{ stats.total_posts ?? 0 }}</div>
                                <div class="text-sm text-gray-500 dark:text-gray-400 mt-1">Total Posts</div>
                            </div>

                            <!-- Published Posts -->
                            <div class="bg-green-100 dark:bg-green-900 rounded-lg p-4 text-center">
                                <div class="text-3xl font-bold text-green-800 dark:text-green-200">{{ stats.published_posts ?? 0 }}</div>
                                <div class="text-sm text-green-600 dark:text-green-400 mt-1">Published</div>
                            </div>

                            <!-- Draft Posts -->
                            <div class="bg-yellow-100 dark:bg-yellow-900 rounded-lg p-4 text-center">
                                <div class="text-3xl font-bold text-yellow-800 dark:text-yellow-200">{{ stats.draft_posts ?? 0 }}</div>
                                <div class="text-sm text-yellow-600 dark:text-yellow-400 mt-1">Drafts</div>
                            </div>

                            <!-- Views (Placeholder) -->
                            <div class="bg-indigo-100 dark:bg-indigo-900 rounded-lg p-4 text-center">
                                <div class="text-3xl font-bold text-indigo-800 dark:text-indigo-200">[TBD]</div>
                                <div class="text-sm text-indigo-600 dark:text-indigo-400 mt-1">Total Views</div>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Charts Placeholder -->
                <div class="mt-6 bg-white dark:bg-gray-800 overflow-hidden shadow-sm sm:rounded-lg">
                    <div class="p-6">
                        <h3 class="text-lg font-medium text-gray-900 dark:text-gray-100 mb-4">Performance Trends</h3>
                        
                        <div class="border-2 border-dashed border-gray-300 dark:border-gray-600 rounded-lg p-8 text-center">
                            <div class="text-gray-500 dark:text-gray-400">
                                <svg xmlns="http://www.w3.org/2000/svg" class="h-12 w-12 mx-auto mb-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                                </svg>
                                <p class="text-lg">Charts coming soon</p>
                                <p class="mt-2 text-sm">View performance trends of your content over time</p>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Top Posts Placeholder -->
                <div class="mt-6 bg-white dark:bg-gray-800 overflow-hidden shadow-sm sm:rounded-lg">
                    <div class="p-6">
                        <h3 class="text-lg font-medium text-gray-900 dark:text-gray-100 mb-4">Top Performing Posts</h3>
                        
                        <div class="border-2 border-dashed border-gray-300 dark:border-gray-600 rounded-lg p-8 text-center">
                            <div class="text-gray-500 dark:text-gray-400">
                                <svg xmlns="http://www.w3.org/2000/svg" class="h-12 w-12 mx-auto mb-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
                                </svg>
                                <p class="text-lg">Top posts data coming soon</p>
                                <p class="mt-2 text-sm">Track which of your content performs best</p>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </AuthenticatedLayout>
</template> 