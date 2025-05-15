<template>
    <header
        class="bg-white dark:bg-gray-900 border-b border-gray-200 dark:border-gray-700 text-gray-800 dark:text-gray-200 sticky top-0 z-50 transition-colors duration-300"
        :style="{ fontFamily: 'Inter, -apple-system, BlinkMacSystemFont, Segoe UI, Roboto, sans-serif' }"
    >
        <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div class="flex items-center justify-between h-16">
                
                <!-- Left Navigation Block -->
                <nav class="hidden md:flex items-center space-x-6">
                    <template v-for="item in generalNavItems" :key="item.name">
                        <NavLink 
                            :href="route(item.routeName)" 
                            :active="item.current ? item.current() : false"
                            class="hover:text-primary-600 dark:hover:text-primary-400 transition-colors duration-200"
                        >
                            {{ item.name }}
                        </NavLink>
                    </template>

                    <!-- Dashboard Link for Admin/Editor -->
                    <template v-if="isAdmin || isEditor">
                        <NavLink 
                            v-if="showPublicDashboardLink"
                            :href="route('admin.dashboard')" 
                            :active="currentRouteIsAdminArea && (page.props.ziggy?.route_name === 'admin.dashboard' || page.props.ziggy?.route_name?.startsWith('admin.dashboard.'))"
                            class="text-sm font-medium hover:text-primary-600 dark:hover:text-primary-400 transition-colors duration-200"
                        >
                            Dashboard
                        </NavLink>
                    </template>
                    
                    <!-- Public Category Navigation -->
                    <template v-if="!currentRouteIsAdminArea">
                        <template v-for="item in navItemsLeft" :key="item.name + '-public-left'">
                            <Dropdown align="left" width="48">
                                <template #trigger>
                                    <button class="group inline-flex items-center px-1 pt-1 border-b-2 border-transparent text-sm font-medium leading-5 text-gray-600 dark:text-gray-300 hover:text-gray-900 dark:hover:text-gray-100 focus:outline-none transition-colors duration-200">
                                        {{ item.name }}
                                        <svg class="ms-1 -me-0.5 h-4 w-4 text-gray-500 dark:text-gray-400 group-hover:text-gray-700 dark:group-hover:text-gray-200 transition-transform duration-200" fill="currentColor" viewBox="0 0 20 20">
                                            <path fill-rule="evenodd" d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z" clip-rule="evenodd" />
                                        </svg>
                                    </button>
                                </template>
                                <template #content>
                                    <div class="py-1">
                                        <DropdownLink 
                                            v-for="subItemName in item.dropdown" 
                                            :key="subItemName" 
                                            :href="route('category', { category: subItemName.toLowerCase().replace(/\s+/g, '-') })"
                                            class="hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors duration-150"
                                        >
                                            {{ subItemName }}
                                        </DropdownLink>
                                    </div>
                                </template>
                            </Dropdown>
                        </template>
                    </template>
                </nav>

                <!-- Centered Logo -->
                <div class="flex flex-grow justify-center md:justify-center">
                    <Link 
                        :href="route('home')" 
                        class="flex items-center font-semibold text-gray-600 transition-colors duration-200"
                    >
                        <span class="">
                            Crafty Articles
                        </span>
                    </Link>
                </div>

                <div class="hidden md:flex items-center space-x-4">
                    <template v-if="!currentRouteIsAdminArea">
                        <template v-for="item in navItemsRight" :key="item.name + '-public-right'">
                            <Dropdown align="right" width="48">
                                <template #trigger>
                                    <button class="group inline-flex items-center px-1 pt-1 border-b-2 border-transparent text-sm font-medium leading-5 text-gray-600 dark:text-gray-300 hover:text-gray-900 dark:hover:text-gray-100 focus:outline-none transition-colors duration-200">
                                        {{ item.name }}
                                        <svg class="ms-1 -me-0.5 h-4 w-4 text-gray-500 dark:text-gray-400 group-hover:text-gray-700 dark:group-hover:text-gray-200 transition-transform duration-200" fill="currentColor" viewBox="0 0 20 20">
                                            <path fill-rule="evenodd" d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z" clip-rule="evenodd" />
                                        </svg>
                                    </button>
                                </template>
                                <template #content>
                                    <div class="py-1">
                                        <DropdownLink 
                                            v-for="subItemName in item.dropdown" 
                                            :key="subItemName" 
                                            :href="route('category', { category: subItemName.toLowerCase().replace(/\s+/g, '-') })"
                                            class="hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors duration-150"
                                        >
                                            {{ subItemName }}
                                        </DropdownLink>
                                    </div>
                                </template>
                            </Dropdown>
                        </template>
                    </template>

                    <!-- Guest Navigation -->
                    <template v-if="!user">
                        <template v-for="item in guestAccountNav" :key="item.name">
                            <NavLink 
                                :href="route(item.routeName)" 
                                :class="{
                                    'px-4 py-2 rounded-md bg-gradient-to-r from-primary-500 to-blue-500 text-white shadow-md hover:shadow-lg transform hover:-translate-y-0.5 transition-all duration-200': item.highlight,
                                    'hover:text-primary-600 dark:hover:text-primary-400 transition-colors duration-200': !item.highlight
                                }"
                            >
                                {{ item.name }}
                            </NavLink>
                        </template>
                    </template>

                    <!-- Authenticated User Navigation -->
                    <template v-if="user">
                        <template v-for="item in authenticatedUserAccountNav" :key="item.name">
                            <Dropdown align="right" width="48">
                                <template #trigger>
                                    <button class="group inline-flex items-center space-x-1">
                                        <div class="h-8 w-8 rounded-full bg-gray-200 dark:bg-gray-700 flex items-center justify-center overflow-hidden">
                                            <span v-if="!user.profile_photo_path" class="text-sm font-medium text-gray-700 dark:text-gray-300">
                                                {{ user.name.charAt(0).toUpperCase() }}
                                            </span>
                                            <img v-else :src="user.profile_photo_path" :alt="user.name" class="h-full w-full object-cover">
                                        </div>
                                        <span class="text-sm font-medium text-gray-700 dark:text-gray-300 group-hover:text-primary-600 dark:group-hover:text-primary-400 transition-colors duration-200">
                                            {{ item.name }}
                                        </span>
                                    </button>
                                </template>
                                <template #content>
                                    <div class="py-1">
                                        <DropdownLink 
                                            v-for="subItem in item.dropdownItems" 
                                            :key="subItem.name" 
                                            :href="route(subItem.routeName)" 
                                            :method="subItem.method" 
                                            :as="subItem.as"
                                            class="hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors duration-150"
                                        >
                                            <div class="flex items-center space-x-2">
                                                <span v-if="subItem.icon" class="material-icons-outlined text-lg">{{ subItem.icon }}</span>
                                                <span>{{ subItem.name }}</span>
                                            </div>
                                        </DropdownLink>
                                    </div>
                                </template>
                            </Dropdown>
                        </template>
                    </template>                    
                </div>

                <div class="md:hidden flex items-center justify-end w-full">
                    <button 
                        @click="handleMobileMenuToggle" 
                        class="inline-flex items-center justify-center p-2 rounded-md text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-800 focus:outline-none transition-colors duration-200"
                        aria-label="Toggle menu"
                    >
                        <svg class="h-6 w-6" stroke="currentColor" fill="none" viewBox="0 0 24 24">
                            <path :class="{'hidden': mobileMenuOpen, 'inline-flex': !mobileMenuOpen }" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16" />
                            <path :class="{'hidden': !mobileMenuOpen, 'inline-flex': mobileMenuOpen }" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                        </svg>
                    </button>
                 
                </div>
            </div>
        </div>

        <Transition
            enter-active-class="transition ease-out duration-100"
            enter-from-class="transform opacity-0 -translate-y-2"
            enter-to-class="transform opacity-100 translate-y-0"
            leave-active-class="transition ease-in duration-75"
            leave-from-class="transform opacity-100 translate-y-0"
            leave-to-class="transform opacity-0 -translate-y-2"
        >
            <div 
                v-show="mobileMenuOpen" 
                class="md:hidden fixed inset-x-0 top-16 z-40 bg-white dark:bg-gray-900 border-t border-gray-200 dark:border-gray-700 shadow-lg max-h-[calc(100vh-4rem)] overflow-y-auto"
            >
                <div class="pt-2 pb-3 space-y-1">
                    <template v-for="item in generalNavItems" :key="item.name + '-mobile-general'">
                        <NavLink 
                            :href="route(item.routeName)" 
                            :active="item.current ? item.current() : false" 
                            mobile 
                            @click="handleMobileMenuToggle"
                            class="px-4 py-3 hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors duration-150"
                        >
                            {{ item.name }}
                        </NavLink>
                    </template>

                    <template v-if="isAdmin">
                        <div class="mt-2 pt-2 border-t border-gray-200 dark:border-gray-700">
                            <p class="px-4 text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wider mb-1">Admin Tools</p>
                            <template v-for="item in adminNavItems" :key="item.name + '-mobile-admin'">
                                <div v-if="item.isDropdown">
                                    <button 
                                        @click="toggleMobileDropdown(item.name)" 
                                        class="w-full flex justify-between items-center px-4 py-3 text-left text-base font-medium text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-800 focus:outline-none transition-colors duration-150"
                                    >
                                        <span>{{ item.name }}</span>
                                        <svg 
                                            class="h-5 w-5 transform transition-transform duration-200 text-gray-400" 
                                            :class="{'rotate-180': openMobileDropdowns[item.name]}" 
                                            fill="currentColor" 
                                            viewBox="0 0 20 20"
                                        >
                                            <path fill-rule="evenodd" d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z" clip-rule="evenodd" />
                                        </svg>
                                    </button>
                                    <div 
                                        v-show="openMobileDropdowns[item.name]" 
                                        class="pt-1 pb-1 space-y-1 pl-6 border-l-2 border-gray-200 dark:border-gray-700 ml-4"
                                    >
                                        <NavLink 
                                            v-for="subItem in item.dropdownItems" 
                                            :key="subItem.name + '-mobile-admin-sub'" 
                                            :href="route(subItem.routeName)" 
                                            mobile 
                                            @click="handleMobileMenuToggle"
                                            class="px-4 py-2 hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors duration-150"
                                        >
                                            {{ subItem.name }}
                                        </NavLink>
                                    </div>
                                </div>
                                <NavLink 
                                    v-else 
                                    :href="route(item.routeName)" 
                                    :active="item.current ? item.current() : false" 
                                    mobile 
                                    @click="handleMobileMenuToggle"
                                    class="px-4 py-3 hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors duration-150"
                                >
                                    {{ item.name }}
                                </NavLink>
                            </template>
                        </div>
                    </template>
                    <template v-else-if="isEditor">
                        <div class="mt-2 pt-2 border-t border-gray-200 dark:border-gray-700">
                            <p class="px-4 text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wider mb-1">Editor Tools</p>
                            <template v-for="item in editorNavItems" :key="item.name + '-mobile-editor'">
                                <div v-if="item.isDropdown">
                                    <button 
                                        @click="toggleMobileDropdown(item.name)" 
                                        class="w-full flex justify-between items-center px-4 py-3 text-left text-base font-medium text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-800 focus:outline-none transition-colors duration-150"
                                    >
                                        <span>{{ item.name }}</span>
                                        <svg 
                                            class="h-5 w-5 transform transition-transform duration-200 text-gray-400" 
                                            :class="{'rotate-180': openMobileDropdowns[item.name]}" 
                                            fill="currentColor" 
                                            viewBox="0 0 20 20"
                                        >
                                            <path fill-rule="evenodd" d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z" clip-rule="evenodd" />
                                        </svg>
                                    </button>
                                    <div 
                                        v-show="openMobileDropdowns[item.name]" 
                                        class="pt-1 pb-1 space-y-1 pl-6 border-l-2 border-gray-200 dark:border-gray-700 ml-4"
                                    >
                                        <NavLink 
                                            v-for="subItem in item.dropdownItems" 
                                            :key="subItem.name + '-mobile-editor-sub'" 
                                            :href="route(subItem.routeName)" 
                                            mobile 
                                            @click="handleMobileMenuToggle"
                                            class="px-4 py-2 hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors duration-150"
                                        >
                                            {{ subItem.name }}
                                        </NavLink>
                                    </div>
                                </div>
                                <NavLink 
                                    v-else 
                                    :href="route(item.routeName)" 
                                    :active="item.current ? item.current() : false" 
                                    mobile 
                                    @click="handleMobileMenuToggle"
                                    class="px-4 py-3 hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors duration-150"
                                >
                                    {{ item.name }}
                                </NavLink>
                            </template>
                        </div>
                    </template>

                    <!-- Public Categories Mobile Menu -->
                    <template v-if="!user || !currentRouteIsAdminArea">
                        <div class="mt-2 pt-2 border-t border-gray-200 dark:border-gray-700">
                            <p class="px-4 text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wider mb-1">Categories</p>
                            <template v-for="item in navItemsLeft" :key="item.name + '-mobile-public-left'">
                                <div v-if="item.dropdown">
                                    <button 
                                        @click="toggleMobileDropdown(item.name)" 
                                        class="w-full flex justify-between items-center px-4 py-3 text-left text-base font-medium text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-800 focus:outline-none transition-colors duration-150"
                                    >
                                        <span>{{ item.name }}</span>
                                        <svg 
                                            class="h-5 w-5 transform transition-transform duration-200 text-gray-400" 
                                            :class="{'rotate-180': openMobileDropdowns[item.name]}" 
                                            fill="currentColor" 
                                            viewBox="0 0 20 20"
                                        >
                                            <path fill-rule="evenodd" d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z" clip-rule="evenodd" />
                                        </svg>
                                    </button>
                                    <div 
                                        v-show="openMobileDropdowns[item.name]" 
                                        class="pt-1 pb-1 space-y-1 pl-6 border-l-2 border-gray-200 dark:border-gray-700 ml-4"
                                    >
                                        <NavLink 
                                            v-for="subItemName in item.dropdown" 
                                            :key="subItemName + '-mobile-public-left-sub'" 
                                            :href="route('category', { category: subItemName.toLowerCase().replace(/\s+/g, '-') })" 
                                            mobile 
                                            @click="handleMobileMenuToggle"
                                            class="px-4 py-2 hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors duration-150"
                                        >
                                            {{ subItemName }}
                                        </NavLink>
                                    </div>
                                </div>
                            </template>
                            <template v-for="item in navItemsRight" :key="item.name + '-mobile-public-right'">
                                <div v-if="item.dropdown">
                                    <button 
                                        @click="toggleMobileDropdown(item.name)" 
                                        class="w-full flex justify-between items-center px-4 py-3 text-left text-base font-medium text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-800 focus:outline-none transition-colors duration-150"
                                    >
                                        <span>{{ item.name }}</span>
                                        <svg 
                                            class="h-5 w-5 transform transition-transform duration-200 text-gray-400" 
                                            :class="{'rotate-180': openMobileDropdowns[item.name]}" 
                                            fill="currentColor" 
                                            viewBox="0 0 20 20"
                                        >
                                            <path fill-rule="evenodd" d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z" clip-rule="evenodd" />
                                        </svg>
                                    </button>
                                    <div 
                                        v-show="openMobileDropdowns[item.name]" 
                                        class="pt-1 pb-1 space-y-1 pl-6 border-l-2 border-gray-200 dark:border-gray-700 ml-4"
                                    >
                                        <NavLink 
                                            v-for="subItemName in item.dropdown" 
                                            :key="subItemName + '-mobile-public-right-sub'" 
                                            :href="route('category', { category: subItemName.toLowerCase().replace(/\s+/g, '-') })" 
                                            mobile 
                                            @click="handleMobileMenuToggle"
                                            class="px-4 py-2 hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors duration-150"
                                        >
                                            {{ subItemName }}
                                        </NavLink>
                                    </div>
                                </div>
                            </template>
                        </div>
                    </template>
                </div>

                <!-- Mobile Account Menu -->
                <div class="pt-4 pb-3 border-t border-gray-200 dark:border-gray-700">
                    <div v-if="user" class="px-4">
                        <div class="flex items-center space-x-3">
                            <div class="h-10 w-10 rounded-full bg-gray-200 dark:bg-gray-700 flex items-center justify-center overflow-hidden">
                                <span v-if="!user.profile_photo_path" class="text-sm font-medium text-gray-700 dark:text-gray-300">
                                    {{ user.name.charAt(0).toUpperCase() }}
                                </span>
                                <img v-else :src="user.profile_photo_path" :alt="user.name" class="h-full w-full object-cover">
                            </div>
                            <div>
                                <div class="font-medium text-base text-gray-800 dark:text-gray-200">{{ user.name }}</div>
                                <div class="font-medium text-sm text-gray-500 dark:text-gray-400">{{ user.email }}</div>
                            </div>
                        </div>
                    </div>
                    <div class="mt-3 space-y-1">
                        <template v-if="!user">
                            <template v-for="item in guestAccountNav" :key="item.name + '-mobile-guest'">
                                <NavLink 
                                    :href="route(item.routeName)" 
                                    mobile 
                                    :class="{
                                        'px-4 py-3 bg-gradient-to-r from-primary-500 to-blue-500 text-white font-medium': item.highlight,
                                        'px-4 py-3 hover:bg-gray-100 dark:hover:bg-gray-800': !item.highlight
                                    }"
                                    @click="handleMobileMenuToggle"
                                >
                                    {{ item.name }}
                                </NavLink>
                            </template>
                        </template>
                        <template v-if="user">
                            <template v-for="item in authenticatedUserAccountNav" :key="item.name + '-mobile-account'">
                                <template v-for="subItem in item.dropdownItems" :key="subItem.name + '-mobile-account-sub'">
                                    <NavLink 
                                        :href="route(subItem.routeName)" 
                                        :method="subItem.method" 
                                        :as="subItem.as" 
                                        mobile 
                                        @click="handleMobileMenuToggle"
                                        class="px-4 py-3 hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors duration-150"
                                    >
                                        <div class="flex items-center space-x-2">
                                            <span v-if="subItem.icon" class="material-icons-outlined text-lg">{{ subItem.icon }}</span>
                                            <span>{{ subItem.name }}</span>
                                        </div>
                                    </NavLink>
                                </template>
                            </template>
                        </template>
                    </div>
                </div>
            </div>
        </Transition>
    </header>
