<template>
    <footer
        class="bg-gradient-to-r from-gray-900 to-gray-800 dark:from-gray-950 dark:to-gray-900 text-gray-200 dark:text-gray-300 py-16 text-sm">
        <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
                <div class="grid grid-cols-1 sm:grid-cols-4 lg:grid-cols-4 xl:grid-cols-5 gap-x-8 gap-y-12">
                    <div v-for="category in footerCategories" :key="category.title"
                        class="transition-all duration-300 ease-in-out hover:translate-y-[-6px] group">
                        <h4
                            class="text-white dark:text-gray-100 text-lg font-semibold mb-5 relative pb-3 after:content-[''] after:absolute after:bottom-0 after:left-0 after:w-12 after:h-[2px] after:bg-blue-500 after:transition-all after:duration-300 group-hover:after:w-24 group-hover:after:bg-blue-400">
                            {{ category.title }}
                        </h4>
                        <ul class="space-y-4">
                            <li v-for="link in category.links" :key="link.name">
                                <Link :href="route(link.route)"
                                    class="text-gray-400 hover:text-blue-300 dark:text-gray-500 dark:hover:text-blue-300 transition-colors duration-200 flex items-center group/link">
                                <div class="flex items-center overflow-hidden">
                                    <span
                                        class="transform translate-x-0 group-hover/link:translate-x-1 transition-transform duration-200 ease-out">
                                        {{ link.name }}
                                    </span>
                                    <svg xmlns="http://www.w3.org/2000/svg"
                                        class="h-4 w-4 ml-1 opacity-0 transform -translate-x-2 group-hover/link:opacity-100 group-hover/link:translate-x-0 transition-all duration-200 ease-out"
                                        fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                                            d="M9 5l7 7-7 7" />
                                    </svg>
                                </div>
                                </Link>
                            </li>
                        </ul>
                    </div>
                </div>
            </div>

            <div class="border-t border-gray-700 dark:border-gray-800 pt-10 pb-8">
                <div class="flex flex-col md:flex-row justify-between items-center gap-6">
                    <div class="max-w-md">
                        <h4 class="text-white dark:text-gray-100 text-lg font-bold mb-2">Join our newsletter</h4>
                        <p class="text-gray-400 dark:text-gray-500 mb-4">Get the latest updates from our team and
                            exclusive content right in your inbox.</p>
                    </div>
                    <div class="w-full md:w-auto">
                        <div class="flex flex-col sm:flex-row gap-3">
                            <input type="email" placeholder="Your email address"
                                class="bg-gray-800 dark:bg-gray-900 text-white rounded-lg px-4 py-2 w-full sm:w-64 focus:outline-none focus:ring-2 focus:ring-blue-500" />
                            <button
                                class="bg-blue-600 hover:bg-blue-700 text-white font-medium py-2 px-6 rounded-lg transition-colors duration-200">
                                Subscribe
                            </button>
                        </div>
                    </div>
                </div>
            </div>

            <div
                class="border-t border-gray-700 dark:border-gray-800 pt-8 flex flex-col md:flex-row justify-between items-center gap-6">
                <div class="flex items-center">
                    <Link :href="route('home')"
                        class="font-heading text-xl font-bold text-white dark:text-gray-100 flex items-center">
                    CraftyXhub
                    </Link>
                </div>

                <p class="text-gray-400 dark:text-gray-500 text-center">
                    © {{ currentYear }} CraftyXhub. All rights reserved.
                </p>

                <div class="flex items-center space-x-4">
                    <a href="#" aria-label="Facebook"
                        class="text-gray-400 hover:text-blue-300 dark:text-gray-500 dark:hover:text-blue-300 transition-colors duration-200">
                        <svg class="h-6 w-6" fill="currentColor" viewBox="0 0 24 24" aria-hidden="true">
                            <path fill-rule="evenodd"
                                d="M22 12c0-5.523-4.477-10-10-10S2 6.477 2 12c0 4.991 3.657 9.128 8.438 9.878v-6.987h-2.54V12h2.54V9.797c0-2.506 1.492-3.89 3.777-3.89 1.094 0 2.238.195 2.238.195v2.46h-1.26c-1.243 0-1.63.771-1.63 1.562V12h2.773l-.443 2.89h-2.33v6.988C18.343 21.128 22 16.991 22 12z"
                                clip-rule="evenodd"></path>
                        </svg>
                    </a>
                    <a href="#" aria-label="Twitter"
                        class="text-gray-400 hover:text-blue-300 dark:text-gray-500 dark:hover:text-blue-300 transition-colors duration-200">
                        <svg class="h-6 w-6" fill="currentColor" viewBox="0 0 24 24" aria-hidden="true">
                            <path
                                d="M8.29 20.251c7.547 0 11.675-6.253 11.675-11.675 0-.178 0-.355-.012-.53A8.348 8.348 0 0022 5.92a8.19 8.19 0 01-2.357.646 4.118 4.118 0 001.804-2.27 8.224 8.224 0 01-2.605.996 4.107 4.107 0 00-6.993 3.743 11.65 11.65 0 01-8.457-4.287 4.106 4.106 0 001.27 5.477A4.072 4.072 0 012.8 9.713v.052a4.105 4.105 0 003.292 4.022 4.095 4.095 0 01-1.853.07 4.108 4.108 0 003.834 2.85A8.233 8.233 0 012 18.407a11.616 11.616 0 006.29 1.84">
                            </path>
                        </svg>
                    </a>
                    <a href="#" aria-label="Instagram"
                        class="text-gray-400 hover:text-blue-300 dark:text-gray-500 dark:hover:text-blue-300 transition-colors duration-200">
                        <svg class="h-6 w-6" fill="currentColor" viewBox="0 0 24 24" aria-hidden="true">
                            <path fill-rule="evenodd"
                                d="M12.315 2c2.43 0 2.784.013 3.808.06 1.064.049 1.791.218 2.427.465a4.902 4.902 0 011.772 1.153 4.902 4.902 0 011.153 1.772c.247.636.416 1.363.465 2.427.048 1.067.06 1.407.06 4.123v.08c0 2.643-.012 2.987-.06 4.043-.049 1.064-.218 1.791-.465 2.427a4.902 4.902 0 01-1.153 1.772 4.902 4.902 0 01-1.772 1.153c-.636.247-1.363.416-2.427.465-1.067.048-1.407.06-4.123.06h-.08c-2.643 0-2.987-.012-4.043-.06-1.064-.049-1.791-.218-2.427-.465a4.902 4.902 0 01-1.772-1.153 4.902 4.902 0 01-1.153-1.772c-.247-.636-.416-1.363-.465-2.427-.047-1.024-.06-1.379-.06-3.808v-.63c0-2.43.013-2.784.06-3.808.049-1.064.218-1.791.465-2.427a4.902 4.902 0 011.153-1.772A4.902 4.902 0 015.45 2.525c.636-.247 1.363-.416 2.427-.465C8.901 2.013 9.256 2 11.685 2h.63zm-.081 1.802h-.468c-2.456 0-2.784.011-3.807.058-.975.045-1.504.207-1.857.344-.467.182-.8.398-1.15.748-.35.35-.566.683-.748 1.15-.137.353-.3.882-.344 1.857-.047 1.023-.058 1.351-.058 3.807v.468c0 2.456.011 2.784.058 3.807.045.975.207 1.504.344 1.857.182.466.399.8.748 1.15.35.35.683.566 1.15.748.353.137.882.3 1.857.344 1.054.048 1.37.058 4.041.058h.08c2.597 0 2.917-.01 3.96-.058.976-.045 1.505-.207 1.858-.344.466-.182.8-.398 1.15-.748.35-.35.566-.683.748-1.15.137-.353.3-.882.344-1.857.048-1.055.058-1.37.058-4.041v-.08c0-2.597-.01-2.917-.058-3.96-.045-.976-.207-1.505-.344-1.858a3.097 3.097 0 00-.748-1.15 3.098 3.098 0 00-1.15-.748c-.353-.137-.882-.3-1.857-.344-1.023-.047-1.351-.058-3.807-.058zM12 6.865a5.135 5.135 0 110 10.27 5.135 5.135 0 010-10.27zm0 1.802a3.333 3.333 0 100 6.666 3.333 3.333 0 000-6.666zm5.338-3.205a1.2 1.2 0 110 2.4 1.2 1.2 0 010-2.4z"
                                clip-rule="evenodd"></path>
                        </svg> </a>
                    <a href="#" aria-label="YouTube"
                        class="text-gray-400 hover:text-blue-300 dark:text-gray-500 dark:hover:text-blue-300 transition-colors duration-200">
                        <svg class="h-6 w-6" fill="currentColor" viewBox="0 0 24 24" aria-hidden="true">
                            <path fill-rule="evenodd"
                                d="M19.812 5.418c.861.23 1.538.907 1.768 1.768C21.998 8.746 22 12 22 12s0 3.255-.418 4.814a2.504 2.504 0 0 1-1.768 1.768c-1.56.419-7.814.419-7.814.419s-6.255 0-7.814-.419a2.505 2.505 0 0 1-1.768-1.768C2 15.255 2 12 2 12s0-3.255.417-4.814a2.507 2.507 0 0 1 1.768-1.768C5.744 5 11.998 5 11.998 5s6.255 0 7.814.418ZM15.194 12 10 15V9l5.194 3Z"
                                clip-rule="evenodd"></path>
                        </svg>
                    </a>
                </div>
            </div>
        </div>
    </footer>
