<template>
    <Head title="Welcome to CraftyXhub" />
    <div class="min-h-screen bg-gradient-to-br from-indigo-900 to-purple-800 text-white">
        <!-- Hero Section -->
        <div class="relative flex min-h-screen flex-col items-center justify-center px-4 py-16 sm:px-6 lg:px-8">
            <!-- Header/Nav -->
            <nav class="absolute top-0 w-full p-6 flex justify-between items-center">
                <div class="flex items-center space-x-2">
                    <div class="w-10 h-10 bg-white rounded-full flex items-center justify-center">
                        <span class="text-indigo-900 font-bold text-xl">CX</span>
                    </div>
                    <span class="text-2xl font-bold">CraftyXhub</span>
                </div>
                
                <div v-if="canLogin" class="flex items-center space-x-4">
                    <Link v-if="$page.props.auth.user" :href="route('dashboard')" 
                        class="px-4 py-2 rounded-md bg-white text-indigo-800 hover:bg-indigo-100 transition font-medium">
                        Dashboard
                    </Link>
                    <template v-else>
                        <Link :href="route('login')" 
                            class="px-4 py-2 rounded-md border-2 border-white text-white hover:bg-white hover:text-indigo-900 transition font-medium">
                            Log in
                        </Link>
                        <Link v-if="canRegister" :href="route('register')" 
                            class="px-4 py-2 rounded-md bg-white text-indigo-800 hover:bg-indigo-100 transition font-medium">
                            Get Started
                        </Link>
                    </template>
                </div>
                    </nav>

            <!-- Main Content -->
            <div class="text-center max-w-5xl mx-auto">
                <h1 class="text-5xl md:text-7xl font-extrabold mb-6">
                    Welcome to <span class="text-transparent bg-clip-text bg-gradient-to-r from-pink-400 to-yellow-400">CraftyXhub</span>
                </h1>
                <p class="text-xl md:text-2xl mb-12 text-indigo-200 max-w-3xl mx-auto">
                    Your one-stop platform for creative artisans to showcase, sell, and connect.
                </p>
                
                <div class="flex flex-col sm:flex-row justify-center gap-4 mb-16">
                    <button class="px-8 py-4 rounded-md bg-white text-indigo-900 font-bold text-lg hover:bg-indigo-100 transition">
                        Explore Marketplace
                    </button>
                    <button class="px-8 py-4 rounded-md border-2 border-white text-white font-bold text-lg hover:bg-white hover:text-indigo-900 transition">
                        Join Our Community
                    </button>
                                    </div>

                <!-- Features Section -->
                <div class="grid grid-cols-1 md:grid-cols-3 gap-8 mt-12">
                    <div class="bg-white/10 backdrop-blur-sm p-6 rounded-xl">
                        <div class="w-16 h-16 bg-gradient-to-br from-pink-500 to-orange-400 rounded-lg flex items-center justify-center mx-auto mb-4">
                            <svg xmlns="http://www.w3.org/2000/svg" class="h-8 w-8 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
                                </svg>
                            </div>
                        <h3 class="text-xl font-bold mb-2">Sell Instantly</h3>
                        <p class="text-indigo-200">Set up your shop and start selling your crafts in minutes with our easy-to-use platform.</p>
                            </div>

                    <div class="bg-white/10 backdrop-blur-sm p-6 rounded-xl">
                        <div class="w-16 h-16 bg-gradient-to-br from-blue-500 to-teal-400 rounded-lg flex items-center justify-center mx-auto mb-4">
                            <svg xmlns="http://www.w3.org/2000/svg" class="h-8 w-8 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
                                </svg>
                            </div>
                        <h3 class="text-xl font-bold mb-2">Connect with Artisans</h3>
                        <p class="text-indigo-200">Join a vibrant community of creators and build your network with like-minded artisans.</p>
                            </div>

                    <div class="bg-white/10 backdrop-blur-sm p-6 rounded-xl">
                        <div class="w-16 h-16 bg-gradient-to-br from-purple-500 to-pink-400 rounded-lg flex items-center justify-center mx-auto mb-4">
                            <svg xmlns="http://www.w3.org/2000/svg" class="h-8 w-8 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
                            </svg>
                        </div>
                        <h3 class="text-xl font-bold mb-2">Manage Your Business</h3>
                        <p class="text-indigo-200">Access powerful tools to track sales, manage inventory, and grow your craft business.</p>
                    </div>
                </div>
            </div>
            
            <!-- Footer -->
            <footer class="absolute bottom-4 text-center w-full text-indigo-300 text-sm">
                <p>CraftyXhub | Laravel v{{ laravelVersion }} (PHP v{{ phpVersion }})</p>
                <p class="mt-1">© {{ new Date().getFullYear() }} CraftyXhub. All rights reserved.</p>
            </footer>
        </div>
    </div>
</template>

<script setup>
import { Head, Link } from '@inertiajs/vue3';

defineProps({
    canLogin: {
        type: Boolean,
    },
    canRegister: {
        type: Boolean,
    },
    laravelVersion: {
        type: String,
        required: true,
    },
    phpVersion: {
        type: String,
        required: true,
    },
});

function handleImageError() {
    document.getElementById('screenshot-container')?.classList.add('!hidden');
    document.getElementById('docs-card')?.classList.add('!row-span-1');
    document.getElementById('docs-card-content')?.classList.add('!flex-row');
    document.getElementById('background')?.classList.add('!hidden');
}
</script>

