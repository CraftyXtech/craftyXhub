<script setup>
import { ref, computed, onUnmounted, watch } from 'vue';
import { Head, Link, usePage, router } from '@inertiajs/vue3';
import TheHeader from '@/Components/Layout/Navbar.vue';
import TheFooter from '@/Components/Layout/Footer.vue';
import BlogPostCard from '@/Components/Blog/BlogPostCard.vue';
import BlogSidebar from '@/Components/Blog/BlogSidebar.vue';
import SubscribeBanner from '@/Components/Shared/SubscribeBanner.vue';
import CommentSection from '@/Components/Blog/CommentSection.vue';
import TopicExplorer from '@/Components/TopicExplorer.vue';

const props = defineProps({
    post: { type: Object, required: true },
    commentsProp: { type: Object, default: () => ({ data: [], links: {} }) },
    isLiked: { type: Boolean, default: false },
    isSaved: { type: Boolean, default: false },
});

const readingTime = computed(() => {
    if (!props.post || !props.post.readTime) return '0 min';
    return props.post.readTime;
});

const showSummary = ref(false);
const quickSummary = ref('Click button to generate summary...');
const isGeneratingSummary = ref(false);
const summaryError = ref(null);

const generateSummary = () => {
    if (!props.post || isGeneratingSummary.value) return;

    isGeneratingSummary.value = true;
    showSummary.value = true;
    summaryError.value = null;
    quickSummary.value = 'Generating summary...';

    router.post(route('ai.summarize'), {
        post_id: props.post.id
    }, {
        only: ['aiResult'],
        preserveState: true,
        preserveScroll: true,
        onSuccess: (page) => {
            quickSummary.value = page.props.aiResult || 'Summary generated.';
        },
        onError: (errors) => {
            console.error("Error generating summary:", errors);
        summaryError.value = "Could not generate summary at this time.";
            quickSummary.value = '';
        },
        onFinish: () => {
        isGeneratingSummary.value = false;
    }
    });
};

const tableOfContents = computed(() => {
    if (!props.post?.body?.sections) return [];
    return props.post.body.sections.map(section => section.title);
});

const relatedPosts = ref([
     { 
        id: 2, 
        title: 'Photography Tips for Craft Product Listings', 
        slug: 'photography-tips-for-craft-product-listings', 
        excerpt: 'Learn how to take professional-quality photos of your handmade items...', 
        category: 'Technology', 
        readTime: '6 min', 
        imageUrl: 'https://via.placeholder.com/800x600/FF6B6B/FFFFFF?text=Craft+Photography', 
        date: '2023-12-10' 
    },
]);

const likeCount = ref(props.post?.like_count || 0);
const isProcessingInteraction = ref(false);

const page = usePage();
const authUser = computed(() => page.props.auth.user);

watch(() => props.post?.like_count, (newValue) => { likeCount.value = newValue || 0; });

const toggleLike = () => {
    if (!authUser.value) {
        alert('Please log in to like posts.'); 
        return;
    }
    if (isProcessingInteraction.value) return;
    isProcessingInteraction.value = true;

    router.post(route('posts.like', props.post.id), {}, {
        preserveScroll: true,
        onSuccess: () => { 
        },
        onError: (errors) => {
             console.error("Error toggling like:", errors);
        },
        onFinish: () => {
        isProcessingInteraction.value = false;
    }
    });
};

const toggleSave = () => {
    if (!authUser.value) {
        alert('Please log in to save posts.');
        return;
    }
     if (isProcessingInteraction.value) return;
    isProcessingInteraction.value = true;

    router.post(route('posts.save', props.post.id), {}, {
         preserveScroll: true,
         onSuccess: () => { 
         },
         onError: (errors) => {
             console.error("Error toggling save:", errors);
         },
         onFinish: () => {
        isProcessingInteraction.value = false;
    }
    });
};

const readingProgress = ref(0);
const articleContentRef = ref(null);
const recordReadTimeout = ref(null);

const handleScroll = () => {
    if (!articleContentRef.value) return;
    const element = articleContentRef.value;
    const totalHeight = element.scrollHeight - element.clientHeight;
    if (totalHeight <= 0) {
        readingProgress.value = 0;
        return;
    }
    const scrollTop = window.scrollY - element.offsetTop;
    const percentage = Math.max(0, Math.min(100, (scrollTop / totalHeight) * 100));
    readingProgress.value = percentage;

    if (authUser.value && props.post?.id) {
        if (recordReadTimeout.value) clearTimeout(recordReadTimeout.value);
        recordReadTimeout.value = setTimeout(() => {
            recordReadProgress(Math.round(percentage));
        }, 1500);
    }
};

const recordReadProgress = (progress) => {
    if (!authUser.value || !props.post?.id) return;
    router.post(route('posts.read', props.post.id), {
        progress: progress
    }, {
        preserveScroll: true,
    });
};