</template>

<script setup>
import { Link, usePage } from '@inertiajs/vue3';
import { ref, onMounted, computed, reactive } from 'vue';
import { navItemsLeft, navItemsRight } from '@/utils/navigationItems';
import Dropdown from '@/Components/Dropdown.vue';
import DropdownLink from '@/Components/DropdownLink.vue';
import NavLink from '@/Components/NavLink.vue';

const emit = defineEmits(['toggle-sidebar']);

const isDarkMode = ref(false);

const mobileMenuOpen = ref(false);
const openMobileDropdowns = reactive({});

const toggleMobileDropdown = (itemName) => {
    openMobileDropdowns[itemName] = !openMobileDropdowns[itemName];
};

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

// Initialize theme from localStorage or system preference
onMounted(() => {
    const savedTheme = localStorage.getItem('theme');
    if (savedTheme === 'dark' || (!savedTheme && window.matchMedia('(prefers-color-scheme: light)').matches)) {
        isDarkMode.value = true;
        document.documentElement.classList.add('light');
    } else {
        isDarkMode.value = false;
        document.documentElement.classList.remove('light');
    }
});

const page = usePage();
const user = computed(() => page.props.auth.user);
const isAdmin = computed(() => user.value?.role === 'admin');
const isEditor = computed(() => user.value?.role === 'editor');

