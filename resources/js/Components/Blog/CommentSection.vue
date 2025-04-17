<script setup>
import { ref, onMounted, watch, computed } from 'vue';
import axios from 'axios';
import { usePage } from '@inertiajs/vue3'; // Import usePage to access auth user

const props = defineProps({
    postId: {
        type: Number,
        required: true
    }
});

const page = usePage();
const authUser = computed(() => page.props.auth.user); // Access authenticated user

// State for comments
const comments = ref([]);
const isLoadingComments = ref(true);
const commentError = ref(null);
const paginationData = ref(null);

// State for new comment form
const newComment = ref('');
const submitting = ref(false);
const submitError = ref(null);

// --- Fetch Comments --- 
const fetchComments = async (page = 1) => {
    isLoadingComments.value = true;
    commentError.value = null;
    try {
        const response = await axios.get(`/api/posts/${props.postId}/comments`, { params: { page } });
        if (page === 1) {
            comments.value = response.data.data;
        } else {
             // Append for load more (adjust if using standard pagination)
             comments.value.push(...response.data.data);
        }
        paginationData.value = response.data.meta;
    } catch (error) {
        console.error("Error fetching comments:", error);
        commentError.value = "Failed to load comments.";
    } finally {
        isLoadingComments.value = false;
    }
};

// --- Submit Comment ---
const submitComment = async () => {
    if (!newComment.value.trim() || !authUser.value) return; // Check if user is logged in

    submitting.value = true;
    submitError.value = null;
    try {
        const response = await axios.post(`/api/posts/${props.postId}/comments`, {
            body: newComment.value,
            // parent_id: null // Add logic for replying later
        });
        
        // Add the new comment to the top/bottom of the list
        comments.value.unshift(response.data); // Add to top
        newComment.value = '';
        // Optionally refetch page 1 or handle pagination update
        if (paginationData.value) paginationData.value.total++; // Increment total count

    } catch (error) {
        console.error("Error submitting comment:", error);
        if (error.response && error.response.status === 422) {
             submitError.value = error.response.data.message || "Validation failed."; // Show validation errors if possible
        } else if (error.response && error.response.status === 401) {
            submitError.value = "You must be logged in to comment.";
        } else {
            submitError.value = "Failed to submit comment. Please try again.";
        }
    } finally {
        submitting.value = false;
    }
};

// --- Load More Comments --- (Example)
const loadMoreComments = () => {
    if (paginationData.value && paginationData.value.current_page < paginationData.value.last_page) {
        fetchComments(paginationData.value.current_page + 1);
    }
};

// Fetch comments when the component mounts or postId changes
onMounted(() => {
    fetchComments();
});
watch(() => props.postId, () => {
    fetchComments(); // Refetch if post ID changes (e.g., navigating between posts)
});

</script>

<template>
    <div class="mt-16 border-t border-gray-200 dark:border-gray-700 pt-12">
        <h2 class="text-2xl font-bold mb-6 text-gray-900 dark:text-gray-100">Comments ({{ paginationData?.total ?? 0 }})</h2>

        <!-- Comment Form (Only show if logged in) -->
        <div v-if="authUser" class="mb-8 p-4 border border-gray-200 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800">
            <h3 class="text-lg font-semibold mb-2 text-gray-800 dark:text-gray-200">Leave a Comment</h3>
             <textarea 
                v-model="newComment"
                rows="4"
                placeholder="Share your thoughts..."
                class="w-full p-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-200 focus:outline-none focus:ring-2 focus:ring-primary dark:focus:ring-primary-light focus:border-primary dark:focus:border-primary-light"
                :disabled="submitting"
            ></textarea>
            <button
                @click="submitComment"
                :disabled="submitting || !newComment.trim()"
                class="mt-2 px-4 py-2 bg-primary hover:bg-primary-dark text-white font-semibold rounded-md transition duration-200 disabled:opacity-50 dark:bg-primary-light dark:hover:bg-primary dark:text-gray-900"
            >
                {{ submitting ? 'Submitting...' : 'Submit Comment' }}
            </button>
             <p v-if="submitError" class="text-sm text-red-600 dark:text-red-400 mt-2">{{ submitError }}</p>
        </div>
         <div v-else class="mb-8 p-4 border border-gray-200 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 text-center">
             <p class="text-gray-600 dark:text-gray-400">Please <Link :href="route('login')" class="text-primary dark:text-primary-light hover:underline">log in</Link> or <Link :href="route('register')" class="text-primary dark:text-primary-light hover:underline">register</Link> to leave a comment.</p>
         </div>

        <!-- Comment List -->
        <div v-if="isLoadingComments && comments.length === 0" class="text-center py-8">
             <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-primary dark:border-primary-light mx-auto"></div>
        </div>
        <div v-else-if="commentError" class="text-center py-8 text-red-600 dark:text-red-400">
            {{ commentError }}
        </div>
        <div v-else-if="comments.length > 0" class="space-y-6">
            <div v-for="comment in comments" :key="comment.id" class="p-4 border border-gray-200 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800">
                <div class="flex items-start space-x-4">
                    <img :src="comment.author?.avatar || 'https://via.placeholder.com/40/cccccc/FFFFFF?text=?'" :alt="comment.author?.name || 'User'" class="w-10 h-10 rounded-full flex-shrink-0 bg-gray-300 dark:bg-gray-600">
                    <div class="flex-1">
                        <div class="flex items-center justify-between mb-1">
                            <span class="font-semibold text-gray-800 dark:text-gray-200">{{ comment.author?.name || 'Anonymous' }}</span>
                            <span class="text-xs text-gray-500 dark:text-gray-400">{{ comment.date }}</span>
                        </div>
                        <p class="text-gray-700 dark:text-gray-300">{{ comment.body }}</p>

                        <!-- Replies -->
                        <div v-if="comment.replies && comment.replies.length > 0" class="mt-4 pl-6 border-l-2 border-gray-200 dark:border-gray-600 space-y-4">
                             <div v-for="reply in comment.replies" :key="reply.id" class="flex items-start space-x-3">
                                 <img :src="reply.author?.avatar || 'https://via.placeholder.com/40/cccccc/FFFFFF?text=?'" :alt="reply.author?.name || 'User'" class="w-8 h-8 rounded-full flex-shrink-0 bg-gray-300 dark:bg-gray-600">
                                 <div class="flex-1">
                                     <div class="flex items-center justify-between mb-1">
                                        <span class="font-semibold text-sm text-gray-800 dark:text-gray-200">{{ reply.author?.name || 'Anonymous' }}</span>
                                        <span class="text-xs text-gray-500 dark:text-gray-400">{{ reply.date }}</span>
                                    </div>
                                    <p class="text-sm text-gray-700 dark:text-gray-300">{{ reply.body }}</p>
                                 </div>
                             </div>
                        </div>
                         <!-- Add Reply Button (Mock UI - Needs implementation) -->
                         <button v-if="authUser" class="mt-2 text-xs text-primary dark:text-primary-light hover:underline">Reply</button>
                    </div>
                </div>
            </div>
            <!-- Load More Button -->
             <div v-if="paginationData && paginationData.current_page < paginationData.last_page" class="text-center pt-4">
                 <button @click="loadMoreComments" :disabled="isLoadingComments" class="text-sm text-primary dark:text-primary-light hover:underline disabled:opacity-50">
                     {{ isLoadingComments ? 'Loading...' : 'Load More Comments' }}
                 </button>
             </div>
        </div>
        <div v-else class="text-center text-gray-500 dark:text-gray-400 py-8">
            No comments yet. Be the first to share your thoughts!
        </div>
    </div>
</template> 