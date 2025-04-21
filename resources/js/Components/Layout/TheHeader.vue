<script setup>
import { Link, usePage } from '@inertiajs/vue3';
import { ref, onMounted, computed } from 'vue'; // Import ref, onMounted, and computed
// Import shared items and necessary components
import { navItemsLeft, navItemsRight, getAuthItems } from '@/Shared/navigationItems'; // Import getAuthItems
import Dropdown from '@/Components/Dropdown.vue';
import DropdownLink from '@/Components/DropdownLink.vue';
import NavLink from '@/Components/NavLink.vue';
import ApplicationLogo from '@/Components/ApplicationLogo.vue'; // Added missing import for logo

// Dark Mode Logic
const isDarkMode = ref(false);

// Compute auth items
const authItems = computed(() => getAuthItems()); // Get auth items dynamically

const toggleDarkMode = () => {
    isDarkMode.value = !isDarkMode.value;
    if (isDarkMode.value) {
        document.documentElement.classList.add('dark');
        localStorage.setItem('theme', 'dark');
    } else {
        document.documentElement.classList.remove('dark');
        localStorage.setItem('theme', 'light');
    }
};

onMounted(() => {
    const savedTheme = localStorage.getItem('theme');
    if (savedTheme === 'dark' || (!savedTheme && window.matchMedia('(prefers-color-scheme: dark)').matches)) {
        isDarkMode.value = true;
        document.documentElement.classList.add('dark');
    } else {
        isDarkMode.value = false;
        document.documentElement.classList.remove('dark');
    }
});
</script>