const currentRouteIsAdminArea = computed(() => {
    const path = window.location.pathname;
    return path.startsWith('/admin/') || path.startsWith('/editor/');
});

const showPublicDashboardLink = computed(() => {
    return (isAdmin.value || isEditor.value) && !currentRouteIsAdminArea.value;
});

const handleMobileMenuToggle = () => {
    mobileMenuOpen.value = !mobileMenuOpen.value;
    if (user.value && (isAdmin.value || isEditor.value)) {
        emit('toggle-sidebar');
    }
};

const generalNavItems = computed(() => [
    { name: 'Home', routeName: 'home', current: () => route().current('home') },
]);

const adminNavItems = computed(() => {
    if (!isAdmin.value) return [];
    return [
        { name: 'User Management', routeName: 'admin.users.index', current: () => route().current('admin.users.index') },
        {
            name: 'Post Management',
            isDropdown: true,
            dropdownItems: [
                { name: 'All Posts', routeName: 'editor.posts.index', icon: 'article' },
                { name: 'Create New Post', routeName: 'editor.posts.create', icon: 'add_circle_outline' },
                { name: 'Pending Approval', routeName: 'admin.posts.pending', icon: 'hourglass_empty' },
            ]
        },
        {
            name: 'Category Management',
            isDropdown: true,
            dropdownItems: [
                { name: 'Manage Categories', routeName: 'editor.categories.index', icon: 'category' },
                { name: 'Create New Category', routeName: 'editor.categories.create', icon: 'playlist_add' },
            ]
        },
        {
            name: 'Tag Management',
            isDropdown: true,
            dropdownItems: [
                { name: 'Manage Tags', routeName: 'editor.tags.index', icon: 'tag' },
                { name: 'Create New Tag', routeName: 'editor.tags.create', icon: 'add' },
            ]
        },
    ];
});

