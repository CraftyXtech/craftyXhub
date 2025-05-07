<script setup>
import AuthenticatedLayout from '@/Layouts/AuthenticatedLayout.vue';
import { Head, Link, router, usePage } from '@inertiajs/vue3';
import { ref, computed, onMounted, watch } from 'vue';
import RoleManagementModal from './Partials/RoleManagementModal.vue';
// import Pagination from '@/Components/Pagination.vue';
import LoadingIndicator from '@/Components/LoadingIndicator.vue';
import ErrorMessage from '@/Components/ErrorMessage.vue';

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
    recentPosts: Array, // Recent posts (added for editor functionality) - Will be site-wide for admin
    pendingReviews: Array, // Pending reviews (added for editor functionality) - Likely part of contentNeedingApproval
    analytics: Object, // Editor analytics - Will be site-wide for admin, or use contentOverview
    // New props might be added by AdminDashboardController for category/tag summaries
    categorySummary: {
        type: Array,
        default: () => [],
    },
    tagSummary: {
        type: Array,
        default: () => [],
    }
});

// Get user role for conditional rendering
const page = usePage();
const currentUserRole = computed(() => page.props.auth.user.role);

const isAdmin = computed(() => currentUserRole.value === 'admin');
const isEditor = computed(() => currentUserRole.value === 'editor');

// Content management sections visible to both Admin and Editor (or just Admin if Editor has a more restricted view)
// For now, assuming if you can see this dashboard, and you are an editor, you see content tools.
const canManageContent = computed(() => isAdmin.value || isEditor.value);


// Show/hide role management modal
const showRoleModal = ref(false);
const selectedUser = ref(null);

// Loading and error states
const loading = ref({
    users: false,
    contentOverview: false,
    deleteUser: null, // User ID being deleted
    posts: false, 
    analytics: false, 
});
const errors = ref({
    users: null,
    contentOverview: null,
    deleteUser: null,
    posts: null, 
    analytics: null, 
});

// Search filter
const search = ref(props.filters.search || '');
const debouncedSearch = computed(() => search.value);

