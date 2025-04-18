<script setup>
import { ref, onMounted } from 'vue';
import { Head, Link } from '@inertiajs/vue3';
import AuthenticatedLayout from '@/Layouts/AuthenticatedLayout.vue';
import BlogPostCard from '@/Components/Blog/BlogPostCard.vue'; // Re-use for saved articles
import axios from 'axios'; // Import axios

// State
const user = ref(null);
const savedArticles = ref([]);
const preferences = ref(null);
const recentlyReadArticles = ref([]);
const followedTopics = ref([]);
const isLoading = ref(true);
const error = ref(null);

// Fetch Profile Data
const fetchProfileData = async () => {
    isLoading.value = true;
    error.value = null;
    try {
        // Fetch profile and preferences concurrently
        const [profileResponse, prefsResponse, readResponse, topicsResponse] = await Promise.all([
            axios.get('/api/user/profile'),
            axios.get('/api/user/preferences'),
            axios.get('/api/user/recently-read?limit=3'),
            axios.get('/api/user/followed-topics?limit=5')
        ]);

        user.value = profileResponse.data.data; // Data is nested in 'data' key from resource
        savedArticles.value = user.value?.savedArticles || []; // Extract saved articles
        preferences.value = prefsResponse.data;
        recentlyReadArticles.value = readResponse.data.data || [];
        followedTopics.value = topicsResponse.data.data || [];

    } catch (err) {
        console.error("Error fetching profile data:", err);
        error.value = "Failed to load profile data.";
    } finally {
        isLoading.value = false;
    }
};

onMounted(() => {
    fetchProfileData();
});

// Format date helper
const formatDate = (dateString) => {
    if (!dateString) return 'N/A';
    const date = new Date(dateString);
    return new Intl.DateTimeFormat('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
    }).format(date);
};
</script>

