<script setup>
import { computed } from 'vue';
import { Head, Link } from '@inertiajs/vue3';
import AuthenticatedLayout from '@/Layouts/AuthenticatedLayout.vue';
import BlogPostCard from '@/Components/Blog/BlogPostCard.vue';
import TheHeader from '@/Components/Layout/Navbar.vue';
import TheFooter from '@/Components/Layout/Footer.vue';

const props = defineProps({
  userProfile: { type: Object, required: true },
  preferences: { type: Object, default: () => ({}) },
  likedPosts: { type: Object, default: () => ({ data: [], links: {} }) },
  bookmarkedPosts: { type: Object, default: () => ({ data: [], links: {} }) },
  recentlyReadArticles: { type: Object, default: () => ({ data: [], links: {} }) },
  followedTopics: { type: Array, default: () => [] },
});

const pageTitle = computed(() => `${props.userProfile.name}'s Profile`);

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
    <TheHeader />
    <Head>
        <title>{{ pageTitle }}</title>
    </Head>

    <AuthenticatedLayout>
        <template #header>
            <h2 class="font-semibold text-xl text-gray-800 dark:text-gray-200 leading-tight">User Profile</h2>
        </template>

        <div class="py-12">
            <div v-if="props.userProfile" class="max-w-7xl mx-auto sm:px-6 lg:px-8 space-y-8">
                <!-- Profile Header -->
                <div class="bg-white dark:bg-gray-800 overflow-hidden shadow-sm sm:rounded-lg p-6 flex flex-col sm:flex-row items-center gap-6">
                     <img :src="props.userProfile.avatar || 'https://via.placeholder.com/150/cccccc/FFFFFF?text=?'" :alt="props.userProfile.name" class="w-24 h-24 rounded-full border-4 border-primary dark:border-primary-light bg-gray-300">
                     <div class="text-center sm:text-left">
                        <h3 class="text-2xl font-semibold text-gray-900 dark:text-gray-100">{{ props.userProfile.name }}</h3>
                        <p class="text-gray-600 dark:text-gray-400">{{ props.userProfile.email }}</p>
                        <p class="text-sm text-gray-500 dark:text-gray-500 mt-1">Joined: {{ formatDate(props.userProfile.created_at) }}</p>
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
                                <h5 class="text-sm font-medium text-gray-500 dark:text-gray-400">Articles Written</h5>
                                <span class="text-2xl font-bold text-gray-900 dark:text-gray-100">
                                    {{ props.userProfile.posts_count || 0 }}
                                </span>
                            </div>
                        </div>
                        
                        <div class="bg-gray-50 dark:bg-gray-700 rounded-lg p-4">
                            <div class="flex items-center justify-between">
                                <h5 class="text-sm font-medium text-gray-500 dark:text-gray-400">Followers</h5>
                                <span class="text-2xl font-bold text-gray-900 dark:text-gray-100">
                                    {{ props.userProfile.followers_count || 0 }}
                                </span>
                            </div>
                        </div>
                        
                        <div class="bg-gray-50 dark:bg-gray-700 rounded-lg p-4">
                            <div class="flex items-center justify-between">
                                <h5 class="text-sm font-medium text-gray-500 dark:text-gray-400">Following</h5>
                                <span class="text-2xl font-bold text-gray-900 dark:text-gray-100">
                                    {{ props.userProfile.following_count || 0 }}
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
                    
                    <div v-if="props.recentlyReadArticles?.data?.length > 0" class="grid grid-cols-1 md:grid-cols-3 gap-6">
                        <BlogPostCard v-for="article in props.recentlyReadArticles.data" :key="article.id" :post="article" />
                    </div>
                    <p v-else class="text-gray-500 dark:text-gray-400">You haven't read any articles yet.</p>
                </div>

                <!-- Liked Articles -->
                <div class="bg-white dark:bg-gray-800 overflow-hidden shadow-sm sm:rounded-lg p-6">
                    <div class="flex justify-between items-center mb-4">
                        <h4 class="text-lg font-semibold text-gray-900 dark:text-gray-100">Liked Articles</h4>
                         <span class="text-sm text-gray-500 dark:text-gray-400">
                            {{ props.likedPosts?.total || 0 }} articles
                        </span>
                    </div>
                    
                    <div v-if="props.likedPosts?.data?.length > 0" class="grid grid-cols-1 md:grid-cols-2 gap-6">
                         <BlogPostCard v-for="article in props.likedPosts.data" :key="article.id" :post="article" />
                         <!-- Pagination for Liked Posts -->
                         <div class="col-span-full mt-4">
                             <Link
                                 v-for="link in props.likedPosts.links"
                                 :key="link.label"
                                 :href="link.url || '#'"
                                 class="px-3 py-1 mx-1 text-sm rounded"
                                 :class="{'bg-primary text-white dark:bg-primary-light dark:text-gray-900': link.active, 'text-gray-600 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-700': !link.active, 'text-gray-400 dark:text-gray-600 cursor-not-allowed': !link.url}"
                                 v-html="link.label"
                                 preserve-scroll
                                 preserve-state
                             />
                         </div>
                    </div>
                    <p v-else class="text-gray-500 dark:text-gray-400">You haven't liked any articles yet.</p>
                </div>

                <!-- Bookmarked Articles -->
                <div class="bg-white dark:bg-gray-800 overflow-hidden shadow-sm sm:rounded-lg p-6">
                    <div class="flex justify-between items-center mb-4">
                        <h4 class="text-lg font-semibold text-gray-900 dark:text-gray-100">Saved Articles</h4>
                        <span class="text-sm text-gray-500 dark:text-gray-400">
                            {{ props.bookmarkedPosts?.total || 0 }} articles
                        </span>
                    </div>
                    
                    <div v-if="props.bookmarkedPosts?.data?.length > 0" class="grid grid-cols-1 md:grid-cols-2 gap-6">
                         <BlogPostCard v-for="article in props.bookmarkedPosts.data" :key="article.id" :post="article" />
                         <!-- Pagination for Bookmarked Posts -->
                          <div class="col-span-full mt-4">
                             <Link
                                 v-for="link in props.bookmarkedPosts.links"
                                 :key="link.label"
                                 :href="link.url || '#'"
                                 class="px-3 py-1 mx-1 text-sm rounded"
                                 :class="{'bg-primary text-white dark:bg-primary-light dark:text-gray-900': link.active, 'text-gray-600 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-700': !link.active, 'text-gray-400 dark:text-gray-600 cursor-not-allowed': !link.url}"
                                 v-html="link.label"
                                 preserve-scroll
                                 preserve-state
                             />
                         </div>
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
                    
                    <div v-if="props.followedTopics?.length > 0" class="flex flex-wrap gap-3 mb-4">
                        <div 
                            v-for="topic in props.followedTopics" 
                            :key="topic.id" 
                            class="px-4 py-2 bg-indigo-100 text-indigo-800 dark:bg-indigo-900 dark:text-indigo-200 rounded-full"
                        >
                            {{ topic.name }}
                        </div>
                    </div>
                    <p v-else class="text-gray-500 dark:text-gray-400">You don't follow any topics yet.</p>
                </div>

                <!-- Preferences -->
                 <div v-if="props.preferences" class="bg-white dark:bg-gray-800 overflow-hidden shadow-sm sm:rounded-lg p-6">
                    <div class="flex justify-between items-center mb-4">
                        <h4 class="text-lg font-semibold text-gray-900 dark:text-gray-100">Preferences</h4>
                        <Link :href="route('profile.edit')" class="text-sm text-indigo-600 dark:text-indigo-400 hover:underline">
                            Edit Preferences
                        </Link>
                    </div>
                    
                     <div class="space-y-2 text-gray-700 dark:text-gray-300">
                         <div class="flex justify-between py-2 border-b border-gray-100 dark:border-gray-700">
                             <span>Newsletter:</span>
                             <span class="font-medium">{{ props.preferences.newsletter_enabled ? 'Subscribed' : 'Not subscribed' }}</span>
                         </div>
                         
                         <div class="flex justify-between py-2 border-b border-gray-100 dark:border-gray-700">
                             <span>Content Personalization:</span>
                             <span class="font-medium">{{ props.preferences.personalization_enabled ? 'Enabled' : 'Disabled' }}</span>
                         </div>
                         
                         <div class="py-2">
                             <p class="mb-2">Preferred Categories:</p>
                             <div class="flex flex-wrap gap-2">
                                 <span 
                                     v-for="(category, index) in props.preferences.preferred_categories" 
                                     :key="index"
                                     class="px-2 py-1 bg-gray-100 dark:bg-gray-700 rounded text-sm"
                                 >
                                     {{ category }}
                                 </span>
                                 <span v-if="!props.preferences.preferred_categories?.length" class="text-gray-500 dark:text-gray-400">
                                     None selected
                                 </span>
                             </div>
                         </div>
                     </div>
                </div>
            </div>
        </div>
    </AuthenticatedLayout>

    <TheFooter />
</template> 