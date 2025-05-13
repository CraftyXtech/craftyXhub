<template>
    <article class="group relative overflow-hidden rounded-xl shadow-lg transition-all duration-300 hover:shadow-xl">
        <div class="relative">
            <img 
                :src="article.image_url || '/default.jpeg'" 
                :alt="article.title"
                class="w-full h-48 object-cover transition-transform duration-300 group-hover:scale-105"
            />
            <div class="absolute inset-0 bg-gradient-to-b from-transparent to-black/50 opacity-0 group-hover:opacity-100 transition-opacity duration-300"></div>
        </div>
        
        <div class="p-6">
            <h3 class="text-xl font-serif font-medium text-neutral-900 mb-3 group-hover:text-neutral-700 transition-colors">
                {{ article.title }}
            </h3>
            
            <p class="text-neutral-600 text-sm mb-4">
                {{ article.excerpt }}
            </p>
            
            <div class="flex items-center justify-between text-xs text-neutral-500">
                <span>{{ article.author }}</span>
                <time>{{ formatDate(article.publishedAt) }}</time>
            </div>
        </div>
    </article>
</template>

<script setup>
const props = defineProps({
    article: {
        type: Object,
        required: true
    }
});

const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
    });
};
</script>