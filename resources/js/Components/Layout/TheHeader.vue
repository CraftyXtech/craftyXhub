<script setup>
import { Link } from '@inertiajs/vue3';
import { ref } from 'vue';

const props = defineProps({
    categories: {
        type: Array,
        default: () => [
            { name: 'Technology', route: 'technology' },
            { name: 'Crafts', route: 'crafts' },
            { name: 'DIY', route: 'diy' },
            { name: 'Art', route: 'art' },
            { name: 'Home Decor', route: 'home-decor' },
            { name: 'Jewelry', route: 'jewelry' },
            { name: 'Handmade', route: 'handmade' },
            { name: 'Community', route: 'community' }
        ]
    }
});

// Split categories into two groups for the nav
const leftCategories = ref(props.categories.slice(0, Math.ceil(props.categories.length / 2)));
const rightCategories = ref(props.categories.slice(Math.ceil(props.categories.length / 2)));
</script>

<template>
    <header class="bg-white py-4 border-b border-gray-200">
        <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div class="flex items-center">
                <!-- Left navigation -->
                <nav class="flex-1 hidden md:block">
                    <ul class="flex items-center justify-end">
                        <li v-for="category in leftCategories" :key="category.name" class="mr-6">
                            <Link 
                                :href="route(category.route)" 
                                class="text-gray-800 hover:text-primary relative px-3 py-2"
                            >
                                {{ category.name }}
                                <span class="absolute text-xs top-1/2 -right-3 transform -translate-y-1/2">▼</span>
                            </Link>
                        </li>
                    </ul>
                </nav>

                <!-- Center logo -->
                <div class="text-center mx-4">
                    <Link :href="route('home')" class="font-heading text-2xl text-primary inline-block">
                        CraftyXhub
                    </Link>
                </div>
                
                <!-- Right navigation -->
                <nav class="flex-1 hidden md:block">
                    <ul class="flex items-center">
                        <li v-for="category in rightCategories" :key="category.name" class="ml-6">
                            <Link 
                                :href="route(category.route)" 
                                class="text-gray-800 hover:text-primary relative px-3 py-2"
                            >
                                {{ category.name }}
                                <span class="absolute text-xs top-1/2 -right-3 transform -translate-y-1/2">▼</span>
                            </Link>
                        </li>
                    </ul>
                </nav>
                
                <!-- Mobile menu button -->
                <div class="md:hidden flex justify-between w-full">
                    <Link :href="route('home')" class="font-heading text-2xl text-primary">
                        CraftyXhub
                    </Link>
                    <button class="text-gray-800">
                        <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16" />
                        </svg>
                    </button>
                </div>
            </div>
        </div>
    </header>
</template> 