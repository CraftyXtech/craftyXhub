<template>
    <header
    style="font-family: 'Gill Sans', 'Gill Sans MT', Calibri, 'Trebuchet MS', sans-serif;"    
    class="bg-white dark:bg-gray-900 py-4 border-b border-gray-200 dark:border-gray-700 text-gray-800 dark:text-gray-200 sticky top-0 z-50">
        <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div class="flex items-center justify-between h-16">
                
                <!-- Left Navigation Block -->
                <nav class="hidden md:flex items-center space-x-6">
                    <!-- General Nav Items (Home) -->
                    <template v-for="item in generalNavItems" :key="item.name">
                        <NavLink :href="route(item.routeName)" :active="item.current ? item.current() : false">
                            {{ item.name }}
                        </NavLink>
                    </template>

                    <!-- Dashboard Link for Admin/Editor (Contextual) -->
                    <template v-if="isAdmin || isEditor">
                        <NavLink 
                            v-if="showPublicDashboardLink"
                            :href="route('admin.dashboard')" 
                            :active="currentRouteIsAdminArea && (page.props.ziggy?.route_name === 'admin.dashboard' || page.props.ziggy?.route_name?.startsWith('admin.dashboard.'))"
                            class="text-sm font-medium"
                        >
                            Dashboard
                        </NavLink>
                    </template>
                    
                    <!-- Public Category Nav (Original navItemsLeft/Right) - Conditionally shown for GUESTS / Public View -->
                    <!-- Condition for this block will be updated in Phase 2 to also show for authenticated users on public pages -->
                     <template v-if="!currentRouteIsAdminArea">
                        <template v-for="item in navItemsLeft" :key="item.name + '-public-left'">
                             <Dropdown align="left" width="48">
                                <template #trigger>
                                    <button class="inline-flex items-center px-1 pt-1 border-b-2 border-transparent text-sm font-medium leading-5 text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300 focus:outline-none focus:border-gray-300 dark:focus:border-gray-700 transition">
                                        {{ item.name }}
                                        <svg class="ms-2 -me-0.5 h-4 w-4" fill="currentColor" viewBox="0 0 20 20"><path fill-rule="evenodd" d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z" clip-rule="evenodd" /></svg>
                                    </button>
                                </template>
                                <template #content>
                                    <DropdownLink v-for="subItemName in item.dropdown" :key="subItemName" :href="route('category', { category: subItemName.toLowerCase().replace(/\s+/g, '-') })">
                                        {{ subItemName }}
                                    </DropdownLink>
                                </template>
                            </Dropdown>
                        </template>
                    </template>
                </nav>

                <!-- Centered Logo -->
                <div class="hidden md:flex flex-grow justify-center">
                    <Link :href="route('home')" class="flex items-center px-2 text-lg font-semibold text-gray-800 dark:text-gray-200 hover:text-primary dark:hover:text-primary-dark transition-colors duration-150 ease-in-out">
                        CraftyXhub
                    </Link>
                </div>

                <!-- Right side: Account Navigation & Dark Mode Toggle -->
                <div class="hidden md:flex items-center space-x-4">
                     <!-- Public Category Nav Right (Only for guests on public pages) -->
                     <!-- Condition for this block will be updated in Phase 2 -->
                    <template v-if="!currentRouteIsAdminArea">
                        <template v-for="item in navItemsRight" :key="item.name + '-public-right'">
                             <Dropdown align="left" width="48">
                                <template #trigger>
                                    <button class="inline-flex items-center px-1 pt-1 border-b-2 border-transparent text-sm font-medium leading-5 text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300 focus:outline-none focus:border-gray-300 dark:focus:border-gray-700 transition">
                                        {{ item.name }}
                                        <svg class="ms-2 -me-0.5 h-4 w-4" fill="currentColor" viewBox="0 0 20 20"><path fill-rule="evenodd" d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z" clip-rule="evenodd" /></svg>
                                    </button>
                                </template>
                                <template #content>
                                    <DropdownLink v-for="subItemName in item.dropdown" :key="subItemName" :href="route('category', { category: subItemName.toLowerCase().replace(/\s+/g, '-') })">
                                        {{ subItemName }}
                                    </DropdownLink>
                                </template>
                            </Dropdown>
                        </template>
                    </template>

                    <template v-if="!user">
                        <template v-for="item in guestAccountNav" :key="item.name">
                             <NavLink :href="route(item.routeName)" :class="{'bg-primary text-white px-3 py-1 rounded-md': item.highlight}">
                                {{ item.name }}
                            </NavLink>
                        </template>
                    </template>
                    <template v-if="user">
                        <template v-for="item in authenticatedUserAccountNav" :key="item.name">
                            <Dropdown align="right" width="48">
                                <template #trigger>
                                    <button class="inline-flex items-center px-1 pt-1 border-b-2 border-transparent text-sm font-medium leading-5 text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300 focus:outline-none focus:border-gray-300 dark:focus:border-gray-700 transition">
                                        {{ item.name }}
                                        <svg class="ms-2 -me-0.5 h-4 w-4" fill="currentColor" viewBox="0 0 20 20"><path fill-rule="evenodd" d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z" clip-rule="evenodd" /></svg>
                                    </button>
                                </template>
                                <template #content>
                                    <DropdownLink v-for="subItem in item.dropdownItems" :key="subItem.name" :href="route(subItem.routeName)" :method="subItem.method" :as="subItem.as">
                                        {{ subItem.name }}
                                    </DropdownLink>
                                </template>
                            </Dropdown>
                        </template>
                    </template>
                    <button @click="toggleDarkMode" class="p-2 rounded-full text-gray-500 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-700">
                        <span class="material-icons text-base">{{ isDarkMode ? 'light_mode' : 'dark_mode' }}</span>
                    </button>
                </div>

                <!-- Mobile menu button and logo -->
                <div class="-me-2 flex items-center md:hidden flex-grow justify-between">
                    <!-- Mobile: Left Spacer (or first nav item if any) -->
                    <div>
                         <button @click="handleMobileMenuToggle" class="inline-flex items-center justify-center p-2 rounded-md text-gray-400 dark:text-gray-500 hover:text-gray-500 dark:hover:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-700 focus:outline-none focus:bg-gray-100 dark:focus:bg-gray-700 focus:text-gray-500 dark:focus:text-gray-400 transition duration-150 ease-in-out">
                            <svg class="h-6 w-6" stroke="currentColor" fill="none" viewBox="0 0 24 24">
                                <path :class="{'hidden': mobileMenuOpen, 'inline-flex': !mobileMenuOpen }" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16" />
                                <path :class="{'hidden': !mobileMenuOpen, 'inline-flex': mobileMenuOpen }" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                            </svg>
                        </button>
                    </div>
                    <!-- Mobile: Centered Logo -->
                    <Link :href="route('home')" class="text-lg font-semibold text-gray-800 dark:text-gray-200 hover:text-primary dark:hover:text-primary-dark">
                        CraftyXhub
                    </Link>
                    <!-- Mobile: Right Dark Mode Toggle -->
                     <button @click="toggleDarkMode" class="p-2 rounded-full text-gray-500 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-700">
                        <span class="material-icons text-base">{{ isDarkMode ? 'light_mode' : 'dark_mode' }}</span>
                    </button>
                </div>
            </div>
        </div>

        <!-- Mobile Menu (Content from previous step - assumed correct) -->
        <div :class="{'block': mobileMenuOpen, 'hidden': !mobileMenuOpen}" class="md:hidden fixed inset-x-0 top-[73px] z-40 bg-white dark:bg-gray-900 border-t border-gray-200 dark:border-gray-700 shadow-lg max-h-[calc(100vh-73px)] overflow-y-auto">
            <div class="pt-2 pb-3 space-y-1">
                <template v-for="item in generalNavItems" :key="item.name + '-mobile-general'">
                    <NavLink :href="route(item.routeName)" :active="item.current ? item.current() : false" mobile @click="handleMobileMenuToggle">
                        {{ item.name }}
                    </NavLink>
                </template>
                <template v-if="isAdmin">
                    <div class="mt-2 pt-2 border-t border-gray-200 dark:border-gray-700">
                        <p class="px-3 text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wider mb-1">Admin Tools</p>
                        <template v-for="item in adminNavItems" :key="item.name + '-mobile-admin'">
                             <div v-if="item.isDropdown">
                                <button @click="toggleMobileDropdown(item.name)" class="w-full flex justify-between items-center px-3 py-2 text-left text-base font-medium text-gray-600 dark:text-gray-300 hover:text-gray-800 dark:hover:text-gray-100 hover:bg-gray-50 dark:hover:bg-gray-800 focus:outline-none focus:text-gray-800 dark:focus:text-gray-100 focus:bg-gray-50 dark:focus:bg-gray-800 transition duration-150 ease-in-out">
                                    <span>{{ item.name }}</span>
                                    <svg class="h-5 w-5 transform transition-transform duration-150" :class="{'rotate-180': openMobileDropdowns[item.name]}" fill="currentColor" viewBox="0 0 20 20"><path fill-rule="evenodd" d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z" clip-rule="evenodd" /></svg>
                                </button>
                                <div v-show="openMobileDropdowns[item.name]" class="pt-1 pb-1 space-y-1 pl-3 border-l-2 border-gray-200 dark:border-gray-700 ml-3">
                                    <NavLink v-for="subItem in item.dropdownItems" :key="subItem.name + '-mobile-admin-sub'" :href="route(subItem.routeName)" mobile @click="handleMobileMenuToggle">
                                        {{ subItem.name }}
                                    </NavLink>
                                </div>
                            </div>
                            <NavLink v-else :href="route(item.routeName)" :active="item.current ? item.current() : false" mobile @click="handleMobileMenuToggle">
                                {{ item.name }}
                            </NavLink>
                        </template>
                    </div>
                </template>
                <template v-else-if="isEditor">
                     <div class="mt-2 pt-2 border-t border-gray-200 dark:border-gray-700">
                        <p class="px-3 text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wider mb-1">Editor Tools</p>
                        <template v-for="item in editorNavItems" :key="item.name + '-mobile-editor'">
                            <div v-if="item.isDropdown">
                                <button @click="toggleMobileDropdown(item.name)" class="w-full flex justify-between items-center px-3 py-2 text-left text-base font-medium text-gray-600 dark:text-gray-300 hover:text-gray-800 dark:hover:text-gray-100 hover:bg-gray-50 dark:hover:bg-gray-800 focus:outline-none focus:text-gray-800 dark:focus:text-gray-100 focus:bg-gray-50 dark:focus:bg-gray-800 transition duration-150 ease-in-out">
                                    <span>{{ item.name }}</span>
                                    <svg class="h-5 w-5 transform transition-transform duration-150" :class="{'rotate-180': openMobileDropdowns[item.name]}" fill="currentColor" viewBox="0 0 20 20"><path fill-rule="evenodd" d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z" clip-rule="evenodd" /></svg>
                            </button>
                                <div v-show="openMobileDropdowns[item.name]" class="pt-1 pb-1 space-y-1 pl-3 border-l-2 border-gray-200 dark:border-gray-700 ml-3">
                                    <NavLink v-for="subItem in item.dropdownItems" :key="subItem.name + '-mobile-editor-sub'" :href="route(subItem.routeName)" mobile @click="handleMobileMenuToggle">
                                        {{ subItem.name }}
                                    </NavLink>
                                </div>
                            </div>
                            <NavLink v-else :href="route(item.routeName)" :active="item.current ? item.current() : false" mobile @click="handleMobileMenuToggle">
                            {{ item.name }}
                            </NavLink>
                    </template>
                </div>
                </template>
                <template v-if="!user">
                    <div class="mt-2 pt-2 border-t border-gray-200 dark:border-gray-700">
                        <p class="px-3 text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wider mb-1">Categories</p>
                        <template v-for="item in navItemsLeft" :key="item.name + '-mobile-public-left'">
                            <div v-if="item.dropdown">
                                <button @click="toggleMobileDropdown(item.name)" class="w-full flex justify-between items-center px-3 py-2 text-left text-base font-medium text-gray-600 dark:text-gray-300 hover:text-gray-800 dark:hover:text-gray-100 hover:bg-gray-50 dark:hover:bg-gray-800 focus:outline-none focus:text-gray-800 dark:focus:text-gray-100 focus:bg-gray-50 dark:focus:bg-gray-800 transition duration-150 ease-in-out">
                                    <span>{{ item.name }}</span>
                                    <svg class="h-5 w-5 transform transition-transform duration-150" :class="{'rotate-180': openMobileDropdowns[item.name]}" fill="currentColor" viewBox="0 0 20 20"><path fill-rule="evenodd" d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z" clip-rule="evenodd" /></svg>
                                </button>
                                <div v-show="openMobileDropdowns[item.name]" class="pt-1 pb-1 space-y-1 pl-3 border-l-2 border-gray-200 dark:border-gray-700 ml-3">
                                    <NavLink v-for="subItemName in item.dropdown" :key="subItemName + '-mobile-public-left-sub'" :href="route('category', { category: subItemName.toLowerCase().replace(/\s+/g, '-') })" mobile @click="handleMobileMenuToggle">
                                        {{ subItemName }}
                                    </NavLink>
                                </div>
                            </div>
                        </template>
                        <template v-for="item in navItemsRight" :key="item.name + '-mobile-public-right'">
                            <div v-if="item.dropdown">
                                <button @click="toggleMobileDropdown(item.name)" class="w-full flex justify-between items-center px-3 py-2 text-left text-base font-medium text-gray-600 dark:text-gray-300 hover:text-gray-800 dark:hover:text-gray-100 hover:bg-gray-50 dark:hover:bg-gray-800 focus:outline-none focus:text-gray-800 dark:focus:text-gray-100 focus:bg-gray-50 dark:focus:bg-gray-800 transition duration-150 ease-in-out">
                                    <span>{{ item.name }}</span>
                                    <svg class="h-5 w-5 transform transition-transform duration-150" :class="{'rotate-180': openMobileDropdowns[item.name]}" fill="currentColor" viewBox="0 0 20 20"><path fill-rule="evenodd" d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z" clip-rule="evenodd" /></svg>
                            </button>
                                <div v-show="openMobileDropdowns[item.name]" class="pt-1 pb-1 space-y-1 pl-3 border-l-2 border-gray-200 dark:border-gray-700 ml-3">
                                    <NavLink v-for="subItemName in item.dropdown" :key="subItemName + '-mobile-public-right-sub'" :href="route('category', { category: subItemName.toLowerCase().replace(/\s+/g, '-') })" mobile @click="handleMobileMenuToggle">
                                        {{ subItemName }}
                                    </NavLink>
                                </div>
                            </div>
                        </template>
                        </div>
                    </template>
            </div>
            <div class="pt-4 pb-3 border-t border-gray-200 dark:border-gray-700">
                <div v-if="user" class="px-4">
                    <div class="font-medium text-base text-gray-800 dark:text-gray-200">{{ user.name }}</div>
                    <div class="font-medium text-sm text-gray-500 dark:text-gray-400">{{ user.email }}</div>
                </div>
                <div class="mt-3 space-y-1">
                    <template v-if="!user">
                        <template v-for="item in guestAccountNav" :key="item.name + '-mobile-guest'">
                            <NavLink :href="route(item.routeName)" mobile :class="{'bg-primary text-white': item.highlight}" @click="handleMobileMenuToggle">
                                {{ item.name }}
                            </NavLink>
                        </template>
                    </template>
                    <template v-if="user">
                        <template v-for="item in authenticatedUserAccountNav" :key="item.name + '-mobile-account'">
                             <template v-for="subItem in item.dropdownItems" :key="subItem.name + '-mobile-account-sub'">
                                <NavLink :href="route(subItem.routeName)" :method="subItem.method" :as="subItem.as" mobile @click="handleMobileMenuToggle">
                                    {{ subItem.name }}
                                </NavLink>
                             </template>
                                </template>
                    </template>
                </div>
            </div>
        </div>
    </header>