</template>

<script setup>
import { Link } from '@inertiajs/vue3';

const footerCategories = [
    {
        title: 'TECHNOLOGY',
        links: [
            { name: 'Web Dev', route: 'technology' },
            { name: 'AI', route: 'technology' },
            { name: 'Hardware', route: 'technology' }
        ]
    },
    {
        title: 'FINANCE',
        links: [
            { name: 'Investing', route: 'finance' },
            { name: 'Budgeting', route: 'finance' },
            { name: 'Personal Finance', route: 'finance' }
        ]
    },
    {
        title: 'HEALTH',
        links: [
            { name: 'Fitness', route: 'health' },
            { name: 'Nutrition', route: 'health' },
            { name: 'Wellness', route: 'health' }
        ]
    },
    {
        title: 'EDUCATION',
        links: [
            { name: 'Courses', route: 'education' },
            { name: 'Tutorials', route: 'education' },
            { name: 'Learning Resources', route: 'education' }
        ]
    },
    {
        title: 'SPORTS',
        links: [
            { name: 'Football', route: 'sports' },
            { name: 'Basketball', route: 'sports' },
            { name: 'Highlights', route: 'sports' }
        ]
    },
    {
        title: 'SPORTS',
        links: [
            { name: 'Football', route: 'sports' },
            { name: 'Basketball', route: 'sports' },
            { name: 'Highlights', route: 'sports' }
        ]
    },
    
    {
        title: 'TRAVEL',
        links: [
            { name: 'Destinations', route: 'travel' },
            { name: 'Travel Tips', route: 'travel' },
            { name: 'Budget Travel', route: 'travel' }
        ]
    },
    {
        title: 'LIFESTYLE',
        links: [
            { name: 'Fashion', route: 'lifestyle' },
            { name: 'Food', route: 'lifestyle' },
            { name: 'Hobbies', route: 'lifestyle' }
        ]
    },
    {
        title: 'COMMUNITY',
        links: [
            { name: 'Forums', route: 'community' },
            { name: 'Events', route: 'community' },
            { name: 'User Stories', route: 'community' }
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