<script setup>
import { ref, computed } from 'vue';
import { Link, router } from '@inertiajs/vue3';

const props = defineProps({
    followed: {
        type: Array,
        default: () => []
    },
    suggestedTopics: {
        type: Array,
        default: () => []
    }
});

// Local state
const processingTopics = ref(new Set());

// Check if there are any topics to display
const hasFollowedTopics = computed(() => props.followed && props.followed.length > 0);
const hasSuggestions = computed(() => props.suggestedTopics && props.suggestedTopics.length > 0);

// Follow or unfollow a topic
const toggleFollowTopic = (topicId) => {
    if (processingTopics.value.has(topicId)) return;
    
    processingTopics.value.add(topicId);
    
    // Use Inertia router
    router.post(route('topics.follow'), { 
        tagId: topicId // Send tagId (or topic_id based on backend)
    }, {
        preserveScroll: true,
        preserveState: true, // Keep other page state
        onSuccess: () => {
            // Data should refresh automatically via controller redirect/prop update
        },
        onError: (errors) => {
            console.error(`Error toggling follow for topic ${topicId}:`, errors);
            // Add user feedback if necessary
        },
        onFinish: () => {
            processingTopics.value.delete(topicId);
        }
    });
};

// Get button style based on following status
const getButtonStyle = (isFollowing) => {
    return isFollowing 
        ? 'bg-indigo-100 text-indigo-800 hover:bg-indigo-200 dark:bg-indigo-900 dark:text-indigo-200 dark:hover:bg-indigo-800' 
        : 'bg-gray-100 text-gray-800 hover:bg-gray-200 dark:bg-gray-700 dark:text-gray-200 dark:hover:bg-gray-600';
};
</script>

<template>
    <div class="bg-white dark:bg-gray-900 rounded-lg shadow-sm overflow-hidden">
        <div class="p-6">
            <h2 class="text-2xl font-bold mb-6 text-gray-900 dark:text-gray-100">
                Topics You Follow
            </h2>
            
            <div v-if="hasFollowedTopics" class="mb-8">
                <div class="flex flex-wrap gap-3">
                    <button
                        v-for="topic in followed"
                        :key="topic.id"
                        @click="toggleFollowTopic(topic.id)"
                        :disabled="processingTopics.has(topic.id)"
                        class="px-4 py-2 rounded-full text-sm font-medium transition-colors relative bg-indigo-100 text-indigo-800 hover:bg-indigo-200 dark:bg-indigo-900 dark:text-indigo-200 dark:hover:bg-indigo-800"
                    >
                        {{ topic.name }}
                        <span class="ml-1">✓</span>
                        <span v-if="processingTopics.has(topic.id)" class="absolute -top-1 -right-1 w-3 h-3 rounded-full animate-pulse bg-indigo-500"></span>
                    </button>
                </div>
                
                <p class="text-sm text-gray-500 dark:text-gray-400 mt-4">
                    Click on a topic to unfollow
                </p>
            </div>
            
            <div v-else class="text-center py-6 mb-6">
                <p class="text-gray-500 dark:text-gray-400 mb-4">
                    You aren't following any topics yet.
                </p>
                <p class="text-gray-600 dark:text-gray-300">
                    Follow topics to see more personalized content.
                </p>
            </div>
            
            <!-- Suggested Topics -->
            <div v-if="hasSuggestions" class="mt-8">
                <h3 class="text-lg font-medium mb-4 text-gray-800 dark:text-gray-200">
                    Suggested Topics
                </h3>
                
                <div class="flex flex-wrap gap-3">
                    <button
                        v-for="topic in suggestedTopics"
                        :key="topic.id"
                        @click="toggleFollowTopic(topic.id)"
                        :disabled="processingTopics.has(topic.id)"
                        :class="[
                            'px-4 py-2 rounded-full text-sm font-medium transition-colors relative',
                            getButtonStyle(false)
                        ]"
                    >
                        {{ topic.name }}
                        <span v-if="processingTopics.has(topic.id)" class="absolute -top-1 -right-1 w-3 h-3 rounded-full animate-pulse bg-indigo-500"></span>
                    </button>
                </div>
            </div>
            
            <div class="mt-8 text-center">
                <Link 
                    :href="route('profile.view')" 
                    class="inline-flex items-center px-4 py-2 bg-indigo-600 border border-transparent rounded-md font-semibold text-xs text-white uppercase tracking-widest hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 dark:focus:ring-offset-gray-800 transition ease-in-out duration-150"
                >
                    Manage All Topics
                </Link>
            </div>
        </div>
    </div>
</template> 