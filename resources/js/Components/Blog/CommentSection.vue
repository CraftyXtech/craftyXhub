<script setup>
import { ref, computed, watch } from 'vue';
import { usePage, useForm, Link } from '@inertiajs/vue3'; // Import useForm and Link

const props = defineProps({
    postId: {
        type: Number,
        required: true
    },
    // Add prop to receive comments passed from parent
    comments: {
        type: Object, // Expecting Laravel Paginator structure { data: [], links: {}, ... }
        default: () => ({ data: [], links: {} })
    }
});

const page = usePage();
const authUser = computed(() => page.props.auth.user);

// --- Form Handling with useForm --- 
const form = useForm({
    body: '',
    parent_id: null // Add logic later if reply functionality is needed
});

// --- Submit Comment ---
const submitComment = () => {
    if (!form.body.trim() || !authUser.value) return;

    form.post(route('posts.comments.store', props.postId), {
        preserveScroll: true, // Keep user scroll position
        onSuccess: () => {
            form.reset('body'); // Clear the textarea on success
            // Comments list will update automatically on next page visit/reload
            // due to the redirect in the controller.
            // If optimistic UI update is desired, it needs manual handling here.
        },
        onError: (errors) => {
            // Validation errors are automatically available in form.errors
            console.error("Error submitting comment:", errors);
        },
        // onFinish: () => { /* Form processing state resets automatically */ }
    });
};

</script>

<template>
    <div class="mt-16 border-t border-gray-200 dark:border-gray-700 pt-12">
        <!-- Use props.comments.total if available from pagination -->
        <h2 class="text-2xl font-bold mb-6 text-gray-900 dark:text-gray-100">Comments ({{ props.comments?.total ?? props.comments?.data?.length ?? 0 }})</h2>

        <!-- Comment Form (Only show if logged in) -->
        <form @submit.prevent="submitComment" v-if="authUser" class="mb-8 p-4 border border-gray-200 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800">
            <h3 class="text-lg font-semibold mb-2 text-gray-800 dark:text-gray-200">Leave a Comment</h3>
            <div>
                 <textarea 
                    v-model="form.body"
                    rows="4"
                    placeholder="Share your thoughts..."
                    class="w-full p-2 border rounded-md bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-200 focus:outline-none focus:ring-2 focus:ring-primary dark:focus:ring-primary-light dark:focus:border-primary-light"
                    :class="{ 'border-red-500 dark:border-red-400': form.errors.body, 'border-gray-300 dark:border-gray-600': !form.errors.body }"
                    :disabled="form.processing"
                ></textarea>
                 <p v-if="form.errors.body" class="text-sm text-red-600 dark:text-red-400 mt-1">{{ form.errors.body }}</p>
             </div>
             <button
                type="submit"
                :disabled="form.processing || !form.body.trim()"
                class="mt-2 px-4 py-2 bg-primary hover:bg-primary-dark text-white font-semibold rounded-md transition duration-200 disabled:opacity-50 dark:bg-primary-light dark:hover:bg-primary dark:text-gray-900"
            >
                {{ form.processing ? 'Submitting...' : 'Submit Comment' }}
            </button>
             <!-- Display general form errors if needed -->
             <p v-if="form.hasErrors && !form.errors.body" class="text-sm text-red-600 dark:text-red-400 mt-2">An error occurred. Please try again.</p>
        </form>
         <div v-else class="mb-8 p-4 border border-gray-200 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 text-center">
             <p class="text-gray-600 dark:text-gray-400">Please <Link :href="route('login')" class="text-primary dark:text-primary-light hover:underline">log in</Link> or <Link :href="route('register')" class="text-primary dark:text-primary-light hover:underline">register</Link> to leave a comment.</p>
         </div>

        <!-- Comment List -->
        <div v-if="props.comments?.data?.length > 0" class="space-y-6">
            <div v-for="comment in props.comments.data" :key="comment.id" class="p-4 border border-gray-200 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800">
                <div class="flex items-start space-x-4">
                    <img :src="comment.user?.avatar || 'https://via.placeholder.com/40/cccccc/FFFFFF?text=?'" :alt="comment.user?.name || 'User'" class="w-10 h-10 rounded-full flex-shrink-0 bg-gray-300 dark:bg-gray-600">
                    <div class="flex-1">
                        <div class="flex items-center justify-between mb-1">
                            <span class="font-semibold text-gray-800 dark:text-gray-200">{{ comment.user?.name || 'Anonymous' }}</span>
                            <span class="text-xs text-gray-500 dark:text-gray-400">{{ comment.created_at_formatted || comment.created_at }}</span>
                        </div>
                        <p class="text-gray-700 dark:text-gray-300 whitespace-pre-wrap">{{ comment.body }}</p>

                        <!-- Replies -->
                        <div v-if="comment.replies && comment.replies.length > 0" class="mt-4 pl-6 border-l-2 border-gray-200 dark:border-gray-600 space-y-4">
                             <div v-for="reply in comment.replies" :key="reply.id" class="flex items-start space-x-3">
                                 <img :src="reply.user?.avatar || 'https://via.placeholder.com/40/cccccc/FFFFFF?text=?'" :alt="reply.user?.name || 'User'" class="w-8 h-8 rounded-full flex-shrink-0 bg-gray-300 dark:bg-gray-600">
                                 <div class="flex-1">
                                     <div class="flex items-center justify-between mb-1">
                                        <span class="font-semibold text-sm text-gray-800 dark:text-gray-200">{{ reply.user?.name || 'Anonymous' }}</span>
                                        <span class="text-xs text-gray-500 dark:text-gray-400">{{ reply.created_at_formatted || reply.created_at }}</span>
                                    </div>
                                    <p class="text-sm text-gray-700 dark:text-gray-300 whitespace-pre-wrap">{{ reply.body }}</p>
                                 </div>
                             </div>
                        </div>
                    </div>
                </div>
            </div>
            <!-- Pagination -->
            <div v-if="props.comments.links && props.comments.links.length > 3" class="mt-8 flex justify-center">
                <div class="flex flex-wrap -mb-1">
                    <template v-for="(link, key) in props.comments.links" :key="key">
                        <div 
                            v-if="link.url === null" 
                            class="mr-1 mb-1 px-4 py-3 text-sm leading-4 text-gray-400 border rounded"
                            v-html="link.label"
                        ></div>
                        <Link 
                            v-else 
                            class="mr-1 mb-1 px-4 py-3 text-sm leading-4 border rounded hover:bg-white focus:border-primary focus:text-primary dark:hover:bg-gray-700 dark:focus:border-primary-light dark:focus:text-primary-light"
                            :class="{ 'bg-white dark:bg-gray-700': link.active }" 
                            :href="link.url" 
                            v-html="link.label" 
                            :preserve-state="true"
                            :preserve-scroll="true"
                            :only="['commentsProp']"
                        ></Link>
                    </template>
                </div>
            </div>
        </div>
        <div v-else class="text-center text-gray-500 dark:text-gray-400 py-8">
            No comments yet. Be the first to share your thoughts!
        </div>
    </div>
</template> 