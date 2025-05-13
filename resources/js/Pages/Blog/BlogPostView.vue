<template>
    <div class="min-h-screen bg-gradient-to-b from-white to-neutral-50 font-sans antialiased">

        <Head :title="props.post.title" />
        <Navbar />

        <main>
            <div class="relative h-[50vh] overflow-hidden">
                <div class="absolute inset-0 bg-center bg-cover"
                    :style="`background-image: linear-gradient(to bottom, rgba(0,0,0,0.7), rgba(0,0,0,0.7)), url('${props.post.image_url || '/default.jpeg'}')`">
                </div>

                <div class="absolute inset-0 flex items-end">
                    <div class="container mx-auto max-w-5xl px-4 pb-16 md:pb-24">
                        <div class="max-w-3xl">
                            <nav class="flex text-sm font-medium text-white/90 mb-6">
                                <a href="/" class="hover:text-white transition-colors">Home</a>
                                <span class="mx-2">/</span>
                                <a href="/" class="hover:text-white transition-colors">Blog</a>
                                <span class="mx-2">/</span>
                                <span class="text-white/70 truncate">{{ props.post.title }}</span>
                            </nav>

                            <h1
                                class="text-4xl md:text-5xl lg:text-6xl font-serif font-light text-white mb-6 tracking-tight">
                                {{ props.post.title }}
                            </h1>

                            <div class="flex items-center space-x-6 text-white">

                                <div class="flex items-center space-x-3">
                                    <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 opacity-70" fill="none"
                                        viewBox="0 0 24 24" stroke="currentColor">
                                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                                            d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
                                    </svg>
                                    <time>{{ formatDate(props.post.published_at) }}</time>
                                </div>
                                <div v-if="props.post.category" class="hidden md:flex items-center space-x-3">
                                    <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 opacity-70" fill="none"
                                        viewBox="0 0 24 24" stroke="currentColor">
                                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                                            d="M7 7h.01M7 3h5c.512 0 1.024.195 1.414.586l7 7a2 2 0 010 2.828l-7 7a2 2 0 01-2.828 0l-7-7A1.994 1.994 0 013 12V7a4 4 0 014-4z" />
                                    </svg>
                                    <span>{{ props.post.category.name }}</span>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <div class="container mx-auto max-w-8xl px-4 -mt-10 relative z-10">
                <div class="bg-white rounded-xl shadow-xl p-8 md:p-12 mb-12">
                    <div class="flex justify-between items-center pb-8 mb-8 border-b border-neutral-100">
                        <div class="flex items-center text-sm text-neutral-500">
                            <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 mr-2" fill="none" viewBox="0 0 24 24"
                                stroke="currentColor">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                                    d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
                            </svg>
                            {{ calculateReadingTime(props.post.body) }} min read
                        </div>
                        <div class="flex items-center space-x-4">
                            <button class="transition-transform hover:scale-110" title="Share on Twitter">
                                <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 text-neutral-600"
                                    fill="currentColor" viewBox="0 0 24 24">
                                    <path
                                        d="M24 4.557c-.883.392-1.832.656-2.828.775 1.017-.609 1.798-1.574 2.165-2.724-.951.564-2.005.974-3.127 1.195-.897-.957-2.178-1.555-3.594-1.555-3.179 0-5.515 2.966-4.797 6.045-4.091-.205-7.719-2.165-10.148-5.144-1.29 2.213-.669 5.108 1.523 6.574-.806-.026-1.566-.247-2.229-.616-.054 2.281 1.581 4.415 3.949 4.89-.693.188-1.452.232-2.224.084.626 1.956 2.444 3.379 4.6 3.419-2.07 1.623-4.678 2.348-7.29 2.04 2.179 1.397 4.768 2.212 7.548 2.212 9.142 0 14.307-7.721 13.995-14.646.962-.695 1.797-1.562 2.457-2.549z" />
                                </svg>
                            </button>
                            <button class="transition-transform hover:scale-110" title="Share on Facebook">
                                <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 text-neutral-600"
                                    fill="currentColor" viewBox="0 0 24 24">
                                    <path
                                        d="M9 8h-3v4h3v12h5v-12h3.642l.358-4h-4v-1.667c0-.955.192-1.333 1.115-1.333h2.885v-5h-3.808c-3.596 0-5.192 1.583-5.192 4.615v3.385z" />
                                </svg>
                            </button>
                            <button class="transition-transform hover:scale-110" title="Share on LinkedIn">
                                <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 text-neutral-600"
                                    fill="currentColor" viewBox="0 0 24 24">
                                    <path
                                        d="M4.98 3.5c0 1.381-1.11 2.5-2.48 2.5s-2.48-1.119-2.48-2.5c0-1.38 1.11-2.5 2.48-2.5s2.48 1.12 2.48 2.5zm.02 4.5h-5v16h5v-16zm7.982 0h-4.968v16h4.969v-8.399c0-4.67 6.029-5.052 6.029 0v8.399h4.988v-10.131c0-7.88-8.922-7.593-11.018-3.714v-2.155z" />
                                </svg>
                            </button>
                            <button class="transition-transform hover:scale-110" title="Copy Link">
                                <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 text-neutral-600" fill="none"
                                    viewBox="0 0 24 24" stroke="currentColor">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                                        d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
                                </svg>
                            </button>
                        </div>
                    </div>

                    <div v-if="props.post.tags && props.post.tags.length"
                        class="mt-12 pt-8 border-t border-neutral-100">
                        <div class="flex flex-wrap gap-2">
                            <a v-for="tag in props.post.tags" :key="tag" :href="`/blog/tag/${tag.name}`"
                                class="px-4 py-2 bg-neutral-100 hover:bg-neutral-200 text-neutral-700 rounded-full text-sm font-medium transition-colors">
                                #{{ tag.name }}
                            </a>
                        </div>
                    </div>

                    <article class="prose prose-lg prose-neutral max-w-8xl mx-auto">
                        <p class="text-xl font-light !leading-relaxed text-neutral-700 mb-8">
                            {{ props.post.body }}
                        </p>
                    </article>


                    <div class="mt-12 pt-8 border-t border-neutral-100">
                        <div class="flex flex-col md:flex-row items-center md:items-start gap-6">
                            <img :src="props.post.author.avatar || '/default-user.jpeg'" :alt="props.post.author.name"
                                class="w-16 h-16 md:w-16 md:h-16 rounded-full object-cover" />
                            <div>
                                <h3 class="text-xl font-serif mb-2">About {{ props.post.author.name }}</h3>
                                <p class="text-neutral-600 mb-4">{{ props.post.author.bio || 'Writer and content creator passionate about sharing insights and stories.' }}</p>
                                <div class="flex space-x-4">
                                    <a v-if="props.post.author.twitter" :href="props.post.author.twitter"
                                        target="_blank" class="text-blue-500 hover:text-blue-600">
                                        <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="currentColor"
                                            viewBox="0 0 24 24">
                                            <path
                                                d="M24 4.557c-.883.392-1.832.656-2.828.775 1.017-.609 1.798-1.574 2.165-2.724-.951.564-2.005.974-3.127 1.195-.897-.957-2.178-1.555-3.594-1.555-3.179 0-5.515 2.966-4.797 6.045-4.091-.205-7.719-2.165-10.148-5.144-1.29 2.213-.669 5.108 1.523 6.574-.806-.026-1.566-.247-2.229-.616-.054 2.281 1.581 4.415 3.949 4.89-.693.188-1.452.232-2.224.084.626 1.956 2.444 3.379 4.6 3.419-2.07 1.623-4.678 2.348-7.29 2.04 2.179 1.397 4.768 2.212 7.548 2.212 9.142 0 14.307-7.721 13.995-14.646.962-.695 1.797-1.562 2.457-2.549z" />
                                        </svg>
                                    </a>
                                    <a v-if="props.post.author.linkedin" :href="props.post.author.linkedin"
                                        target="_blank" class="text-blue-700 hover:text-blue-800">
                                        <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="currentColor"
                                            viewBox="0 0 24 24">
                                            <path
                                                d="M4.98 3.5c0 1.381-1.11 2.5-2.48 2.5s-2.48-1.119-2.48-2.5c0-1.38 1.11-2.5 2.48-2.5s2.48 1.12 2.48 2.5zm.02 4.5h-5v16h5v-16zm7.982 0h-4.968v16h4.969v-8.399c0-4.67 6.029-5.052 6.029 0v8.399h4.988v-10.131c0-7.88-8.922-7.593-11.018-3.714v-2.155z" />
                                        </svg>
                                    </a>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <section class="container mx-auto max-w-5xl px-4 py-12">
                <h2 class="text-3xl font-serif text-center mb-2 text-neutral-900">
                    Continue Reading
                    <span class="block h-1 w-24 mx-auto mt-2 bg-gradient-to-r from-blue-500 to-blue-700 rounded-full"></span>
                </h2>
                <p class="text-center text-neutral-600 mb-12">
                    Discover more insightful, inspiring, and expertly crafted articles tailored to your interests and reading journey.
                </p>

                <div class="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
                    <ArticleCard 
                        v-for="article in relatedPosts" 
                        :key="article.id" 
                        :article="article"
                        class="transform transition duration-300 hover:-translate-y-2" 
                    />
                </div>
            </section>

            <SubscribeBanner />
        </main>

        <Footer />

        <button v-show="showBackToTop" @click="scrollToTop"
            class="fixed bottom-8 right-8 bg-white text-dark p-3 rounded-full shadow-lg transition-all duration-300 hover:bg-white"
            aria-label="Back to top">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24"
                stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 10l7-7m0 0l7 7m-7-7v18" />
            </svg>
        </button>
    </div>