watch(articleContentRef, (newRef) => {
    if (newRef) {
    window.addEventListener('scroll', handleScroll);
        handleScroll();
    }
});

onUnmounted(() => {
    window.removeEventListener('scroll', handleScroll);
    if (recordReadTimeout.value) clearTimeout(recordReadTimeout.value);
});

const botQuestion = ref('');
const botAnswer = ref('');
const isAskingBot = ref(false);
const botError = ref(null);

const askBot = () => {
    if (!botQuestion.value || isAskingBot.value || !props.post?.id) return;

    isAskingBot.value = true;
    botAnswer.value = 'Thinking...';
    botError.value = null;

    router.post(route('ai.ask'), {
        post_id: props.post.id,
        question: botQuestion.value
    }, {
        only: ['aiAnswer'],
        preserveState: true,
        preserveScroll: true,
        onSuccess: (page) => {
            botAnswer.value = page.props.aiAnswer || 'Got an answer.';
        },
        onError: (errors) => {
            console.error("Error asking bot:", errors);
            botError.value = "Sorry, I couldn't answer that right now.";
            botAnswer.value = '';
        },
        onFinish: () => {
            isAskingBot.value = false;
        }
    });
};
</script>

<template>
    <Head :title="props.post?.title || 'Blog Post'" />
    
    <TheHeader />
    
    <div class="relative">
        <!-- Reading Progress Bar -->
        <div class="fixed top-0 left-0 w-full h-1 z-50">
            <div 
                class="h-full bg-primary dark:bg-primary-light transition-all duration-100 ease-linear"
                :style="{ width: readingProgress + '%' }"
            ></div>
        </div>

        <main class="bg-gray-50 dark:bg-gray-800">
            <div v-if="isGeneratingSummary" class="flex justify-center items-center py-32">
                <div class="animate-spin rounded-full h-16 w-16 border-b-2 border-primary dark:border-primary-light"></div>
            </div>
            <div v-else-if="error" class="text-center py-32 text-red-600 dark:text-red-400">
                <p>{{ error }}</p>
                <Link href="/" class="text-primary dark:text-primary-light hover:underline mt-4 inline-block">Go back home</Link>
            </div>
            <template v-else-if="props.post">
                <!-- Article Header -->
                <section class="py-12 text-center bg-white dark:bg-gray-900">
                    <div class="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8">
                        <h1 class="text-3xl md:text-4xl lg:text-5xl font-bold mb-4 text-gray-900 dark:text-gray-100">
                            {{ props.post.title }}
                        </h1>
                        
                        <p class="text-xl text-gray-600 dark:text-gray-400 max-w-3xl mx-auto mb-6">
                            {{ props.post.excerpt }}
                        </p>
                        
                        <div class="flex flex-wrap justify-center items-center gap-4 text-sm text-gray-500 dark:text-gray-400 mb-6">
                            <span v-if="props.post.category" class="bg-primary text-white px-3 py-1 rounded-md dark:bg-primary-light dark:text-gray-900">{{ props.post.category.name }}</span>
                            <!-- <span v-if="props" class="bg-gray-800 text-white px-3 py-1 rounded-md dark:bg-gray-700 dark:text-gray-200">{{ props.post.author }}</span> -->
                            <span>Published {{ props.post.published_at }}</span>
                            <span class="ml-2"><i class="far fa-clock mr-1"></i> {{ readingTime }}</span>
                        </div>

                        <!-- Interaction Buttons -->
                        <div class="flex justify-center items-center gap-4 mt-4">
                            <button
                                @click="toggleLike"
                                :disabled="isProcessingInteraction"
                                :class="[
                                    'flex items-center gap-1 px-3 py-1 rounded-full border transition-colors duration-200 disabled:opacity-50',
                                    props.isLiked
                                        ? 'bg-red-100 border-red-300 text-red-600 dark:bg-red-900 dark:border-red-700 dark:text-red-400' 
                                        : 'bg-gray-100 border-gray-300 text-gray-600 hover:bg-gray-200 dark:bg-gray-700 dark:border-gray-600 dark:text-gray-300 dark:hover:bg-gray-600'
                                ]"
                            >
                                <i :class="[props.isLiked ? 'fas' : 'far', 'fa-heart']"></i>
                                <span>{{ likeCount }}</span>
                            </button>
                            <button
                                @click="toggleSave"
                                 :disabled="isProcessingInteraction"
                                :class="[
                                    'flex items-center gap-1 px-3 py-1 rounded-full border transition-colors duration-200 disabled:opacity-50',
                                    props.isSaved
                                        ? 'bg-blue-100 border-blue-300 text-blue-600 dark:bg-blue-900 dark:border-blue-700 dark:text-blue-400' 
                                        : 'bg-gray-100 border-gray-300 text-gray-600 hover:bg-gray-200 dark:bg-gray-700 dark:border-gray-600 dark:text-gray-300 dark:hover:bg-gray-600'
                                ]"
                            >
                                <i :class="[props.isSaved ? 'fas' : 'far', 'fa-bookmark']"></i>
                            </button>
                            <button
                                @click="sharePost" 
                                :disabled="isProcessingInteraction"
                                class="flex items-center gap-1 px-3 py-1 rounded-full border bg-gray-100 border-gray-300 text-gray-600 hover:bg-gray-200 dark:bg-gray-700 dark:border-gray-600 dark:text-gray-300 dark:hover:bg-gray-600 transition-colors duration-200 disabled:opacity-50"
                            >
                                <i class="far fa-share-square"></i>
                                <span>Share</span>
                            </button>
                        </div>
                    </div>
                </section>
                
                <!-- Featured Image -->
                <img 
                    :src="props.post.imageUrl || 'https://via.placeholder.com/1200x600/cccccc/FFFFFF?text=No+Image'" 
                    :alt="props.post.title" 
                    class="w-full max-h-[500px] object-cover mb-12 bg-gray-200 dark:bg-gray-700"
                    loading="lazy" 
                >
                
                <!-- Article Content -->
                <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                    <div class="flex flex-col lg:flex-row gap-12 mt-12">
                        <article ref="articleContentRef" class="flex-1 min-w-0 prose prose-lg max-w-none dark:prose-invert">
                            <!-- Introduction -->
                            <p class="text-lg leading-relaxed mb-8 text-gray-800 dark:text-gray-300">
                                {{ props.post.body.introduction }}
                            </p>
                            
                            <!-- Numbered Sections -->
                            <ol class="mb-12">
                                <li 
                                    v-for="(section, index) in props.post.body.sections" 
                                    :key="index"
                                    class="mb-12"
                                    :id="`section-${index + 1}`"
                                >
                                    <h2 class="text-2xl font-semibold mb-4 text-gray-900 dark:text-gray-100">
                                        <span class="text-primary dark:text-primary-light font-bold mr-2">{{ index + 1 }}.</span>
                                        {{ section.title }}
                                    </h2>
                                    <p class="leading-relaxed text-gray-700 dark:text-gray-400">
                                        {{ section.body }}
                                    </p>
                                </li>
                            </ol>
                            
                            <!-- Conclusion -->
                            <div class="border-t border-gray-200 dark:border-gray-700 pt-8 mt-12 italic text-gray-600 dark:text-gray-400">
                                <p class="mb-2">
                                    <strong class="font-semibold text-gray-800 dark:text-gray-200 not-italic">Summary</strong>
                                </p>
                                <p>{{ props.post.body.conclusion }}</p>
                            </div>

                            <!-- Topic Explorer -->
                            <TopicExplorer :category="props.post.category" :tags="props.post.tags" />

                            <!-- Summarizer Button -->
                            <div class="mt-8 text-center">
                                <button 
                                    @click="generateSummary" 
                                    :disabled="isGeneratingSummary"
                                    class="bg-secondary hover:bg-opacity-80 text-white font-bold py-2 px-4 rounded dark:bg-gray-600 dark:hover:bg-gray-500 disabled:opacity-50"
                                >
                                    {{ isGeneratingSummary ? 'Generating...' : (showSummary && quickSummary && !summaryError ? 'Hide Summary' : 'Show Quick Summary') }}
                                </button>
                                <div v-if="showSummary" class="mt-4 p-4 border border-gray-200 dark:border-gray-700 rounded bg-gray-100 dark:bg-gray-700 text-left">
                                    <p v-if="summaryError" class="text-red-600 dark:text-red-400 text-sm">{{ summaryError }}</p>
                                    <p v-else class="text-gray-700 dark:text-gray-300">{{ quickSummary }}</p>
                                </div>
                            </div>
                        </article>
                        
                        <!-- Sidebar -->
                        <div class="lg:w-80 flex-shrink-0">
                            <div class="sticky top-8">
                                <BlogSidebar 
                                    :table-of-contents="tableOfContents" 
                                    :post-title="props.post.title" 
                                />
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Comment Section -->
                <div class="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
                    <CommentSection :post-id="props.post.id" :comments="props.commentsProp" />
                </div>

                <!-- Related Articles Section -->
                <section class="py-16 mt-12 border-t border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-900">
                    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                        <h2 class="text-3xl font-bold text-center mb-12 text-gray-900 dark:text-gray-100">Related Articles</h2>
                        
                        <div class="grid grid-cols-1 md:grid-cols-3 gap-8">
                            <BlogPostCard 
                                v-for="relatedPostItem in relatedPosts" 
                                :key="relatedPostItem.id" 
                                :post="relatedPostItem" 
                            />
                        </div>
                    </div>
                </section>
                
                <SubscribeBanner />
            </template>
        </main>
    </div>
    
    <TheFooter />
</template> 