<template>
    <header class="bg-white dark:bg-gray-900 py-4 border-b border-gray-200 dark:border-gray-700 text-gray-800 dark:text-gray-200">
        <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div class="flex items-center">
                <!-- Left navigation -->
                <nav class="flex-1 hidden md:flex items-center justify-start space-x-8">
                    <!-- Logo (Moved to left for consistency with AuthenticatedLayout) -->
                     <div class="shrink-0 flex items-center">
                        <Link :href="route('home')">
                            <ApplicationLogo class="block h-9 w-auto" />
                             <!-- Optional: If logo doesn't contain text -->
                             <span class="ml-2 text-lg font-semibold">CraftyXhub</span>
                        </Link>
                    </div>
                    <!-- Left Links -->
                    <template v-for="item in navItemsLeft" :key="item.name">
                        <Dropdown v-if="item.dropdown" align="left" width="48">
                            <template #trigger>
                                <button class="inline-flex items-center px-1 pt-1 border-b-2 border-transparent text-sm font-medium leading-5 text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300 hover:border-gray-300 dark:hover:border-gray-600 focus:outline-none focus:text-gray-700 dark:focus:text-gray-300 focus:border-gray-300 dark:focus:border-gray-600 transition duration-150 ease-in-out">
                                    {{ item.name }}
                                    <svg class="ms-2 -me-0.5 h-4 w-4" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
                                        <path fill-rule="evenodd" d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z" clip-rule="evenodd" />
                                    </svg>
                                </button>
                            </template>
                            <template #content>
                                <div class="bg-white dark:bg-gray-800 rounded-md shadow-lg ring-1 ring-black ring-opacity-5 py-1">
                                    <DropdownLink v-for="subItem in item.dropdown" :key="subItem" :href="route('category', { category: subItem.toLowerCase().replace(' ', '-') })">
                                        {{ subItem }}
                                    </DropdownLink>
                                </div>
                            </template>
                        </Dropdown>
                         <NavLink v-else :href="route('category', { category: item.name.toLowerCase().replace(' ', '-') })">
                            {{ item.name }}
                        </NavLink>
                    </template>
                </nav>

                <!-- Right navigation & Auth Items -->
                 <nav class="flex-1 hidden md:flex items-center justify-end space-x-8">
                     <!-- Right Links -->
                    <template v-for="item in navItemsRight" :key="item.name">
                         <Dropdown v-if="item.dropdown" align="right" width="48">
                             <template #trigger>
                                <button class="inline-flex items-center px-1 pt-1 border-b-2 border-transparent text-sm font-medium leading-5 text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300 hover:border-gray-300 dark:hover:border-gray-600 focus:outline-none focus:text-gray-700 dark:focus:text-gray-300 focus:border-gray-300 dark:focus:border-gray-600 transition duration-150 ease-in-out">
                                    {{ item.name }}
                                    <svg class="ms-2 -me-0.5 h-4 w-4" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
                                        <path fill-rule="evenodd" d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z" clip-rule="evenodd" />
                                    </svg>
                                </button>
                            </template>
                             <template #content>
                                <div class="bg-white dark:bg-gray-800 rounded-md shadow-lg ring-1 ring-black ring-opacity-5 py-1">
                                    <DropdownLink v-for="subItem in item.dropdown" :key="subItem" :href="route('category', { category: subItem.toLowerCase().replace(' ', '-') })">
                                        {{ subItem }}
                                    </DropdownLink>
                                </div>
                            </template>
                        </Dropdown>
                         <NavLink v-else :href="route('category', { category: item.name.toLowerCase().replace(' ', '-') })">
                            {{ item.name }}
                        </NavLink>
                    </template>

                    <!-- ****** NEW AUTH ITEMS SECTION ****** -->
                    <div class="flex items-center ml-6 space-x-4">
                        <template v-for="item in authItems" :key="item.name">
                            <Dropdown v-if="item.dropdown && usePage().props.auth.user" align="right" width="48">
                                <template #trigger>
                                     <span class="inline-flex rounded-md">
                                        <button type="button" class="inline-flex items-center px-3 py-2 border border-transparent text-sm leading-4 font-medium rounded-md text-gray-500 dark:text-gray-400 bg-white dark:bg-gray-800 hover:text-gray-700 dark:hover:text-gray-300 focus:outline-none transition ease-in-out duration-150">
                                            {{ usePage().props.auth.user.name }}
                                            <svg class="ms-2 -me-0.5 h-4 w-4" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
                                                <path fill-rule="evenodd" d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z" clip-rule="evenodd" />
                                            </svg>
                                        </button>
                                     </span>
                                </template>
                                <template #content>
                                    <div class="bg-white dark:bg-gray-800 rounded-md shadow-lg ring-1 ring-black ring-opacity-5 py-1">
                                        <DropdownLink :href="route('profile.view')"> Profile </DropdownLink>
                                        <!-- Add Settings Link if needed -->
                                        <!-- <DropdownLink :href="route('profile.edit')"> Settings </DropdownLink> -->
                                         <DropdownLink :href="route('logout')" method="post" as="button"> Log Out </DropdownLink>
                                     </div>
                                </template>
                            </Dropdown>
                             <Link v-else-if="!usePage().props.auth.user"
                                :href="item.href"
                                :class="[
                                    item.highlight
                                        ? 'bg-primary hover:bg-primary-dark text-white'
                                        : 'text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300 border-2 border-transparent hover:border-gray-300 dark:hover:border-gray-600',
                                    'px-4 py-2 rounded-md text-sm font-medium transition duration-150 ease-in-out'
                                ]"
                            >
                                {{ item.name }}
                            </Link>
                        </template>
                    </div>
                     <!-- ****** END AUTH ITEMS SECTION ****** -->

                    <!-- Dark Mode Toggle Button -->
                    <button @click="toggleDarkMode" class="ml-4 p-2 rounded-full text-gray-500 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary dark:focus:ring-offset-gray-800">
                        <svg v-if="isDarkMode" xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                            <path d="M10 2a1 1 0 011 1v1a1 1 0 11-2 0V3a1 1 0 011-1zm4 8a4 4 0 11-8 0 4 4 0 018 0zm-.464 4.95l.707.707a1 1 0 001.414-1.414l-.707-.707a1 1 0 00-1.414 1.414zm2.12-10.607a1 1 0 010 1.414l-.706.707a1 1 0 11-1.414-1.414l.707-.707a1 1 0 011.414 0zM17 11a1 1 0 100-2h-1a1 1 0 100 2h1zm-7 4a1 1 0 011 1v1a1 1 0 11-2 0v-1a1 1 0 011-1zM5.05 14.95a1 1 0 010-1.414l.707-.707a1 1 0 011.414 1.414l-.707.707a1 1 0 01-1.414 0zm-.464-4.95a1 1 0 011.414 0l.707.707a1 1 0 11-1.414 1.414l-.707-.707a1 1 0 010-1.414zM1 11a1 1 0 100-2H0a1 1 0 100 2h1zM4.54 5.46a1 1 0 00-1.414-1.414l-.707.707a1 1 0 101.414 1.414l.707-.707z" />
                        </svg>
                        <svg v-else xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                            <path d="M17.293 13.293A8 8 0 016.707 2.707a8.001 8.001 0 1010.586 10.586z" />
                        </svg>
                    </button>
                </nav>
                
                <!-- Mobile menu button (remains unchanged for now) -->
                <div class="md:hidden flex justify-between items-center w-full">
                    <Link :href="route('home')" class="font-heading text-2xl text-primary dark:text-primary-dark">
                        CraftyXhub
                    </Link>
                    <div class="flex items-center">
                         <!-- Dark Mode Toggle Button (Mobile) -->
                         <button @click="toggleDarkMode" class="mr-2 p-2 rounded-full text-gray-500 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-700 focus:outline-none">
                            <svg v-if="isDarkMode" xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                                <path d="M10 2a1 1 0 011 1v1a1 1 0 11-2 0V3a1 1 0 011-1zm4 8a4 4 0 11-8 0 4 4 0 018 0zm-.464 4.95l.707.707a1 1 0 001.414-1.414l-.707-.707a1 1 0 00-1.414 1.414zm2.12-10.607a1 1 0 010 1.414l-.706.707a1 1 0 11-1.414-1.414l.707-.707a1 1 0 011.414 0zM17 11a1 1 0 100-2h-1a1 1 0 100 2h1zm-7 4a1 1 0 011 1v1a1 1 0 11-2 0v-1a1 1 0 011-1zM5.05 14.95a1 1 0 010-1.414l.707-.707a1 1 0 011.414 1.414l-.707.707a1 1 0 01-1.414 0zm-.464-4.95a1 1 0 011.414 0l.707.707a1 1 0 11-1.414 1.414l-.707-.707a1 1 0 010-1.414zM1 11a1 1 0 100-2H0a1 1 0 100 2h1zM4.54 5.46a1 1 0 00-1.414-1.414l-.707.707a1 1 0 101.414 1.414l.707-.707z" />
                            </svg>
                            <svg v-else xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                                <path d="M17.293 13.293A8 8 0 016.707 2.707a8.001 8.001 0 1010.586 10.586z" />
                            </svg>
                         </button>
                        <button class="text-gray-800 dark:text-gray-200">
                            <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16" />
                            </svg>
                        </button>
                    </div>
                </div>
            </div>
        </div>
    </header>
</template> 