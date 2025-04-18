<script setup>
import AuthenticatedLayout from '@/Layouts/AuthenticatedLayout.vue';
import { Head, Link, router } from '@inertiajs/vue3';
import { ref, computed, onMounted } from 'vue';
import RoleManagementModal from './Partials/RoleManagementModal.vue';
import Pagination from '@/Components/Pagination.vue';
import LoadingIndicator from '@/Components/LoadingIndicator.vue';
import ErrorMessage from '@/Components/ErrorMessage.vue';
import axios from 'axios';

const props = defineProps({
    userCount: {
        type: Number,
        default: 0,
    },
    userStats: {
        type: Object,
        default: () => ({}),
    },
    users: Object, // Paginated users from backend
    filters: Object, // Search filters
    contentOverview: Object, // Content statistics
    viewTrends: Object, // View trends data
    contentNeedingApproval: Object, // Content needing approval
});

// Show/hide role management modal
const showRoleModal = ref(false);
const selectedUser = ref(null);

// Loading and error states
const loading = ref({
    users: false,
    contentOverview: false,
    deleteUser: null, // User ID being deleted
});
const errors = ref({
    users: null,
    contentOverview: null,
    deleteUser: null,
});

// Search filter
const search = ref(props.filters.search || '');
const debouncedSearch = computed(() => search.value);

// Function to load user data
const loadUsers = (params = {}) => {
    loading.value.users = true;
    errors.value.users = null;
    
    router.get(route('admin.dashboard'), {
        ...props.filters,
        ...params,
        search: debouncedSearch.value,
    }, {
        preserveState: true,
        preserveScroll: true,
        onError: (error) => {
            errors.value.users = "Failed to load users. " + error;
        },
        onFinish: () => {
            loading.value.users = false;
        }
    });
};

// Function to delete a user
const deleteUser = async (user) => {
    if (!confirm(`Are you sure you want to delete the user ${user.name}?`)) {
        return;
    }
    
    loading.value.deleteUser = user.id;
    errors.value.deleteUser = null;
    
    try {
        await axios.delete(route('admin.users.delete', user.id));
        loadUsers(); // Reload the user list
    } catch (error) {
        errors.value.deleteUser = "Failed to delete user: " + (error.response?.data?.message || error.message);
    } finally {
        loading.value.deleteUser = null;
    }
};

// Role management modal functions
const openRoleModal = (user) => {
    selectedUser.value = user;
    showRoleModal.value = true;
};

const closeRoleModal = () => {
    showRoleModal.value = false;
    selectedUser.value = null;
};

const handleRoleUpdate = ({ userId, role }) => {
    // This is now handled by the modal component
    // Will make a proper API call
    closeRoleModal();
    
    // Refresh the user list to reflect changes
    setTimeout(() => {
        loadUsers();
    }, 500);
};

// Handle search input changes
const handleSearchInput = () => {
    loadUsers();
};

// Function to retry loading data after an error
const retryLoadUsers = () => {
    loadUsers();
};

// Period selection for view trends
const changePeriod = (period) => {
    router.get(route('admin.dashboard'), {
        ...props.filters,
        period
    }, {
        preserveState: true,
        preserveScroll: true
    });
};

// Format large numbers for display
const formatNumber = (num) => {
    if (num === undefined || num === null) return '0';
    return new Intl.NumberFormat().format(num);
};
</script>

