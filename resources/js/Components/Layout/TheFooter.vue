<script setup>
import { Link } from '@inertiajs/vue3';

const footerCategories = [
    {
        title: 'TECHNOLOGY',
        links: [
            { name: 'AI & Tech', route: 'technology' },
            { name: 'Software & Apps', route: 'technology' },
            { name: 'Cybersecurity', route: 'technology' }
        ]
    },
    {
        title: 'CRAFTS',
        links: [
            { name: 'Knitting', route: 'crafts' },
            { name: 'Pottery', route: 'crafts' },
            { name: 'Paper Crafts', route: 'crafts' },
            { name: 'DIY Projects', route: 'diy' }
        ]
    },
    {
        title: 'ART',
        links: [
            { name: 'Painting', route: 'art' },
            { name: 'Digital Art', route: 'art' },
            { name: 'Sculpture', route: 'art' },
            { name: 'Drawing', route: 'art' }
        ]
    },
    {
        title: 'HOME DECOR',
        links: [
            { name: 'Furniture', route: 'home-decor' },
            { name: 'Textiles', route: 'home-decor' },
            { name: 'Wall Art', route: 'home-decor' },
            { name: 'Seasonal Decor', route: 'home-decor' }
        ]
    },
    {
        title: 'JEWELRY',
        links: [
            { name: 'Beaded', route: 'jewelry' },
            { name: 'Metal Work', route: 'jewelry' },
            { name: 'Wire Jewelry', route: 'jewelry' },
            { name: 'Vintage', route: 'jewelry' },
            { name: 'Custom Designs', route: 'jewelry' }
        ]
    },
    {
        title: 'HANDMADE',
        links: [
            { name: 'Clothing', route: 'handmade' },
            { name: 'Accessories', route: 'handmade' },
            { name: 'Gifts', route: 'handmade' }
        ]
    },
    {
        title: 'COMMUNITY',
        links: [
            { name: 'Interviews', route: 'community' },
            { name: 'Success Stories', route: 'community' },
            { name: 'Artist Features', route: 'community' },
            { name: 'Workshops', route: 'community' }
        ]
    },
    {
        title: 'ABOUT',
        links: [
            { name: 'Our Story', route: 'home' },
            { name: 'Contact Us', route: 'home' },
            { name: 'Careers', route: 'home' }
        ]
    }
];

const currentYear = new Date().getFullYear();
</script>

<template>
    <footer class="bg-gray-900 text-gray-200 py-12 text-sm">
        <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div class="flex flex-wrap justify-between gap-6 mb-12">
                <div 
                    v-for="category in footerCategories" 
                    :key="category.title" 
                    class="flex-1 min-w-[150px]"
                >
                    <h4 class="text-white text-base font-semibold mb-4">{{ category.title }}</h4>
                    <ul>
                        <li v-for="link in category.links" :key="link.name" class="mb-2">
                            <Link :href="route(link.route)" class="text-gray-400 hover:text-white">
                                {{ link.name }}
                            </Link>
                        </li>
                    </ul>
                </div>
            </div>
            
            <div class="border-t border-gray-700 pt-6 flex flex-wrap justify-between items-center gap-4">
                <Link :href="route('home')" class="font-heading text-xl font-bold text-white">
                    CraftyXhub
                </Link>
                
                <p class="text-gray-400 text-center flex-grow">
                    © {{ currentYear }} CraftyXhub. All rights reserved.
                </p>
                
                <div class="text-gray-400">
                    <a href="#" aria-label="Facebook" class="ml-4 text-lg hover:text-white">
                        <i class="fab fa-facebook-f"></i>
                    </a>
                    <a href="#" aria-label="LinkedIn" class="ml-4 text-lg hover:text-white">
                        <i class="fab fa-linkedin-in"></i>
                    </a>
                    <a href="#" aria-label="Twitter" class="ml-4 text-lg hover:text-white">
                        <i class="fab fa-twitter"></i>
                    </a>
                </div>
            </div>
        </div>
    </footer>
</template> 