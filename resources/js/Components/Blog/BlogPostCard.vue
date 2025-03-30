<script setup>
import { Link } from '@inertiajs/vue3';

defineProps({
    post: {
        type: Object,
        required: true,
        // Expected structure of post:
        // {
        //   id: Number,
        //   title: String,
        //   slug: String,
        //   excerpt: String,
        //   category: String,
        //   readTime: String,
        //   imageUrl: String,
        //   date: String (optional)
        // }
    }
});
</script>

<template>
    <article class="bg-white border border-gray-200 rounded-lg overflow-hidden shadow-sm hover:shadow-md transition duration-200 transform hover:-translate-y-1">
        <img 
            :src="post.imageUrl" 
            :alt="post.title" 
            class="w-full h-48 object-cover"
        >
        <div class="p-6">
            <div class="flex justify-between items-center text-sm mb-2">
                <span class="text-primary font-medium">{{ post.category }}</span>
                <span class="text-gray-500">{{ post.readTime }} read</span>
            </div>
            
            <h3 class="text-xl font-semibold mb-2 leading-tight">
                <Link 
                    :href="route('blog.show', { slug: post.slug })" 
                    class="text-gray-800 hover:text-primary"
                >
                    {{ post.title }}
                </Link>
            </h3>
            
            <p class="text-gray-600 text-sm mb-4 line-clamp-3">
                {{ post.excerpt }}
            </p>
            
            <Link 
                :href="route('blog.show', { slug: post.slug })" 
                class="font-medium text-sm text-primary hover:text-primary-dark"
            >
                Continue Reading
            </Link>
        </div>
    </article>
</template> 