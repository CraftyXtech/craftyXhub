<script setup>
import AuthenticatedLayout from '@/Layouts/AuthenticatedLayout.vue';
import { Head, Link, router, usePage } from '@inertiajs/vue3';
import { ref, computed, onMounted } from 'vue';
import RoleManagementModal from '@/Pages/Admin/Partials/RoleManagementModal.vue';
import LoadingIndicator from '@/Components/LoadingIndicator.vue';
import ErrorMessage from '@/Components/ErrorMessage.vue';

const props = defineProps({
    users: Object,
    filters: Object,
});

// Get user role for conditional rendering
const page = usePage();
const currentUserRole = computed(() => page.props.auth.user.role);
const isAdmin = computed(() => currentUserRole.value === 'admin');

// Show/hide role management modal
const showRoleModal = ref(false);
const selectedUser = ref(null);

// Loading and error states
const loading = ref({
    users: false,
    deleteUser: null, // User ID being deleted
});

const errors = ref({
    users: null,
    deleteUser: null,
});

// Search filter
const search = ref(props.filters?.search || '');
const debouncedSearch = computed(() => search.value);

// Function to load user data
const loadUsers = (params = {}) => {
    if (!isAdmin.value) return; // Only admins can load all users
    loading.value.users = true;
    errors.value.users = null;
    
    router.get(route('admin.users.index'), {
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

// Delete user method
const confirmAndDeleteUser = (user) => {
    if (!isAdmin.value) return;
    if (!confirm(`Are you sure you want to delete the user ${user.name}? This action cannot be undone.`)) {
        return;
    }
    // Use Inertia link/router for deletion
    router.delete(route('admin.users.destroy', user.id), {
        preserveScroll: true,
        onStart: () => {
            loading.value.deleteUser = user.id;
        },
        onSuccess: () => {
            // Success handled by redirect
        },
        onError: (error) => {
            errors.value.deleteUser = error.message || 'Failed to delete user.';
            console.error("Error deleting user:", error);
        },
        onFinish: () => {
            loading.value.deleteUser = null;
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
    closeRoleModal();
    
    // Refresh the user list after role update
    setTimeout(() => {
        loadUsers();
    }, 500);
};

// Handle search input changes
const handleSearchInput = () => {
    if (isAdmin.value) {
        loadUsers();
    }
};

// Function to retry loading data after an error
const retryLoadUsers = () => {
    if (isAdmin.value) {
        loadUsers();
    }
};

// Format large numbers for display
const formatNumber = (num) => {
    if (num === undefined || num === null) return '0';
    return new Intl.NumberFormat().format(num);
};
</script>

<template>
    <Head title="User Management" />

    <AuthenticatedLayout>
        <template #header>
            <h2 class="font-semibold text-xl text-gray-800 dark:text-gray-200 leading-tight">
                User Management
            </h2>
        </template>

        <div class="py-12">
            <div class="max-w-7xl mx-auto sm:px-6 lg:px-8 space-y-6">
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
                            
                            <template v-else-if="users">
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
                                        <tr v-if="users.length === 0">
                                            <td colspan="4" class="px-6 py-4 text-center text-gray-500 dark:text-gray-400">
                                                No users found matching your criteria.
                                            </td>
                                        </tr>
                                        <tr v-for="user in users" :key="user.id" class="hover:bg-gray-50 dark:hover:bg-gray-700">
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
                            </template>
                            <div v-else class="text-gray-500 dark:text-gray-400 text-center py-4">
                                No user data available.
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <!-- Role Management Modal -->
        <RoleManagementModal 
            v-if="isAdmin"
            :show="showRoleModal" 
            :user="selectedUser" 
            @close="closeRoleModal" 
            @update="handleRoleUpdate" 
        />
    </AuthenticatedLayout>
</template> 