<template>
    <div class="min-h-screen bg-neutral-50 font-sans antialiased">
        <Navbar />
        
        <div v-if="props.post" class="container mx-auto max-w-4xl px-4 py-12">
            <header class="text-center mb-12">
                <h1 class="text-4xl md:text-5xl font-serif font-light tracking-tight text-neutral-900 mb-6">
                    {{ props.post.title }}
                </h1>
                
                <div class="flex justify-center items-center space-x-4 text-neutral-600 text-sm mb-8">
                    <span>{{ props.post.author.name }}</span>
                    <span class="h-4 border-l border-neutral-300"></span>
                    <time>{{ formatDate(props.post.published_at) }}</time>
                </div>
            </header>

            <figure class="mb-12 overflow-hidden rounded-xl shadow-lg">
                <img 
                    :src="props.post.image_url || '/default.jpeg'"
                    :alt="props.post.title"
                    class="w-full h-[500px] object-cover transition-transform duration-300 hover:scale-105"
                    loading="lazy"
                />
            </figure>

            <article class="prose prose-neutral max-w-prose mx-auto">
                <p class="text-medium text-neutral-900 leading-relaxed mb-8">
                    {{ props.post.body }}
                </p>
            </article>

            <section class="mt-16 pt-12 border-t border-neutral-200">
                <h2 class="text-3xl font-serif text-center mb-12 text-neutral-900">
                    Continue Reading
                </h2>

                <div class="grid md:grid-cols-3 gap-8">
                    <ArticleCard 
                        v-for="article in relatedPosts" 
                        :key="article.id"
                        :article="article"
                    />
                </div>
            </section>
        </div>

        <Footer />
    </div>
</template>

<script setup>
import { ref } from 'vue';
import Navbar from '@/Components/Layout/Navbar.vue';
import Footer from '@/Components/Layout/Footer.vue';
import ArticleCard from '@/Pages/Blog/ArticleCard.vue';

const props = defineProps({
    post: { type: Object, required: true },
});

const relatedPosts = ref([
    {
        id: 1,
        title: 'Crafting Digital Experiences',
        excerpt: 'Exploring the intersection of design and technology.',
        author: 'Elena Rodriguez',
        imageUrl: 'https://via.placeholder.com/800x600',
        publishedAt: '2024-05-10'
    },
    {
        id: 2,
        title: 'The Art of Minimalism',
        excerpt: 'Finding beauty in simplicity and purposeful design.',
        author: 'Marcus Chen',
        imageUrl: 'https://via.placeholder.com/800x600',
        publishedAt: '2024-05-15'
    },
    {
        id: 3,
        title: 'Future of User Interface',
        excerpt: 'Emerging trends in interactive design.',
        author: 'Sophia Kim',
        imageUrl: 'https://via.placeholder.com/800x600',
        publishedAt: '2024-05-20'
    }
]);

const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'long',
        day: 'numeric'
    });
};
</script>

<style>
.prose {
    max-width: 65ch;
    line-height: 1.75;
}
</style>