<template>
    <Head title="Your Profile" />

    <AuthenticatedLayout>
        <template #header>
            <h2 class="font-semibold text-xl text-gray-800 dark:text-gray-200 leading-tight">User Profile</h2>
        </template>

        <div class="py-12">
             <div v-if="isLoading" class="text-center py-16">
                <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-primary dark:border-primary-light mx-auto"></div>
            </div>
            <div v-else-if="error" class="text-center py-16 text-red-600 dark:text-red-400">
                <p>{{ error }}</p>
            </div>
            <div v-else-if="user" class="max-w-7xl mx-auto sm:px-6 lg:px-8 space-y-8">
                <!-- Profile Header -->
                <div class="bg-white dark:bg-gray-800 overflow-hidden shadow-sm sm:rounded-lg p-6 flex flex-col sm:flex-row items-center gap-6">
                     <img :src="user.avatar || 'https://via.placeholder.com/150/cccccc/FFFFFF?text=?'" :alt="user.name" class="w-24 h-24 rounded-full border-4 border-primary dark:border-primary-light bg-gray-300">
                     <div class="text-center sm:text-left">
                        <h3 class="text-2xl font-semibold text-gray-900 dark:text-gray-100">{{ user.name }}</h3>
                        <p class="text-gray-600 dark:text-gray-400">{{ user.email }}</p>
                        <p class="text-sm text-gray-500 dark:text-gray-500 mt-1">Joined: {{ formatDate(user.joinedDate) }}</p>
                        <Link :href="route('profile.edit')" class="mt-2 inline-block text-sm text-primary hover:underline dark:text-primary-light">
                            Edit Profile & Settings
                        </Link>
                    </div>
                </div>

                <!-- Overview Section (Merged from Dashboard) -->
                <div class="bg-white dark:bg-gray-800 overflow-hidden shadow-sm sm:rounded-lg p-6">
                    <h4 class="text-lg font-semibold mb-6 text-gray-900 dark:text-gray-100">Overview</h4>
                    
                    <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
                        <!-- Activity Stats -->
                        <div class="bg-gray-50 dark:bg-gray-700 rounded-lg p-4">
                            <div class="flex items-center justify-between">
                                <h5 class="text-sm font-medium text-gray-500 dark:text-gray-400">Articles Read</h5>
                                <span class="text-2xl font-bold text-gray-900 dark:text-gray-100">
                                    {{ user.stats?.articlesRead || 0 }}
                                </span>
                            </div>
                        </div>
                        
                        <div class="bg-gray-50 dark:bg-gray-700 rounded-lg p-4">
                            <div class="flex items-center justify-between">
                                <h5 class="text-sm font-medium text-gray-500 dark:text-gray-400">Articles Saved</h5>
                                <span class="text-2xl font-bold text-gray-900 dark:text-gray-100">
                                    {{ savedArticles.length || 0 }}
                                </span>
                            </div>
                        </div>
                        
                        <div class="bg-gray-50 dark:bg-gray-700 rounded-lg p-4">
                            <div class="flex items-center justify-between">
                                <h5 class="text-sm font-medium text-gray-500 dark:text-gray-400">Topics Followed</h5>
                                <span class="text-2xl font-bold text-gray-900 dark:text-gray-100">
                                    {{ followedTopics.length || 0 }}
                                </span>
                            </div>
                        </div>
                    </div>
                    
                    <div class="mt-6 flex flex-wrap gap-3">
                        <Link :href="route('home')" class="text-indigo-600 dark:text-indigo-400 hover:underline text-sm">
                            Browse Articles
                        </Link>
                        <span class="text-gray-300 dark:text-gray-600">|</span>
                        <Link :href="route('profile.edit')" class="text-indigo-600 dark:text-indigo-400 hover:underline text-sm">
                            Update Profile
                        </Link>
                        <span class="text-gray-300 dark:text-gray-600">|</span>
                        <Link :href="route('profile.edit')" class="text-indigo-600 dark:text-indigo-400 hover:underline text-sm">
                            Account Settings
                        </Link>
                    </div>
                </div>

                <!-- Recently Read Articles -->
                <div class="bg-white dark:bg-gray-800 overflow-hidden shadow-sm sm:rounded-lg p-6">
                    <div class="flex justify-between items-center mb-4">
                        <h4 class="text-lg font-semibold text-gray-900 dark:text-gray-100">Recently Read</h4>
                        <Link :href="route('home')" class="text-sm text-indigo-600 dark:text-indigo-400 hover:underline">
                            View All
                        </Link>
                    </div>
                    
                    <div v-if="recentlyReadArticles.length > 0" class="grid grid-cols-1 md:grid-cols-3 gap-6">
                        <BlogPostCard v-for="article in recentlyReadArticles" :key="article.id" :post="article" />
                    </div>
                    <p v-else class="text-gray-500 dark:text-gray-400">You haven't read any articles yet.</p>
                </div>

                <!-- Saved Articles -->
                <div class="bg-white dark:bg-gray-800 overflow-hidden shadow-sm sm:rounded-lg p-6">
                    <div class="flex justify-between items-center mb-4">
                        <h4 class="text-lg font-semibold text-gray-900 dark:text-gray-100">Saved Articles</h4>
                        <span class="text-sm text-gray-500 dark:text-gray-400">
                            {{ savedArticles.length }} articles
                        </span>
                    </div>
                    
                    <div v-if="savedArticles.length > 0" class="grid grid-cols-1 md:grid-cols-2 gap-6">
                         <BlogPostCard v-for="article in savedArticles" :key="article.id" :post="article" />
                    </div>
                    <p v-else class="text-gray-500 dark:text-gray-400">You haven't saved any articles yet.</p>
                </div>

                <!-- Followed Topics -->
                <div class="bg-white dark:bg-gray-800 overflow-hidden shadow-sm sm:rounded-lg p-6">
                    <div class="flex justify-between items-center mb-4">
                        <h4 class="text-lg font-semibold text-gray-900 dark:text-gray-100">Topics You Follow</h4>
                        <Link :href="route('home')" class="text-sm text-indigo-600 dark:text-indigo-400 hover:underline">
                            Explore Topics
                        </Link>
                    </div>
                    
                    <div v-if="followedTopics.length > 0" class="flex flex-wrap gap-3 mb-4">
                        <div 
                            v-for="topic in followedTopics" 
                            :key="topic.id" 
                            class="px-4 py-2 bg-indigo-100 text-indigo-800 dark:bg-indigo-900 dark:text-indigo-200 rounded-full"
                        >
                            {{ topic.name }}
                        </div>
                    </div>
                    <p v-else class="text-gray-500 dark:text-gray-400">You don't follow any topics yet.</p>
                </div>

                <!-- Preferences -->
                 <div v-if="preferences" class="bg-white dark:bg-gray-800 overflow-hidden shadow-sm sm:rounded-lg p-6">
                    <div class="flex justify-between items-center mb-4">
                        <h4 class="text-lg font-semibold text-gray-900 dark:text-gray-100">Preferences</h4>
                        <Link :href="route('profile.edit')" class="text-sm text-indigo-600 dark:text-indigo-400 hover:underline">
                            Edit Preferences
                        </Link>
                    </div>
                    
                     <div class="space-y-2 text-gray-700 dark:text-gray-300">
                         <div class="flex justify-between py-2 border-b border-gray-100 dark:border-gray-700">
                             <span>Newsletter:</span>
                             <span class="font-medium">{{ preferences.newsletter_enabled ? 'Subscribed' : 'Not subscribed' }}</span>
                         </div>
                         
                         <div class="flex justify-between py-2 border-b border-gray-100 dark:border-gray-700">
                             <span>Content Personalization:</span>
                             <span class="font-medium">{{ preferences.personalization_enabled ? 'Enabled' : 'Disabled' }}</span>
                         </div>
                         
                         <div class="py-2">
                             <p class="mb-2">Preferred Categories:</p>
                             <div class="flex flex-wrap gap-2">
                                 <span 
                                     v-for="(category, index) in preferences.preferred_categories" 
                                     :key="index"
                                     class="px-2 py-1 bg-gray-100 dark:bg-gray-700 rounded text-sm"
                                 >
                                     {{ category }}
                                 </span>
                                 <span v-if="!preferences.preferred_categories?.length" class="text-gray-500 dark:text-gray-400">
                                     None selected
                                 </span>
                             </div>
                         </div>
                     </div>
                </div>
            </div>
        </div>
    </AuthenticatedLayout>
</template> 