// Function to load user data
const loadUsers = (params = {}) => {
    if (!isAdmin.value) return; // Only admins can load all users
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

// Refactored delete user method
const confirmAndDeleteUser = (user) => {
    if (!isAdmin.value) return;
    if (!confirm(`Are you sure you want to delete the user ${user.name}? This action cannot be undone.`)) {
        return;
    }
    // Use Inertia link/router for deletion
    router.delete(route('admin.users.delete', user.id), {
        preserveScroll: true,
        onStart: () => {
            // Optionally set a loading state for this specific user
            loading.value.deleteUser = user.id;
        },
        onSuccess: () => {
            // No need to manually call loadUsers(), the redirect handles the refresh.
            // Optionally show a success notification based on flashed session data
        },
        onError: (errors) => {
            // Handle errors, maybe display a notification
             errors.value.deleteUser = errors.message || 'Failed to delete user.';
             console.error("Error deleting user:", errors);
        },
        onFinish: () => {
             loading.value.deleteUser = null; // Reset loading state
        },
    });
};

// Role management modal functions
const openRoleModal = (user) => {
    if (!isAdmin.value) return;
    selectedUser.value = user;
    showRoleModal.value = true;
};

const closeRoleModal = () => {
    showRoleModal.value = false;
    selectedUser.value = null;
};

const handleRoleUpdate = ({ userId, role }) => {
    if (!isAdmin.value) return;
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
    if (isAdmin.value) { // Assuming search is for users, restrict to admin
    loadUsers();
    }
};

// Function to retry loading data after an error
const retryLoadUsers = () => {
    if (isAdmin.value) {
    loadUsers();
    }
};

// Period selection for view trends
const changePeriod = (period) => {
    // This might be an admin-only feature or adaptable for editors if they see trends
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

// Format date to readable format (added for editor functionality)
const formatDate = (dateString) => {
    if (!dateString) return 'N/A';
    const date = new Date(dateString);
    return new Intl.DateTimeFormat('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit',
    }).format(date);
};

// Get status badge class (added for editor functionality)
const getStatusClass = (status) => {
    switch (status) {
        case 'published':
            return 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200';
        case 'draft':
            return 'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-200';
        case 'under_review':
            return 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200';
        case 'scheduled':
            return 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200';
        case 'rejected':
            return 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200';
        default:
            return 'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-200';
    }
};

// Format status text (added for editor functionality)
const formatStatus = (status) => {
    switch (status) {
        case 'published':
            return 'Published';
        case 'draft':
            return 'Draft';
        case 'under_review':
            return 'Under Review';
        case 'scheduled':
            return 'Scheduled';
        case 'rejected':
            return 'Rejected';
        default:
            return status.charAt(0).toUpperCase() + status.slice(1);
    }
};

// Function to retry loading data after an error (generic for sections)
const retryLoadSectionData = (sectionKey) => {
    // This function might need more context or specific reload actions per section
    // For now, a general refresh might be okay for some data, or it triggers specific loaders
    loading.value[sectionKey] = true;
    errors.value[sectionKey] = null;
    router.visit(route('admin.dashboard'), { // Or a more specific route if data is segmented
        preserveScroll: true,
        onSuccess: () => loading.value[sectionKey] = false,
        onError: (err) => {
            errors.value[sectionKey] = "Failed to reload " + sectionKey;
            loading.value[sectionKey] = false;
        }
    });
};

// Helper function to handle direct navigation to admin routes when on editor routes
const navigateToAdminRoute = (routeName) => {
    console.log(`Direct navigation to admin route: ${routeName}`);
    const currentRouteName = page.props.ziggy.route_name;
    const isOnEditorRoute = currentRouteName.startsWith('editor.');
    
    if (isOnEditorRoute && isAdmin.value) {
        console.log('Using direct router.visit for admin route from editor context');
        router.visit(route(routeName));
        return false;
    }
    
    return true;
};
</script>

<template>
    <Head :title="isAdmin ? 'Admin Dashboard' : 'Editor Dashboard'" />

    <AuthenticatedLayout>
        <template #header>
            <h2 class="font-semibold text-xl text-gray-800 dark:text-gray-200 leading-tight">
                {{ isAdmin ? 'Admin Dashboard' : 'Editor Dashboard' }}
            </h2>
        </template>

        <div class="py-12">
            <div class="max-w-7xl mx-auto sm:px-6 lg:px-8 space-y-6">
                
                <!-- Welcome Banner & Quick Actions (Visible to Admins and Editors) -->
                <div v-if="canManageContent" class="bg-indigo-600 dark:bg-indigo-800 shadow-sm sm:rounded-lg">
                    <div class="px-4 py-6 sm:px-6">
                        <h2 class="text-2xl font-bold text-white">
                            Welcome, {{ $page.props.auth.user.name }}!
                        </h2>
                        <p class="mt-1 text-indigo-100">
                            {{ isAdmin ? 'Manage users, content, and site performance from here.' : 'Manage your content from here.' }}
                        </p>
                        
                        <!-- Quick actions buttons removed as these functions are now accessed through the sidebar -->
                    </div>
                </div>

                <!-- Editor-specific Content Dashboard -->
                <div v-if="isEditor && !isAdmin" class="bg-white dark:bg-gray-800 overflow-hidden shadow-sm sm:rounded-lg">
                    <div class="p-6">
                        <h3 class="text-lg font-medium text-gray-900 dark:text-gray-100 mb-4">My Content Overview</h3>
                        <div v-if="loading.contentOverview"><LoadingIndicator /></div>
                        <ErrorMessage v-else-if="errors.contentOverview" :message="errors.contentOverview" @retry="retryLoadSectionData('contentOverview')" />
                        <div v-else-if="contentOverview" class="grid grid-cols-1 md:grid-cols-4 gap-4">
                            <div class="bg-gray-100 dark:bg-gray-700 p-4 rounded-lg">
                                <p class="text-sm text-gray-500 dark:text-gray-400">Total Posts</p>
                                <p class="text-2xl font-bold text-gray-900 dark:text-gray-100">{{ formatNumber(contentOverview.totalPosts) }}</p>
                            </div>
                            <div class="bg-gray-100 dark:bg-gray-700 p-4 rounded-lg">
                                <p class="text-sm text-gray-500 dark:text-gray-400">Published</p>
                                <p class="text-2xl font-bold text-gray-900 dark:text-gray-100">{{ formatNumber(contentOverview.publishedPosts) }}</p>
                            </div>
                            <div class="bg-gray-100 dark:bg-gray-700 p-4 rounded-lg">
                                <p class="text-sm text-gray-500 dark:text-gray-400">Drafts</p>
                                <p class="text-2xl font-bold text-gray-900 dark:text-gray-100">{{ formatNumber(contentOverview.draftPosts) }}</p>
                            </div>
                            <div class="bg-gray-100 dark:bg-gray-700 p-4 rounded-lg">
                                <p class="text-sm text-gray-500 dark:text-gray-400">Under Review</p>
                                <p class="text-2xl font-bold text-gray-900 dark:text-gray-100">{{ formatNumber(contentOverview.pendingReviewPosts || 0) }}</p>
                            </div>
                            <div class="bg-gray-100 dark:bg-gray-700 p-4 rounded-lg md:col-span-2">
                                <p class="text-sm text-gray-500 dark:text-gray-400">Total Views</p>
                                <p class="text-2xl font-bold text-gray-900 dark:text-gray-100">{{ formatNumber(contentOverview.totalViews) }}</p>
                            </div>
                            <div class="bg-gray-100 dark:bg-gray-700 p-4 rounded-lg md:col-span-2">
                                <p class="text-sm text-gray-500 dark:text-gray-400">Total Comments</p>
                                <p class="text-2xl font-bold text-gray-900 dark:text-gray-100">{{ formatNumber(contentOverview.totalComments) }}</p>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Editor View Trends (Editor-specific) -->
                <div v-if="isEditor && !isAdmin && viewTrends" class="bg-white dark:bg-gray-800 overflow-hidden shadow-sm sm:rounded-lg">
                    <div class="p-6">
                        <h3 class="text-lg font-medium text-gray-900 dark:text-gray-100 mb-4">My Content Performance</h3>
                        
                        <!-- Period selection -->
                        <div class="mb-4">
                            <label for="period" class="block text-sm font-medium text-gray-700 dark:text-gray-300">Period:</label>
                            <select id="period" v-model="filters.period" @change="changePeriod($event.target.value)" class="mt-1 block w-full pl-3 pr-10 py-2 text-base border-gray-300 dark:border-gray-600 dark:bg-gray-700 dark:text-white focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm rounded-md">
                                <option value="day">Today</option>
                                <option value="week">Last 7 Days</option>
                                <option value="month">Last 30 Days</option>
                                <option value="year">Last Year</option>
                            </select>
                        </div>
                        
                        <div v-if="viewTrends && viewTrends.labels && viewTrends.labels.length">
                            <!-- Simplified chart or data display -->
                            <div class="h-40 flex items-end space-x-1 bg-gray-50 dark:bg-gray-700 p-2 rounded">
                                <div
                                    v-for="(count, index) in viewTrends.data"
                                    :key="index"
                                    :style="`height: ${Math.max(10, (count / (Math.max(...viewTrends.data) || 1)) * 100)}%`"
                                    class="bg-indigo-500 dark:bg-indigo-600 w-full rounded-t"
                                    :title="`${viewTrends.labels[index]}: ${formatNumber(count)} views`"
                                ></div>
                            </div>
                            <div class="mt-2 flex justify-between text-xs text-gray-500 dark:text-gray-400">
                                <span>{{ viewTrends.labels[0] }}</span>
                                <span v-if="viewTrends.labels.length > 2">{{ viewTrends.labels[Math.floor(viewTrends.labels.length / 2)] }}</span>
                                <span v-if="viewTrends.labels.length > 1">{{ viewTrends.labels[viewTrends.labels.length - 1] }}</span>
                            </div>
                        </div>
                        <div v-else class="text-sm text-gray-500 dark:text-gray-400">No trend data available for the selected period.</div>
                    </div>
                </div>

                <!-- Editor Recent Posts -->
                <div v-if="isEditor && !isAdmin && recentPostsList && recentPostsList.length" class="bg-white dark:bg-gray-800 overflow-hidden shadow-sm sm:rounded-lg">
                    <div class="p-6">
                        <h3 class="text-lg font-medium text-gray-900 dark:text-gray-100 mb-4">My Recent Posts</h3>
                        <ul class="space-y-3">
                            <li v-for="post in recentPostsList" :key="post.id" class="border-b dark:border-gray-700 pb-2 last:border-b-0">
                                <div class="flex justify-between items-center">
                                    <div>
                                        <Link :href="route('editor.posts.edit', post.id)" class="text-indigo-600 hover:underline dark:text-indigo-400">{{ post.title }}</Link>
                                        <span class="px-2 py-0.5 rounded-full text-xs ml-2" :class="getStatusClass(post.status)">{{ formatStatus(post.status) }}</span>
                                    </div>
                                    <div class="text-xs text-gray-500 dark:text-gray-400">
                                        Last updated {{ formatDate(post.updated_at) }}
                                    </div>
                                </div>
                            </li>
                        </ul>
                        <div class="mt-4">
                            <Link :href="route('editor.posts.index')" class="text-indigo-600 hover:underline dark:text-indigo-400 text-sm">View all posts →</Link>
                        </div>
                    </div>
                </div>

                <!-- Content Management Hub (Visible to Admins and Editors) - Removed as these functions are now accessed through the sidebar -->
                
                <!-- Role Management Modal (Admin Only) -->
                <RoleManagementModal 
                    v-if="isAdmin"
                    :show="showRoleModal" 
                    :user="selectedUser" 
                    @close="closeRoleModal" 
                    @update="handleRoleUpdate" 
                />
                
                <!-- User Management Section (Admin Only) -->
                <div v-if="isAdmin" class="bg-white dark:bg-gray-800 overflow-hidden shadow-sm sm:rounded-lg">
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
                                                    @click="confirmAndDeleteUser(user)" 
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
                                    <!-- <Pagination :links="users.links" /> -->
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

                <!-- Site Analytics & Overview (Admin Only) -->
                <div v-if="isAdmin" class="grid grid-cols-1 md:grid-cols-2 gap-6">
                <!-- Content Overview -->
                    <div class="bg-white dark:bg-gray-800 overflow-hidden shadow-sm sm:rounded-lg">
                        <div class="p-6">
                            <h3 class="text-lg font-medium text-gray-900 dark:text-gray-100 mb-4">Content Overview</h3>
                            <div v-if="loading.contentOverview"><LoadingIndicator /></div>
                            <ErrorMessage v-else-if="errors.contentOverview" :message="errors.contentOverview" @retry="retryLoadSectionData('contentOverview')" />
                            <div v-else-if="contentOverview" class="space-y-2 text-sm">
                                <p>Total Posts: {{ formatNumber(contentOverview.totalPosts) }}</p>
                                <p>Published Posts: {{ formatNumber(contentOverview.publishedPosts) }}</p>
                                <p>Total Views: {{ formatNumber(contentOverview.totalViews) }}</p>
                                <!-- Add more stats as needed -->
                            </div>
                        </div>
                    </div>

                    <!-- View Trends -->
                    <div class="bg-white dark:bg-gray-800 overflow-hidden shadow-sm sm:rounded-lg">
                        <div class="p-6">
                            <h3 class="text-lg font-medium text-gray-900 dark:text-gray-100 mb-4">View Trends</h3>
                            <!-- Existing View Trends implementation, ensure it's admin-centric -->
                            <!-- Example: Period selection -->
                             <div class="mb-4">
                                <label for="period" class="block text-sm font-medium text-gray-700 dark:text-gray-300">Period:</label>
                                <select id="period" v-model="filters.period" @change="changePeriod($event.target.value)" class="mt-1 block w-full pl-3 pr-10 py-2 text-base border-gray-300 dark:border-gray-600 dark:bg-gray-700 dark:text-white focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm rounded-md">
                                    <option value="day">Today</option>
                                    <option value="week">Last 7 Days</option>
                                    <option value="month">Last 30 Days</option>
                                    <option value="year">Last Year</option>
                                </select>
                            </div>
                            <div v-if="viewTrends && viewTrends.labels && viewTrends.labels.length">
                                <!-- Simplified chart or data display -->
                                <div class="h-40 flex items-end space-x-1 bg-gray-50 dark:bg-gray-700 p-2 rounded">
                                    <div 
                                        v-for="(count, index) in viewTrends.data" 
                                        :key="index"
                                        :style="`height: ${Math.max(10, (count / (Math.max(...viewTrends.data) || 1)) * 100)}%`"
                                        class="bg-indigo-500 dark:bg-indigo-600 w-full rounded-t"
                                        :title="`${viewTrends.labels[index]}: ${formatNumber(count)} views`"
                                    ></div>
                                </div>
                                <div class="mt-2 flex justify-between text-xs text-gray-500 dark:text-gray-400">
                                    <span>{{ viewTrends.labels[0] }}</span>
                                    <span v-if="viewTrends.labels.length > 2">{{ viewTrends.labels[Math.floor(viewTrends.labels.length / 2)] }}</span>
                                    <span v-if="viewTrends.labels.length > 1">{{ viewTrends.labels[viewTrends.labels.length - 1] }}</span>
                                </div>
                            </div>
                             <div v-else class="text-sm text-gray-500 dark:text-gray-400">No trend data available for selected period.</div>
                        </div>
                    </div>
                </div>

                <!-- Recent Site Activity (Placeholder - Admin Only) -->
                <div v-if="isAdmin && props.recentPosts && props.recentPosts.length">
                    <div class="bg-white dark:bg-gray-800 overflow-hidden shadow-sm sm:rounded-lg">
                        <div class="p-6">
                            <h3 class="text-lg font-medium text-gray-900 dark:text-gray-100 mb-4">Recent Site Posts</h3>
                            <ul class="space-y-3">
                                <li v-for="post in props.recentPosts.slice(0,5)" :key="post.id" class="border-b dark:border-gray-700 pb-2 last:border-b-0">
                                    <Link :href="route('posts.show', post.slug)" class="text-indigo-600 hover:underline dark:text-indigo-400" target="_blank">{{ post.title }}</Link>
                                     <span class="px-2 py-0.5 rounded-full text-xs ml-2" :class="getStatusClass(post.status)">{{ formatStatus(post.status) }}</span>
                                    <p class="text-xs text-gray-500 dark:text-gray-400">By {{ post.author ? post.author.name : 'N/A' }} - Last updated {{ formatDate(post.updated_at) }}</p>
                                </li>
                            </ul>
                        </div>
                    </div>
                </div>

            </div>
        </div>
    </AuthenticatedLayout>
</template> 