<template>
    <article
        class="group relative overflow-hidden rounded-xl bg-white shadow-md transition-all duration-500 hover:shadow-xl hover:translate-y-px">
        <div class="relative h-56 overflow-hidden">
            <img :src="article.image_url || '/default.jpeg'" :alt="article.title"
                class="h-full w-full object-cover transition-transform duration-700 group-hover:scale-110" />
            <div class="absolute inset-0 bg-gradient-to-t from-black/60 to-transparent opacity-60"></div>

            <span v-if="article.category"
                class="absolute top-4 left-4 rounded-full bg-blue-500 px-3 py-1 text-xs font-medium text-white shadow-lg">
                {{ article.category.name }}
            </span>

            <span
                class="absolute top-4 right-4 rounded-full bg-black/40 backdrop-blur-sm px-3 py-1 text-xs font-medium text-white">
                {{ article.reading_time || 10 }} min read
            </span>
        </div>

        <div class="relative p-6">
            <h3
                class="mb-3 font-serif text-xl font-bold leading-tight text-neutral-900 group-hover:text-primary-700 transition-colors duration-300">
                {{ article.title }}
            </h3>

            <p class="mb-5 text-sm text-neutral-600 line-clamp-3">
                {{ article.excerpt }}
            </p>

            <div class="flex items-center justify-between border-t border-neutral-100 pt-4">
                <div class="flex items-center space-x-3">
                    <img v-if="article.author.avatar" :src="article.author.avatar" :alt="article.author.name"
                        class="h-8 w-8 rounded-full object-cover" />
                    <div v-else
                        class="h-8 w-8 rounded-full bg-neutral-200 flex items-center justify-center text-xs text-neutral-500">
                        {{ getInitials(article.author.name) }}
                    </div>
                    <span class="text-sm font-medium text-neutral-700">{{ article.author.name }}</span>
                </div>

                <time class="text-xs text-neutral-500">{{ formatDate(article.published_at) }}</time>
            </div>

            <a :href="`/blog/${article.slug}`"
                class="mt-4 flex items-center text-sm font-medium text-primary-600 group-hover:text-primary-700">
                <span>Read Article</span>
                <svg xmlns="http://www.w3.org/2000/svg"
                    class="h-4 w-4 ml-1 transform transition-transform duration-300 group-hover:translate-x-1"
                    fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
                </svg>
            </a>
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

const getInitials = (name) => {
    return name
        .split(' ')
        .map(part => part[0])
        .join('')
        .substring(0, 2)
        .toUpperCase();
};
</script>

<style scoped>
/* Add Tailwind directive if needed, or use these custom styles */
.line-clamp-3 {
    display: -webkit-box;
    -webkit-line-clamp: 3;
    -webkit-box-orient: vertical;
    overflow: hidden;
}

/* Define any custom colors needed */
:root {
    --primary-600: #2563eb;
    --primary-700: #1d4ed8;
}

.bg-primary-600 {
    background-color: var(--primary-600);
}

.text-primary-600 {
    color: var(--primary-600);
}

.text-primary-700 {
    color: var(--primary-700);
}

.group-hover\:text-primary-700:hover {
    color: var(--primary-700);
}
</style>