</template>

<script setup>
import { Link, usePage } from '@inertiajs/vue3';
import { ref, onMounted, computed, reactive, watch } from 'vue';
import { navItemsLeft, navItemsRight, getAuthItems } from '@/Shared/navigationItems';
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

// --- New Role-Based Navigation Items Definition ---

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
                { name: 'All Posts', routeName: 'editor.posts.index' },
                { name: 'Create New Post', routeName: 'editor.posts.create' },
                { name: 'Pending Approval', routeName: 'admin.posts.pending' },
            ]
        },
        {
            name: 'Category Management',
            isDropdown: true,
            dropdownItems: [
                { name: 'Manage Categories', routeName: 'editor.categories.index' },
                { name: 'Create New Category', routeName: 'editor.categories.create' },
            ]
        },
        {
            name: 'Tag Management',
            isDropdown: true,
            dropdownItems: [
                { name: 'Manage Tags', routeName: 'editor.tags.index' },
                { name: 'Create New Tag', routeName: 'editor.tags.create' },
            ]
        },
        // { name: 'System Settings', routeName: 'admin.settings.index', current: () => route().current('admin.settings.index') }, // Placeholder, ensure route exists
    ];
});

const editorNavItems = computed(() => {
    if (!isEditor.value || isAdmin.value) return []; // Editors who are also admins use adminNavItems
    return [
        // Editors link to admin.dashboard which will show their contextualized view
        {
            name: 'Post Management',
            isDropdown: true,
            dropdownItems: [
                { name: 'All Posts', routeName: 'editor.posts.index' },
                { name: 'Create New Post', routeName: 'editor.posts.create' },
            ]
        },
        {
            name: 'Category Management',
            isDropdown: true,
            dropdownItems: [
                { name: 'Manage Categories', routeName: 'editor.categories.index' },
                { name: 'Create New Category', routeName: 'editor.categories.create' },
            ]
        },
        {
            name: 'Tag Management',
            isDropdown: true,
            dropdownItems: [
                { name: 'Manage Tags', routeName: 'editor.tags.index' },
                { name: 'Create New Tag', routeName: 'editor.tags.create' },
            ]
        },
    ];
});

const authenticatedUserAccountNav = computed(() => { // Renamed to avoid conflict
    if (!user.value) return [];
    return [
        { 
            name: user.value.name, 
            isDropdown: true,
            dropdownItems: [
                { name: 'My Profile', routeName: 'profile.view' },
                { name: 'Account Settings', routeName: 'profile.edit' },
                { name: 'Log Out', routeName: 'logout', method: 'post', as: 'button' },
            ]
        }
    ];
});

const guestAccountNav = computed(() => { // Renamed to avoid conflict
    if (user.value) return [];
    return [
        { name: 'Log In', routeName: 'login' },
        { name: 'Register', routeName: 'register', highlight: true }
    ];
});
</script>