const editorNavItems = computed(() => {
    if (!isEditor.value || isAdmin.value) return [];
    return [
        {
            name: 'Post Management',
            isDropdown: true,
            dropdownItems: [
                { name: 'All Posts', routeName: 'editor.posts.index', icon: 'article' },
                { name: 'Create New Post', routeName: 'editor.posts.create', icon: 'add_circle_outline' },
            ]
        },
        {
            name: 'Category Management',
            isDropdown: true,
            dropdownItems: [
                { name: 'Manage Categories', routeName: 'editor.categories.index', icon: 'category' },
                { name: 'Create New Category', routeName: 'editor.categories.create', icon: 'playlist_add' },
            ]
        },
        {
            name: 'Tag Management',
            isDropdown: true,
            dropdownItems: [
                { name: 'Manage Tags', routeName: 'editor.tags.index', icon: 'tag' },
                { name: 'Create New Tag', routeName: 'editor.tags.create', icon: 'add' },
            ]
        },
    ];
});

const authenticatedUserAccountNav = computed(() => {
    if (!user.value) return [];
    return [
        { 
            name: user.value.name, 
            isDropdown: true,
            dropdownItems: [
                { name: 'My Profile', routeName: 'profile.view', icon: 'person' },
                { name: 'Account Settings', routeName: 'profile.edit', icon: 'settings' },
                { name: 'Log Out', routeName: 'logout', method: 'post', as: 'button', icon: 'logout' },
            ]
        }
    ];
});

const guestAccountNav = computed(() => {
    if (user.value) return [];
    return [
        { name: 'Log In', routeName: 'login' },
        { name: 'Register', routeName: 'register', highlight: true }
    ];
});
</script>

<style>
.dropdown-enter-active,
.dropdown-leave-active {
    transition: all 0.2s ease;
}

.dropdown-enter-from,
.dropdown-leave-to {
    opacity: 0;
    transform: translateY(-10px);
}

.bg-gradient-to-r {
    background-image: linear-gradient(to right, var(--tw-gradient-stops));
}

:root {
    --color-primary-400: #818cf8;
    --color-primary-500: #6366f1;
    --color-primary-600: #4f46e5;
}

.dark {
    --color-primary-400: #a5b4fc;
    --color-primary-500: #818cf8;
    --color-primary-600: #6366f1;
}
</style>