</template>


<script setup>
import { ref, onMounted, onUnmounted } from 'vue';
import Navbar from '@/Components/Layout/Navbar.vue';
import { Head } from '@inertiajs/vue3';
import Footer from '@/Components/Layout/Footer.vue';
import ArticleCard from '@/Components/Blog/ArticleCard.vue';
import SubscribeBanner from '@/Components/Shared/SubscribeBanner.vue';

const props = defineProps({
    post: { type: Object, required: true },
    relatedPosts: { type: Object, required: true }
});

const showBackToTop = ref(false);

const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'long',
        day: 'numeric'
    });
};

const calculateReadingTime = (text) => {
    const wordsPerMinute = 200;
    const words = text.trim().split(/\s+/).length;
    return Math.ceil(words / wordsPerMinute);
};

const extractFirstParagraph = (text) => {
    const firstParagraphEnd = text.indexOf('\n\n');
    if (firstParagraphEnd === -1) {
        return text.substring(0, 200) + (text.length > 200 ? '...' : '');
    }
    return text.substring(0, firstParagraphEnd);
};

const checkScroll = () => {
    showBackToTop.value = window.scrollY > 500;
};

const scrollToTop = () => {
    window.scrollTo({
        top: 0,
        behavior: 'smooth'
    });
};

onMounted(() => {
    window.addEventListener('scroll', checkScroll);

    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth'
                });
            }
        });
    });
});

