<script setup>
import { ref, computed } from 'vue';
import ApplicationLogo from '@/Components/ApplicationLogo.vue';
import Dropdown from '@/Components/Dropdown.vue';
import DropdownLink from '@/Components/DropdownLink.vue';
import NavLink from '@/Components/NavLink.vue';
import ResponsiveNavLink from '@/Components/ResponsiveNavLink.vue';
import { Link } from '@inertiajs/vue3';
import { navItemsLeft, navItemsRight, getAuthItems } from '@/Shared/navigationItems';
import QnABot from '@/Components/Shared/QnABot.vue';

const showingNavigationDropdown = ref(false);

// Compute auth items
const authItems = computed(() => getAuthItems());
</script>

<template>
    <div>
        <div class="min-h-screen bg-gray-100">
            <nav
                class="border-b border-gray-100 bg-white"
            >
                <!-- Primary Navigation Menu -->
                <div class="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
                    <div class="flex h-16 justify-between">
                        <!-- Left Navigation Links -->
                        <div class="hidden items-center space-x-8 sm:-my-px sm:flex">
                             <template v-for="item in navItemsLeft" :key="item.name">
                                <Dropdown v-if="item.dropdown" align="left" width="48">
                                    <template #trigger>
                                        <button class="inline-flex items-center border-b-2 border-transparent px-1 pt-1 text-sm font-medium leading-5 text-gray-500 transition duration-150 ease-in-out hover:border-gray-300 hover:text-gray-700 focus:border-gray-300 focus:text-gray-700 focus:outline-none">
                                            {{ item.name }}
                                            <svg class="ms-2 -me-0.5 h-4 w-4" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
                                                <path fill-rule="evenodd" d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z" clip-rule="evenodd" />
                                            </svg>
                                        </button>
                                    </template>
                                    <template #content>
                                        <DropdownLink v-for="subItem in item.dropdown" :key="subItem" href="#">
                                            {{ subItem }}
                                        </DropdownLink>
                                    </template>
                                </Dropdown>
                                <NavLink v-else :href="item.href || '#'">
                                    {{ item.name }}
                                </NavLink>
                            </template>
                        </div>

                        <!-- Logo -->
                        <div class="flex shrink-0 items-center">
                            <Link :href="route('dashboard')">
                                <ApplicationLogo
                                    class="block h-9 w-auto fill-current text-gray-800"
                                />
                                <!-- Optional: If logo doesn't contain text -->
                                <!-- <span class="ml-2 text-lg font-semibold text-gray-800">CraftyXhub</span> -->
                            </Link>
                        </div>

                        <!-- Right Navigation Links & Settings -->
                        <div class="hidden sm:ms-6 sm:flex sm:items-center">
                             <div class="hidden items-center space-x-8 sm:-my-px sm:flex">
                                <template v-for="item in navItemsRight" :key="item.name">
                                    <Dropdown v-if="item.dropdown" align="right" width="48">
                                         <template #trigger>
                                            <button class="inline-flex items-center border-b-2 border-transparent px-1 pt-1 text-sm font-medium leading-5 text-gray-500 transition duration-150 ease-in-out hover:border-gray-300 hover:text-gray-700 focus:border-gray-300 focus:text-gray-700 focus:outline-none">
                                                {{ item.name }}
                                                <svg class="ms-2 -me-0.5 h-4 w-4" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
                                                    <path fill-rule="evenodd" d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z" clip-rule="evenodd" />
                                                </svg>
                                            </button>
                                        </template>
                                        <template #content>
                                            <DropdownLink v-for="subItem in item.dropdown" :key="subItem" href="#">
                                                {{ subItem }}
                                            </DropdownLink>
                                        </template>
                                    </Dropdown>
                                     <NavLink v-else :href="item.href || '#'">
                                        {{ item.name }}
                                    </NavLink>
                                </template>
                            </div>

                            <!-- Auth Items -->
                            <div class="hidden items-center space-x-4 sm:-my-px sm:flex">
                                <template v-for="item in authItems" :key="item.name">
                                    <Dropdown v-if="item.dropdown" align="right" width="48">
                                        <template #trigger>
                                            <button class="inline-flex items-center rounded-md border border-transparent bg-white px-3 py-2 text-sm font-medium leading-4 text-gray-500 transition duration-150 ease-in-out hover:text-gray-700 focus:outline-none">
                                                {{ item.name }}
                                                <svg class="ms-2 -me-0.5 h-4 w-4" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
                                                    <path fill-rule="evenodd" d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z" clip-rule="evenodd" />
                                                </svg>
                                            </button>
                                        </template>
                                        <template #content>
                                            <DropdownLink :href="route('profile.view')">Profile</DropdownLink>
                                            <DropdownLink :href="route('logout')" method="post" as="button">Log Out</DropdownLink>
                                        </template>
                                    </Dropdown>
                                    <Link v-else
                                        :href="item.href"
                                        :class="[
                                            item.highlight
                                                ? 'bg-indigo-600 text-white hover:bg-indigo-500'
                                                : 'text-gray-500 hover:text-gray-700 border-2 border-transparent hover:border-gray-300',
                                            'px-4 py-2 rounded-md text-sm font-medium transition duration-150 ease-in-out'
                                        ]"
                                    >
                                        {{ item.name }}
                                    </Link>
                                </template>
                            </div>
                        </div>

                        <!-- Hamburger -->
                        <div class="-me-2 flex items-center sm:hidden">
                            <button
                                @click="
                                    showingNavigationDropdown =
                                        !showingNavigationDropdown
                                "
                                class="inline-flex items-center justify-center rounded-md p-2 text-gray-400 transition duration-150 ease-in-out hover:bg-gray-100 hover:text-gray-500 focus:bg-gray-100 focus:text-gray-500 focus:outline-none"
                            >
                                <svg
                                    class="h-6 w-6"
                                    stroke="currentColor"
                                    fill="none"
                                    viewBox="0 0 24 24"
                                >
                                    <path
                                        :class="{
                                            hidden: showingNavigationDropdown,
                                            'inline-flex':
                                                !showingNavigationDropdown,
                                        }"
                                        stroke-linecap="round"
                                        stroke-linejoin="round"
                                        stroke-width="2"
                                        d="M4 6h16M4 12h16M4 18h16"
                                    />
                                    <path
                                        :class="{
                                            hidden: !showingNavigationDropdown,
                                            'inline-flex':
                                                showingNavigationDropdown,
                                        }"
                                        stroke-linecap="round"
                                        stroke-linejoin="round"
                                        stroke-width="2"
                                        d="M6 18L18 6M6 6l12 12"
                                    />
                                </svg>
                            </button>
                        </div>
                    </div>
                </div>

                <!-- Responsive Navigation Menu -->
                <div
                    :class="{
                        block: showingNavigationDropdown,
                        hidden: !showingNavigationDropdown,
                    }"
                    class="sm:hidden"
                >
                    <div class="space-y-1 pb-3 pt-2">
                         <!-- Responsive Links -->
                        <template v-for="item in [...navItemsLeft, ...navItemsRight, ...authItems]" :key="item.name">
                             <div v-if="item.dropdown" class="pt-2 pb-1 border-t border-gray-200">
                                <div class="px-4 font-medium text-base text-gray-800">{{ item.name }}</div>
                                <ResponsiveNavLink v-for="subItem in item.dropdown" :key="subItem" href="#">
                                    {{ subItem }}
                                </ResponsiveNavLink>
                            </div>
                             <ResponsiveNavLink v-else :href="item.href || '#'">
                                {{ item.name }}
                            </ResponsiveNavLink>
                        </template>
                    </div>
                </div>
            </nav>

            <!-- Page Heading -->
            <header
                class="bg-white shadow"
                v-if="$slots.header"
            >
                <div class="mx-auto max-w-7xl px-4 py-6 sm:px-6 lg:px-8">
                    <slot name="header" />
                </div>
            </header>

            <!-- Page Content -->
            <main>
                <slot />
            </main>

            <!-- QnA Bot Component -->
            <QnABot />

        </div>
    </div>
</template>
