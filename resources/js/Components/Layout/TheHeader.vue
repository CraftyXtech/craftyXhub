<script setup>
import { Link } from '@inertiajs/vue3';
// Import shared items and necessary components
import { navItemsLeft, navItemsRight } from '@/Shared/navigationItems';
import Dropdown from '@/Components/Dropdown.vue';
import DropdownLink from '@/Components/DropdownLink.vue';
import NavLink from '@/Components/NavLink.vue';
</script>

<template>
    <header class="bg-white py-4 border-b border-gray-200">
        <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div class="flex items-center">
                <!-- Left navigation - Using AuthenticatedLayout structure -->
                <nav class="flex-1 hidden md:flex items-center justify-end space-x-8">
                    <template v-for="item in navItemsLeft" :key="item.name">
                        <Dropdown v-if="item.dropdown" align="left" width="48">
                            <template #trigger>
                                <button class="inline-flex items-center px-1 pt-1 border-b-2 border-transparent text-sm font-medium leading-5 text-gray-500 hover:text-gray-700 hover:border-gray-300 focus:outline-none focus:text-gray-700 focus:border-gray-300 transition duration-150 ease-in-out">
                                    {{ item.name }}
                                    <svg class="ms-2 -me-0.5 h-4 w-4" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
                                        <path fill-rule="evenodd" d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z" clip-rule="evenodd" />
                                    </svg>
                                </button>
                            </template>
                            <template #content>
                                <DropdownLink v-for="subItem in item.dropdown" :key="subItem" href="#"> <!-- Replace # with actual links -->
                                    {{ subItem }}
                                </DropdownLink>
                            </template>
                        </Dropdown>
                        <NavLink v-else href="#"> <!-- Replace # with actual links -->
                            {{ item.name }}
                        </NavLink>
                    </template>
                </nav>

                <!-- Center logo -->
                <div class="text-center mx-4">
                    <Link :href="route('home')" class="font-heading text-2xl text-primary inline-block">
                        CraftyXhub
                    </Link>
                </div>
                
                <!-- Right navigation - Using AuthenticatedLayout structure -->
                 <nav class="flex-1 hidden md:flex items-center space-x-8">
                    <template v-for="item in navItemsRight" :key="item.name">
                        <Dropdown v-if="item.dropdown" align="right" width="48">
                            <template #trigger>
                                <button class="inline-flex items-center px-1 pt-1 border-b-2 border-transparent text-sm font-medium leading-5 text-gray-500 hover:text-gray-700 hover:border-gray-300 focus:outline-none focus:text-gray-700 focus:border-gray-300 transition duration-150 ease-in-out">
                                    {{ item.name }}
                                    <svg class="ms-2 -me-0.5 h-4 w-4" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
                                        <path fill-rule="evenodd" d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z" clip-rule="evenodd" />
                                    </svg>
                                </button>
                            </template>
                            <template #content>
                                <DropdownLink v-for="subItem in item.dropdown" :key="subItem" href="#"> <!-- Replace # with actual links -->
                                    {{ subItem }}
                                </DropdownLink>
                            </template>
                        </Dropdown>
                        <NavLink v-else href="#"> <!-- Replace # with actual links -->
                            {{ item.name }}
                        </NavLink>
                    </template>
                </nav>
                
                <!-- Mobile menu button (remains unchanged for now) -->
                <div class="md:hidden flex justify-between w-full">
                    <Link :href="route('home')" class="font-heading text-2xl text-primary">
                        CraftyXhub
                    </Link>
                    <button class="text-gray-800">
                        <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16" />
                        </svg>
                    </button>
                </div>
            </div>
        </div>
    </header>
</template> 