<script setup>
import { ref, watch } from 'vue';
import Modal from '@/Components/Modal.vue';
import InputLabel from '@/Components/InputLabel.vue';
import PrimaryButton from '@/Components/PrimaryButton.vue';
import SecondaryButton from '@/Components/SecondaryButton.vue';
import DangerButton from '@/Components/DangerButton.vue';
import { router } from '@inertiajs/vue3';

const props = defineProps({
    show: {
        type: Boolean,
        default: false,
    },
    user: {
        type: Object,
        default: () => ({}),
    },
});

const emit = defineEmits(['close', 'update']);

const selectedRole = ref('');
const processing = ref(false);
const formError = ref('');
const successMessage = ref('');

// Reset form when modal opens with a new user
watch(() => props.user, (newUser) => {
    if (newUser) {
        selectedRole.value = newUser.role || '';
        formError.value = '';
        successMessage.value = '';
    }
});

// Reset form when modal visibility changes
watch(() => props.show, (visible) => {
    if (!visible) {
        // Reset form on close
        formError.value = '';
        successMessage.value = '';
    }
});

const close = () => {
    emit('close');
};

const updateRole = () => {
    // Validation
    if (!selectedRole.value) {
        formError.value = 'Please select a role.';
        return;
    }

    processing.value = true;
    
    // Make API call to update the user's role
    router.patch(route('admin.users.update-role', { user: props.user.id }), {
        role: selectedRole.value,
    }, {
        preserveScroll: true,
        onSuccess: () => {
            processing.value = false;
            successMessage.value = `User role updated to ${selectedRole.value}`;
            
            // Emit update event to parent component
            emit('update', { userId: props.user.id, role: selectedRole.value });
            
            // Optionally close the modal after success
            // setTimeout(close, 1500);
        },
        onError: (errors) => {
            processing.value = false;
            formError.value = errors.role || 'Error updating user role. Please try again.';
        }
    });
};
</script>

<template>
    <Modal :show="show" @close="close">
        <div class="p-6">
            <h2 class="text-lg font-medium text-gray-900 dark:text-gray-100">
                Edit User Role
            </h2>

            <p class="mt-1 text-sm text-gray-600 dark:text-gray-400" v-if="user.name">
                Update role for {{ user.name }} ({{ user.email }})
            </p>

            <!-- Form Content -->
            <div class="mt-6">
                <InputLabel for="role" value="Select Role" />
                
                <!-- Role Selection -->
                <div class="mt-2 space-y-2">
                    <div class="flex items-center">
                        <input 
                            id="role-user" 
                            type="radio" 
                            name="role" 
                            value="user" 
                            v-model="selectedRole"
                            class="h-4 w-4 text-indigo-600 focus:ring-indigo-500"
                        />
                        <label for="role-user" class="ml-2 block text-sm text-gray-900 dark:text-gray-100">
                            User
                        </label>
                    </div>
                    
                    <div class="flex items-center">
                        <input 
                            id="role-editor" 
                            type="radio" 
                            name="role" 
                            value="editor" 
                            v-model="selectedRole"
                            class="h-4 w-4 text-indigo-600 focus:ring-indigo-500"
                        />
                        <label for="role-editor" class="ml-2 block text-sm text-gray-900 dark:text-gray-100">
                            Editor
                        </label>
                    </div>
                    
                    <div class="flex items-center">
                        <input 
                            id="role-admin" 
                            type="radio" 
                            name="role" 
                            value="admin" 
                            v-model="selectedRole"
                            class="h-4 w-4 text-indigo-600 focus:ring-indigo-500"
                        />
                        <label for="role-admin" class="ml-2 block text-sm text-gray-900 dark:text-gray-100">
                            Admin
                        </label>
                    </div>
                </div>
                
                <!-- Error Message -->
                <p v-if="formError" class="mt-2 text-sm text-red-600 dark:text-red-400">
                    {{ formError }}
                </p>

                <!-- Success Message -->
                <p v-if="successMessage" class="mt-2 text-sm text-green-600 dark:text-green-400">
                    {{ successMessage }}
                </p>
            </div>

            <!-- Form Actions -->
            <div class="mt-6 flex justify-end space-x-3">
                <SecondaryButton @click="close">
                    Cancel
                </SecondaryButton>
                
                <PrimaryButton 
                    :class="{ 'opacity-25': processing }" 
                    :disabled="processing"
                    @click="updateRole"
                >
                    Update Role
                </PrimaryButton>
            </div>
        </div>
    </Modal>
</template> 