<template>
    <Head title="Admin Dashboard" />

    <AuthenticatedLayout>
        <template #header>
            <h2 class="font-semibold text-xl text-gray-800 dark:text-gray-200 leading-tight">Admin Dashboard</h2>
        </template>

        <div class="py-12">
            <div class="max-w-7xl mx-auto sm:px-6 lg:px-8 space-y-6">
                <!-- Role Management Modal -->
                <RoleManagementModal 
                    :show="showRoleModal" 
                    :user="selectedUser" 
                    @close="closeRoleModal" 
                    @update="handleRoleUpdate" 
                />
                
                <!-- User Management Section -->
                <div class="bg-white dark:bg-gray-800 overflow-hidden shadow-sm sm:rounded-lg">
                        <div class="p-6">
                        <h3 class="text-lg font-medium text-gray-900 dark:text-gray-100 mb-4">
                            User Management
                        </h3>
                            
                            <div class="mb-4">
                            <div class="relative">
                                    <input
                                    v-model="search"
                                    @input="handleSearchInput"
                                    class="w-full rounded-md border-gray-300 dark:border-gray-700 dark:bg-gray-900 dark:text-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
                                    placeholder="Search users by name or email..."
                                />
                                <div class="absolute inset-y-0 right-0 flex items-center pr-3">
                                    <svg v-if="loading.users" class="animate-spin h-5 w-5 text-gray-400" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                                        <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                                        <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                                    </svg>
                                </div>
                            </div>
                        </div>
                        
                        <!-- Error Message -->
                        <ErrorMessage 
                            v-if="errors.users" 
                            :message="errors.users"
                            :showRetry="true"
                            @retry="retryLoadUsers"
                        />
                            
                            <!-- User Table -->
                            <div class="mt-4 overflow-x-auto">
                            <LoadingIndicator v-if="loading.users && !users" />
                            
                            <template v-else>
                                <table class="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
                                    <thead class="bg-gray-50 dark:bg-gray-700">
                                        <tr>
                                            <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Name</th>
                                            <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Email</th>
                                            <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Role</th>
                                            <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Actions</th>
                                        </tr>
                                    </thead>
                                    <tbody class="bg-white dark:bg-gray-800 divide-y divide-gray-200 dark:divide-gray-700">
                                        <tr v-if="users && users.data.length === 0">
                                            <td colspan="4" class="px-6 py-4 text-center text-gray-500 dark:text-gray-400">
                                                No users found matching your criteria.
                                            </td>
                                        </tr>
                                        <tr v-for="user in users?.data" :key="user.id" class="hover:bg-gray-50 dark:hover:bg-gray-700">
                                            <td class="px-6 py-4 whitespace-nowrap">
                                                <div class="text-sm font-medium text-gray-900 dark:text-gray-100">{{ user.name }}</div>
                                            </td>
                                            <td class="px-6 py-4 whitespace-nowrap">
                                                <div class="text-sm text-gray-500 dark:text-gray-400">{{ user.email }}</div>
                                            </td>
                                            <td class="px-6 py-4 whitespace-nowrap">
                                                <span class="px-2 py-1 inline-flex text-xs leading-5 font-semibold rounded-full" 
                                                    :class="{
                                                        'bg-purple-100 text-purple-800 dark:bg-purple-900 dark:text-purple-200': user.role === 'admin',
                                                        'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200': user.role === 'editor',
                                                        'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200': user.role === 'user'
                                                    }">
                                                    {{ user.role.charAt(0).toUpperCase() + user.role.slice(1) }}
                                                </span>
                                            </td>
                                            <td class="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                                                <button 
                                                    class="text-indigo-600 hover:text-indigo-900 dark:text-indigo-400 dark:hover:text-indigo-300 mr-2"
                                                    @click="openRoleModal(user)"
                                                >
                                                    Change Role
                                                </button>
                                                <button 
                                                    class="text-red-600 hover:text-red-900 dark:text-red-400 dark:hover:text-red-300"
                                                    @click="deleteUser(user)"
                                                    :disabled="loading.deleteUser === user.id"
                                                >
                                                    <span v-if="loading.deleteUser === user.id">Deleting...</span>
                                                    <span v-else>Delete</span>
                                                </button>
                                                <div v-if="errors.deleteUser && loading.deleteUser === user.id" class="text-red-500 text-xs mt-1">
                                                    {{ errors.deleteUser }}
                                                </div>
                                            </td>
                                        </tr>
                                    </tbody>
                                </table>
                                
                                <!-- Pagination -->
                                <div class="mt-4" v-if="users && users.links && users.links.length > 3">
                                    <Pagination :links="users.links" />
                                </div>
                            </template>
                        </div>
                        
                        <!-- User Stats Summary -->
                        <div class="mt-6 grid grid-cols-1 md:grid-cols-4 gap-4" v-if="userStats">
                            <div class="bg-gray-100 dark:bg-gray-700 p-4 rounded-lg">
                                <p class="text-sm text-gray-500 dark:text-gray-400">Total Users</p>
                                <p class="text-2xl font-bold text-gray-900 dark:text-gray-100">{{ formatNumber(userStats.total) }}</p>
                            </div>
                            <div class="bg-gray-100 dark:bg-gray-700 p-4 rounded-lg">
                                <p class="text-sm text-gray-500 dark:text-gray-400">Admins</p>
                                <p class="text-2xl font-bold text-gray-900 dark:text-gray-100">{{ formatNumber(userStats.admins) }}</p>
                            </div>
                            <div class="bg-gray-100 dark:bg-gray-700 p-4 rounded-lg">
                                <p class="text-sm text-gray-500 dark:text-gray-400">Editors</p>
                                <p class="text-2xl font-bold text-gray-900 dark:text-gray-100">{{ formatNumber(userStats.editors) }}</p>
                            </div>
                            <div class="bg-gray-100 dark:bg-gray-700 p-4 rounded-lg">
                                <p class="text-sm text-gray-500 dark:text-gray-400">Regular Users</p>
                                <p class="text-2xl font-bold text-gray-900 dark:text-gray-100">{{ formatNumber(userStats.regular_users) }}</p>
                            </div>
                            </div>
                        </div>
                    </div>

                <!-- Content Overview -->
                <div class="grid grid-cols-1 md:grid-cols-2 gap-6 mt-6">
                    <div class="bg-white dark:bg-gray-800 overflow-hidden shadow-sm sm:rounded-lg">
                        <div class="p-6">
                            <h3 class="text-lg font-medium text-gray-900 dark:text-gray-100 mb-4">Content Overview</h3>
                            <LoadingIndicator v-if="!contentOverview" />
                            <div v-else-if="contentOverview" class="grid grid-cols-2 gap-4">
                                <div class="p-4 bg-gray-100 dark:bg-gray-700 rounded">
                                    <p class="text-sm text-gray-600 dark:text-gray-400">Total Posts</p>
                                    <p class="text-2xl font-bold text-gray-900 dark:text-gray-100">{{ formatNumber(contentOverview.totalPosts) }}</p>
                                </div>
                                <div class="p-4 bg-gray-100 dark:bg-gray-700 rounded">
                                    <p class="text-sm text-gray-600 dark:text-gray-400">Total Views</p>
                                    <p class="text-2xl font-bold text-gray-900 dark:text-gray-100">{{ formatNumber(contentOverview.totalViews) }}</p>
                                </div>
                                <div class="p-4 bg-gray-100 dark:bg-gray-700 rounded">
                                    <p class="text-sm text-gray-600 dark:text-gray-400">Published Posts</p>
                                    <p class="text-2xl font-bold text-gray-900 dark:text-gray-100">{{ formatNumber(contentOverview.publishedPosts) }}</p>
                                </div>
                                <div class="p-4 bg-gray-100 dark:bg-gray-700 rounded">
                                    <p class="text-sm text-gray-600 dark:text-gray-400">Unique Viewers</p>
                                    <p class="text-2xl font-bold text-gray-900 dark:text-gray-100">{{ formatNumber(contentOverview.uniqueViewers) }}</p>
                                </div>
                            </div>
                            
                            <!-- Top Posts Preview -->
                            <div v-if="contentOverview && contentOverview.mostViewedPosts && contentOverview.mostViewedPosts.length > 0" class="mt-6">
                                <h4 class="text-md font-medium text-gray-800 dark:text-gray-200 mb-2">Top Performing Posts</h4>
                                <ul class="divide-y divide-gray-200 dark:divide-gray-700">
                                    <li v-for="post in contentOverview.mostViewedPosts" :key="post.id" class="py-2">
                                        <div class="flex justify-between">
                                            <Link 
                                                :href="route('blog.show', post.slug)" 
                                                class="text-sm text-indigo-600 dark:text-indigo-400 hover:underline truncate max-w-xs"
                                            >
                                                {{ post.title }}
                                            </Link>
                                            <span class="text-sm text-gray-500 dark:text-gray-400">{{ formatNumber(post.view_count) }} views</span>
                                        </div>
                                    </li>
                                </ul>
                            </div>
                            
                            <div class="mt-4">
                                <Link 
                                    :href="route('admin.content.analytics')" 
                                    class="text-sm text-indigo-600 dark:text-indigo-400 hover:underline"
                                >
                                    View detailed content analytics →
                                </Link>
                            </div>
                        </div>
                    </div>

                    <!-- Content Needing Approval -->
                    <div class="bg-white dark:bg-gray-800 overflow-hidden shadow-sm sm:rounded-lg">
                        <div class="p-6">
                            <h3 class="text-lg font-medium text-gray-900 dark:text-gray-100 mb-4">Content Needing Approval</h3>
                            <LoadingIndicator v-if="!contentNeedingApproval" />
                            
                            <template v-else-if="contentNeedingApproval && contentNeedingApproval.pendingPosts && contentNeedingApproval.pendingPosts.length > 0">
                                <h4 class="text-md font-medium text-gray-800 dark:text-gray-200 mb-2">Posts Under Review</h4>
                                <ul class="divide-y divide-gray-200 dark:divide-gray-700">
                                    <li v-for="post in contentNeedingApproval.pendingPosts" :key="post.id" class="py-2">
                                        <div class="flex justify-between">
                                            <span class="text-sm text-gray-700 dark:text-gray-300 truncate">{{ post.title }}</span>
                                            <span class="text-sm text-gray-500 dark:text-gray-400">by {{ post.author ? post.author.name : 'Unknown' }}</span>
                                        </div>
                                    </li>
                                </ul>
                                
                                <div class="mt-4">
                                    <Link 
                                        :href="route('admin.content.approval')" 
                                        class="text-sm text-indigo-600 dark:text-indigo-400 hover:underline"
                                    >
                                        Review all pending content →
                                    </Link>
                                </div>
                            </template>
                            
                            <template v-else-if="contentNeedingApproval && contentNeedingApproval.pendingComments && contentNeedingApproval.pendingComments.length > 0">
                                <h4 class="text-md font-medium text-gray-800 dark:text-gray-200 mb-2">Comments Pending Approval</h4>
                                <ul class="divide-y divide-gray-200 dark:divide-gray-700">
                                    <li v-for="comment in contentNeedingApproval.pendingComments" :key="comment.id" class="py-2">
                                        <div class="text-sm text-gray-700 dark:text-gray-300 truncate">
                                            {{ comment.user ? comment.user.name : 'Anonymous' }} on "{{ comment.post ? comment.post.title : 'Unknown Post' }}"
                                        </div>
                                    </li>
                                </ul>
                                
                                <div class="mt-4">
                                    <Link 
                                        :href="route('admin.content.approval')" 
                                        class="text-sm text-indigo-600 dark:text-indigo-400 hover:underline"
                                    >
                                        Review all pending content →
                                    </Link>
                                </div>
                            </template>
                            
                            <div v-else class="text-center py-6 text-gray-500 dark:text-gray-400">
                                No content currently needs approval.
                            </div>
                        </div>
                        </div>
                    </div>

                <!-- View Trends -->
                <div v-if="viewTrends" class="bg-white dark:bg-gray-800 overflow-hidden shadow-sm sm:rounded-lg">
                        <div class="p-6">
                        <div class="flex justify-between items-center mb-4">
                            <h3 class="text-lg font-medium text-gray-900 dark:text-gray-100">
                                View Trends
                            </h3>
                            <div class="flex space-x-2">
                                <button 
                                    v-for="period in ['day', 'week', 'month', 'year']" 
                                    :key="period"
                                    @click="changePeriod(period)"
                                    class="px-3 py-1 text-sm rounded-md"
                                    :class="[
                                        props.filters.period === period 
                                            ? 'bg-indigo-100 text-indigo-800 dark:bg-indigo-900 dark:text-indigo-200' 
                                            : 'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-200 hover:bg-gray-200 dark:hover:bg-gray-600'
                                    ]"
                                >
                                    {{ period.charAt(0).toUpperCase() + period.slice(1) }}
                                </button>
                            </div>
                        </div>
                        
                        <div class="h-80 w-full">
                            <!-- Placeholder for Chart.js implementation -->
                            <div v-if="viewTrends.labels && viewTrends.data" class="relative h-full">
                                <!-- Simple representation of the chart data -->
                                <div class="absolute inset-0 flex items-end">
                                    <div 
                                        v-for="(value, index) in viewTrends.data" 
                                        :key="index"
                                        class="bg-indigo-500 dark:bg-indigo-400 mx-1 rounded-t-sm"
                                        :style="{
                                            height: `${Math.max(5, (value / Math.max(...viewTrends.data)) * 100)}%`,
                                            width: `${100 / viewTrends.data.length}%`
                                        }"
                                    ></div>
                                </div>
                                
                                <!-- X axis labels -->
                                <div class="absolute bottom-0 left-0 right-0 flex justify-between text-xs text-gray-500 dark:text-gray-400 pt-2 border-t border-gray-200 dark:border-gray-700">
                                    <div>{{ viewTrends.labels[0] }}</div>
                                    <div>{{ viewTrends.labels[Math.floor(viewTrends.labels.length / 2)] }}</div>
                                    <div>{{ viewTrends.labels[viewTrends.labels.length - 1] }}</div>
                                </div>
                            </div>
                            
                            <div v-else class="flex justify-center items-center h-full">
                                <LoadingIndicator />
                            </div>
                        </div>
                        
                        <div class="mt-4">
                            <Link 
                                :href="route('admin.content.analytics')" 
                                class="text-sm text-indigo-600 dark:text-indigo-400 hover:underline"
                            >
                                View detailed analytics →
                            </Link>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </AuthenticatedLayout>
</template> 