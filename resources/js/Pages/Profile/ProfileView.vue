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
const isLoading = ref(true);
const error = ref(null);

// Fetch Profile Data
const fetchProfileData = async () => {
    isLoading.value = true;
    error.value = null;
    try {
        // Fetch profile and preferences concurrently
        const [profileResponse, prefsResponse] = await Promise.all([
            axios.get('/api/user/profile'),
            axios.get('/api/user/preferences')
        ]);

        user.value = profileResponse.data.data; // Data is nested in 'data' key from resource
        savedArticles.value = user.value?.savedArticles || []; // Extract saved articles
        preferences.value = prefsResponse.data;

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
                        <p class="text-sm text-gray-500 dark:text-gray-500 mt-1">Joined: {{ user.joinedDate }}</p>
                        <Link :href="route('profile.edit')" class="mt-2 inline-block text-sm text-primary hover:underline dark:text-primary-light">
                            Edit Profile & Settings
                        </Link>
                    </div>
                </div>

                <!-- Saved Articles -->
                <div class="bg-white dark:bg-gray-800 overflow-hidden shadow-sm sm:rounded-lg p-6">
                    <h4 class="text-lg font-semibold mb-4 text-gray-900 dark:text-gray-100">Saved Articles ({{ savedArticles.length }})</h4>
                    <div v-if="savedArticles.length > 0" class="grid grid-cols-1 md:grid-cols-2 gap-6">
                         <BlogPostCard v-for="article in savedArticles" :key="article.id" :post="article" />
                    </div>
                    <p v-else class="text-gray-500 dark:text-gray-400">You haven't saved any articles yet.</p>
                </div>

                <!-- Reading History (Placeholder) -->
                <div class="bg-white dark:bg-gray-800 overflow-hidden shadow-sm sm:rounded-lg p-6">
                    <h4 class="text-lg font-semibold mb-4 text-gray-900 dark:text-gray-100">Reading History</h4>
                     <p class="text-gray-500 dark:text-gray-400">Reading history feature coming soon.</p>
                </div>

                <!-- Preferences -->
                 <div v-if="preferences" class="bg-white dark:bg-gray-800 overflow-hidden shadow-sm sm:rounded-lg p-6">
                    <h4 class="text-lg font-semibold mb-4 text-gray-900 dark:text-gray-100">Preferences</h4>
                     <div class="space-y-2 text-gray-700 dark:text-gray-300">
                         <p>Newsletter: {{ preferences.newsletter_enabled ? 'Enabled' : 'Disabled' }}</p>
                         <p>Preferred Categories: {{ preferences.preferred_categories?.join(', ') || 'None selected' }}</p>
                         <Link :href="route('profile.edit')" class="mt-2 inline-block text-sm text-primary hover:underline dark:text-primary-light">
                            Change Preferences / Edit Profile
                        </Link>
                     </div>
                </div>

            </div>
        </div>
    </AuthenticatedLayout>
</template> 