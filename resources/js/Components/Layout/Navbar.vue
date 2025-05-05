<template>
    <header
    style="font-family: 'Gill Sans', 'Gill Sans MT', Calibri, 'Trebuchet MS', sans-serif;"    
    class="bg-white dark:bg-gray-900 py-4 border-b border-gray-200 dark:border-gray-700 text-gray-800 dark:text-gray-200">
        <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div class="flex items-center justify-between">
                <!-- Left navigation -->
                <nav class="flex-1 hidden md:flex items-center justify-start space-x-8">
                    <!-- Left Links -->
                    <template v-for="item in navItemsLeft" :key="item.name">
                        <Dropdown v-if="item.dropdown" align="left" width="48">
                            <template #trigger>
                                <button
                                    class="inline-flex items-center px-1 pt-1 border-b-2 border-transparent text-sm font-medium leading-7 text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300 dark:hover:border-gray-600 dark:focus:text-gray-300 dark:focus:border-gray-600 transition duration-150 ease-in-out">
                                    {{ item.name }}
                                    <svg class="ms-2 -me-0.5 h-4 w-4" xmlns="http://www.w3.org/2000/svg"
                                        viewBox="0 0 20 20" fill="currentColor">
                                        <path fill-rule="evenodd"
                                            d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z"
                                            clip-rule="evenodd" />
                                    </svg>
                                </button>
                            </template>
                            <template #content>
                                <div
                                    class="bg-white dark:bg-gray-800 rounded-md shadow-lg ring-1 ring-black ring-opacity-5 py-1">
                                    <DropdownLink v-for="subItem in item.dropdown" :key="subItem"
                                        :href="route('category', { category: subItem.toLowerCase().replace(' ', '-') })">
                                        {{ subItem }}
                                    </DropdownLink>
                                </div>
                            </template>
                        </Dropdown>
                        <NavLink v-else
                            :href="route('category', { category: item.name.toLowerCase().replace(' ', '-') })">
                            {{ item.name }}
                        </NavLink>
                    </template>
                </nav>

                <!-- Center Logo -->
                <div
                    class="hidden sm:flex flex-shrink-0 items-center justify-center mx-auto absolute left-1/2 transform -translate-x-1/2">
                    <Link :href="route('home')" class="flex items-center">
                    <span class="text-lg font-semibold">CraftyXhub</span>
                    </Link>
                </div>


                <!-- Right navigation & Auth Items -->
                <nav class="flex-1 hidden md:flex items-center justify-end space-x-8">
                    <!-- Right Links -->
                    <template v-for="item in navItemsRight" :key="item.name">
                        <Dropdown v-if="item.dropdown" align="right" width="48">
                            <template #trigger>
                                <button
                                    class="inline-flex items-center px-1 pt-1 border-b-2 border-transparent text-sm font-medium leading-7 text-gray-500 dark:text-gray-400 dark:hover:text-gray-300 hover:border-gray-300 dark:hover:border-gray-600 focus:outline-none dark:focus:text-gray-300 dark:focus:border-gray-600 transition duration-150 ease-in-out">
                                    {{ item.name }}
                                    <svg class="ms-2 -me-0.5 h-4 w-4" xmlns="http://www.w3.org/2000/svg"
                                        viewBox="0 0 20 20" fill="currentColor">
                                        <path fill-rule="evenodd"
                                            d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z"
                                            clip-rule="evenodd" />
                                    </svg>
                                </button>
                            </template>
                            <template #content>
                                <div
                                    class="bg-white dark:bg-gray-800 rounded-md shadow-lg ring-1 ring-black ring-opacity-5 py-1">
                                    <DropdownLink v-for="subItem in item.dropdown" :key="subItem"
                                        :href="route('category', { category: subItem.toLowerCase().replace(' ', '-') })">
                                        {{ subItem }}
                                    </DropdownLink>
                                </div>
                            </template>
                        </Dropdown>
                        <NavLink v-else
                            :href="route('category', { category: item.name.toLowerCase().replace(' ', '-') })">
                            {{ item.name }}
                        </NavLink>
                    </template>

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

                <!-- Mobile menu button -->
                <div class="md:hidden flex justify-between items-center w-full">
                    <button @click="mobileMenuOpen = !mobileMenuOpen" class="text-gray-800 dark:text-gray-200">
                        <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24"
                            stroke="currentColor">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                                d="M4 6h16M4 12h16M4 18h16" />
                        </svg>
                    </button>

                    <!-- Center Logo (Mobile) -->
                    <Link :href="route('home')"
                        class="font-heading text-2xl text-primary dark:text-primary-dark mx-auto">
                    CraftyXhub
                    </Link>

                    <div class="flex items-center">
                        <!-- Dark Mode Toggle Button (Mobile) -->
                        <button @click="toggleDarkMode"
                            class="p-2 rounded-full text-gray-500 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-700">
                            <svg v-if="isDarkMode" xmlns="http://www.w3.org/2000/svg" class="h-5 w-5"
                                viewBox="0 0 20 20" fill="currentColor">
                                <path
                                    d="M10 2a1 1 0 011 1v1a1 1 0 11-2 0V3a1 1 0 011-1zm4 8a4 4 0 11-8 0 4 4 0 018 0zm-.464 4.95l.707.707a1 1 0 001.414-1.414l-.707-.707a1 1 0 00-1.414 1.414zm2.12-10.607a1 1 0 010 1.414l-.706.707a1 1 0 11-1.414-1.414l.707-.707a1 1 0 011.414 0zM17 11a1 1 0 100-2h-1a1 1 0 100 2h1zm-7 4a1 1 0 011 1v1a1 1 0 11-2 0v-1a1 1 0 011-1zM5.05 14.95a1 1 0 010-1.414l.707-.707a1 1 0 011.414 1.414l-.707.707a1 1 0 01-1.414 0zm-.464-4.95a1 1 0 011.414 0l.707.707a1 1 0 11-1.414 1.414l-.707-.707a1 1 0 010-1.414zM1 11a1 1 0 100-2H0a1 1 0 100 2h1zM4.54 5.46a1 1 0 00-1.414-1.414l-.707.707a1 1 0 101.414 1.414l.707-.707z" />
                            </svg>
                            <svg v-else xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20"
                                fill="currentColor">
                                <path d="M17.293 13.293A8 8 0 016.707 2.707a8.001 8.001 0 1010.586 10.586z" />
                            </svg>
                        </button>
                    </div>
                </div>
            </div>
        </div>

        <!-- Mobile Menu (Dropdown) -->
        <div v-show="mobileMenuOpen" class="md:hidden">
            <div class="px-2 pt-2 pb-3 space-y-1 sm:px-3 bg-white dark:bg-gray-900 border-t border-gray-200 dark:border-gray-700">
                <!-- Left Navigation Items (Mobile) -->
                <div class="space-y-2 mb-4">
                    <p class="px-3 text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                        Navigation
                    </p>
                    <template v-for="item in navItemsLeft" :key="item.name">
                        <div v-if="item.dropdown" class="space-y-1">
                            <button @click="toggleMobileDropdown(item.name)" 
                                class="w-full flex justify-between items-center px-3 py-2 rounded-md text-base font-medium text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-800">
                                {{ item.name }}
                                <svg class="h-4 w-4" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
                                    <path fill-rule="evenodd" d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z" clip-rule="evenodd" />
                                </svg>
                            </button>
                            <div v-show="openMobileDropdowns[item.name]" class="pl-4 space-y-1">
                                <Link v-for="subItem in item.dropdown" :key="subItem"
                                    :href="route('category', { category: subItem.toLowerCase().replace(' ', '-') })"
                                    class="block px-3 py-2 rounded-md text-base font-medium text-gray-600 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-800">
                                    {{ subItem }}
                                </Link>
                            </div>
                        </div>
                        <Link v-else
                            :href="route('category', { category: item.name.toLowerCase().replace(' ', '-') })"
                            class="block px-3 py-2 rounded-md text-base font-medium text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-800">
                            {{ item.name }}
                        </Link>
                    </template>
                </div>
                
                <!-- Right Navigation Items (Mobile) -->
                <div class="space-y-2">
                    <p class="px-3 text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                        Other
                    </p>
                    <template v-for="item in navItemsRight" :key="item.name">
                        <div v-if="item.dropdown" class="space-y-1">
                            <button @click="toggleMobileDropdown(item.name)" 
                                class="w-full flex justify-between items-center px-3 py-2 rounded-md text-base font-medium text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-800">
                                {{ item.name }}
                                <svg class="h-4 w-4" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
                                    <path fill-rule="evenodd" d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z" clip-rule="evenodd" />
                                </svg>
                            </button>
                            <div v-show="openMobileDropdowns[item.name]" class="pl-4 space-y-1">
                                <Link v-for="subItem in item.dropdown" :key="subItem"
                                    :href="route('category', { category: subItem.toLowerCase().replace(' ', '-') })"
                                    class="block px-3 py-2 rounded-md text-base font-medium text-gray-600 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-800">
                                    {{ subItem }}
                                </Link>
                            </div>
                        </div>
                        <Link v-else
                            :href="route('category', { category: item.name.toLowerCase().replace(' ', '-') })"
                            class="block px-3 py-2 rounded-md text-base font-medium text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-800">
                            {{ item.name }}
                        </Link>
                    </template>
                </div>
            </div>
        </div>
    </header>
</template>

<script setup>
import { Link, usePage } from '@inertiajs/vue3';
import { ref, onMounted, computed, reactive } from 'vue';
import { navItemsLeft, navItemsRight, getAuthItems } from '@/Shared/navigationItems';
import Dropdown from '@/Components/Dropdown.vue';
import DropdownLink from '@/Components/DropdownLink.vue';
import NavLink from '@/Components/NavLink.vue';

const isDarkMode = ref(false);

const mobileMenuOpen = ref(false);
const openMobileDropdowns = reactive({});

const toggleMobileDropdown = (itemName) => {
    openMobileDropdowns[itemName] = !openMobileDropdowns[itemName];
};

const authItems = computed(() => getAuthItems());

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