<template>
    <div>
        <div class="min-h-screen bg-gray-100 dark:bg-gray-900 flex">
            <!-- <Sidebar 
                v-if="auth.user && (isAdmin || isEditor)" 
                :navItems="sidebarNavItems" 
                :isMobileOpen="sidebarOpen"
            /> -->

            <div class="flex-1 flex flex-col overflow-hidden">
                <Navbar @toggle-sidebar="toggleSidebar" />

                <header
                    class="bg-white dark:bg-gray-800 shadow sticky top-0 z-10"
                    v-if="$slots.header"
                >
                    <div class="max-w-7xl mx-auto py-6 px-4 sm:px-6 lg:px-8">
                        <slot name="header" />
                    </div>
                </header>

                <main class="flex-1 overflow-y-auto">
                    <slot />
                </main>
            </div>
        </div>
    </div>
</template>

<script setup>
import { ref, computed } from 'vue';
import {  usePage } from '@inertiajs/vue3';
import Navbar from '@/Components/Layout/Navbar.vue';
import Sidebar from '@/Layouts/Partials/Sidebar.vue';

const sidebarOpen = ref(false);

const page = usePage();
const auth = computed(() => page.props.auth);
const isAdmin = computed(() => page.props.auth.isAdmin);
const isEditor = computed(() => page.props.auth.isEditor);

const getDirectUrl = (path) => {
    return window.location.origin + path;
};

const sidebarNavItems = computed(() => {
    let items = [
        {
            label: 'Dashboard',
            href: getDirectUrl('/admin/dashboard'),
            icon: 'HomeIcon',
            activeRoutes: ['admin.dashboard']
        },
    ];

    if (isAdmin.value || isEditor.value) {
        items.push(
            {
                label: 'Post Management',
                icon: 'DocumentDuplicateIcon',
                activeRoutes: ['editor.posts', 'admin.posts'], 
                children: [
                    {
                        label: 'All Posts',
                        href: getDirectUrl('/editor/posts'),
                        icon: 'ListBulletIcon',
                        activeRoutes: ['editor.posts.index', 'editor.posts.edit', 'editor.posts.show', 'admin.posts.index']
                    },
                    {
                        label: 'Add New Post',
                        href: getDirectUrl('/editor/posts/create'),
                        icon: 'PlusCircleIcon',
                        activeRoutes: ['editor.posts.create']
                    },
                    {
                        label: 'My Drafts',
                        href: getDirectUrl('/editor/posts/drafts'),
                        icon: 'DocumentDuplicateIcon',
                        activeRoutes: ['editor.posts.drafts']
                    },
                    ...(isAdmin.value ? [{
                        label: 'Pending Approval',
                        href: getDirectUrl('/admin/posts/pending'),
                        icon: 'ClockIcon',
                        activeRoutes: ['admin.posts.pending', 'admin.posts.review']
                    }] : []),
                ]
            },
            {
                label: 'Category Management',
                icon: 'RectangleStackIcon',
                activeRoutes: ['editor.categories'],
                children: [
                    {
                        label: 'All Categories',
                        href: getDirectUrl('/editor/categories'),
                        icon: 'ListBulletIcon',
                        activeRoutes: ['editor.categories.index', 'editor.categories.edit', 'editor.categories.show']
                    },
                    {
                        label: 'Add New Category',
                        href: getDirectUrl('/editor/categories/create'),
                        icon: 'PlusCircleIcon',
                        activeRoutes: ['editor.categories.create']
                    },
                ]
            },
            {
                label: 'Tag Management',
                icon: 'TagIcon',
                activeRoutes: ['editor.tags'],
                children: [
                    {
                        label: 'All Tags',
                        href: getDirectUrl('/editor/tags'),
                        icon: 'ListBulletIcon',
                        activeRoutes: ['editor.tags.index', 'editor.tags.edit', 'editor.tags.show']
                    },
                    {
                        label: 'Add New Tag',
                        href: getDirectUrl('/editor/tags/create'),
                        icon: 'PlusCircleIcon',
                        activeRoutes: ['editor.tags.create']
                    },
                ]
            }
        );
    }

    if (isAdmin.value) {
        items.push({
            label: 'User Management',
            icon: 'UsersIcon',
            activeRoutes: ['admin.users'], 
            children: [
                {
                    label: 'All Users',
                    href: getDirectUrl('/admin/users'),
                    icon: 'UserGroupIcon',
                    activeRoutes: ['admin.users.index']
                },
                {
                    label: 'Roles & Permissions',
                    href: '#', 
                    icon: 'ShieldCheckIcon',
                    activeRoutes: ['admin.roles.index'] 
                },
            ]
        });
    }

    return items;
});

const toggleSidebar = () => {
    sidebarOpen.value = !sidebarOpen.value;
};
</script>