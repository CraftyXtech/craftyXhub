<script setup>
import { Link } from '@inertiajs/vue3';

// Updated footer categories to match main navigation
const footerCategories = [
    {
        title: 'TECHNOLOGY',
        links: [
            { name: 'Web Dev', route: 'technology' }, 
            { name: 'AI', route: 'technology' },
            { name: 'Hardware', route: 'technology' }
            // Add more specific tech links if needed
        ]
    },
    {
        title: 'FINANCE',
        links: [
            { name: 'Investing', route: 'finance' },
            { name: 'Budgeting', route: 'finance' },
            { name: 'Personal Finance', route: 'finance' } 
            // Add more specific finance links if needed
        ]
    },
    {
        title: 'HEALTH',
        links: [
            { name: 'Fitness', route: 'health' },
            { name: 'Nutrition', route: 'health' },
            { name: 'Wellness', route: 'health' }
            // Add more specific health links if needed
        ]
    },
    {
        title: 'EDUCATION',
        links: [
            { name: 'Courses', route: 'education' },
            { name: 'Tutorials', route: 'education' },
            { name: 'Learning Resources', route: 'education' }
            // Add more specific education links if needed
        ]
    },
    {
        title: 'SPORTS',
        links: [
            { name: 'Football', route: 'sports' },
            { name: 'Basketball', route: 'sports' },
            { name: 'Highlights', route: 'sports' }
             // Add more specific sports links if needed
        ]
    },
    {
        title: 'TRAVEL',
        links: [
            { name: 'Destinations', route: 'travel' },
            { name: 'Travel Tips', route: 'travel' },
            { name: 'Budget Travel', route: 'travel' }
            // Add more specific travel links if needed
        ]
    },
    {
        title: 'LIFESTYLE',
        links: [
            { name: 'Fashion', route: 'lifestyle' },
            { name: 'Food', route: 'lifestyle' },
            { name: 'Hobbies', route: 'lifestyle' }
            // Add more specific lifestyle links if needed
        ]
    },
    {
        title: 'COMMUNITY',
        links: [
            { name: 'Forums', route: 'community' },
            { name: 'Events', route: 'community' },
            { name: 'User Stories', route: 'community' } 
             // Add more specific community links if needed
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
    <footer class="bg-gray-900 text-gray-200 dark:bg-gray-950 dark:text-gray-300 py-12 text-sm">
        <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div class="flex justify-between gap-4 mb-12 overflow-x-auto pb-4">
                <div 
                    v-for="category in footerCategories" 
                    :key="category.title" 
                    class=""  
                >
                    <h4 class="text-white dark:text-gray-100 text-base font-semibold mb-4 whitespace-nowrap">{{ category.title }}</h4>
                    <ul>
                        <li v-for="link in category.links" :key="link.name" class="mb-2">
                            <Link :href="route(link.route)" class="text-gray-400 hover:text-white dark:text-gray-500 dark:hover:text-gray-100 whitespace-nowrap">
                                {{ link.name }}
                            </Link>
                        </li>
                    </ul>
                </div>
            </div>
            
            <div class="border-t border-gray-700 dark:border-gray-800 pt-6 flex flex-wrap justify-between items-center gap-4">
                <Link :href="route('home')" class="font-heading text-xl font-bold text-white dark:text-gray-100">
                    CraftyXhub
                </Link>
                
                <p class="text-gray-400 dark:text-gray-500 text-center flex-grow">
                    © {{ currentYear }} CraftyXhub. All rights reserved.
                </p>
                
                <div class="text-gray-400 dark:text-gray-500">
                    <a href="#" aria-label="Facebook" class="ml-4 text-lg hover:text-white dark:hover:text-gray-100">
                        <i class="fab fa-facebook-f"></i>
                    </a>
                    <a href="#" aria-label="LinkedIn" class="ml-4 text-lg hover:text-white dark:hover:text-gray-100">
                        <i class="fab fa-linkedin-in"></i>
                    </a>
                    <a href="#" aria-label="Twitter" class="ml-4 text-lg hover:text-white dark:hover:text-gray-100">
                        <i class="fab fa-twitter"></i>
                    </a>
                </div>
            </div>
        </div>
    </footer>
</template> 