onUnmounted(() => {
    window.removeEventListener('scroll', checkScroll);
});
</script>

<style>
.prose {
    max-width: 70ch;
    line-height: 1.8;
}

.prose h2 {
    font-family: serif;
    margin-top: 2rem;
    margin-bottom: 1rem;
}

.prose p {
    margin-bottom: 1.5rem;
}

.prose img {
    border-radius: 0.5rem;
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
}

.prose a {
    color: #2563eb;
    text-decoration: none;
    border-bottom: 1px solid #bfdbfe;
    transition: border-color 0.2s ease;
}

.prose a:hover {
    border-color: #2563eb;
}

.prose blockquote {
    font-style: italic;
    color: #4b5563;
    border-left: 4px solid #e5e7eb;
    padding-left: 1rem;
    margin-left: 0;
}

/* Animations */
@keyframes fadeIn {
    from {
        opacity: 0;
    }

    to {
        opacity: 1;
    }
}

.fade-in {
    animation: fadeIn 0.5s ease-in-out;
}

/* Scrollbar styling */
body::-webkit-scrollbar {
    width: 12px;
}

body::-webkit-scrollbar-track {
    background: #f1f1f1;
}

body::-webkit-scrollbar-thumb {
    background-color: #c1c1c1;
    border-radius: 6px;
    border: 3px solid #f1f1f1;
}

body::-webkit-scrollbar-thumb:hover {
    background-color: #a8a8a8;
}
</style>