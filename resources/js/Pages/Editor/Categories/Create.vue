<script setup>
import { Head, router, usePage } from '@inertiajs/vue3';
import AuthenticatedLayout from '@/Layouts/AuthenticatedLayout.vue';
import CategoryForm from './Form.vue'; // Changed from Form.vue to CategoryForm.vue for clarity
import { computed } from 'vue';

// Define props that might be passed from the controller (e.g., permissions)
const props = defineProps({
    // categories: Array, // Not needed for create, but might be for Form if it had a parent selector
    canPublish: Boolean, // Example, might be canCreateCategory or similar
});

const page = usePage();
const currentUserRole = computed(() => page.props.auth.user.role);
const isAdmin = computed(() => currentUserRole.value === 'admin');

const pageTitle = computed(() =>
    isAdmin.value ? 'Admin | Create Category' : 'Editor | Create Category'
);
const headerTitle = computed(() =>
    isAdmin.value ? 'Create New Category (Admin)' : 'Create New Category'
);

const handleCancel = () => {
    router.visit(route('editor.categories.index'));
};

// Form submission is handled by the Form component itself via its submitForm method
// The controller will redirect on success.
</script>

<template>
    <Head :title="pageTitle" />

    <AuthenticatedLayout>
        <template #header>
            <h2 class="font-semibold text-xl text-gray-800 dark:text-gray-200 leading-tight">
                {{ headerTitle }}
            </h2>
        </template>

        <div class="py-12">
            <div class="max-w-3xl mx-auto sm:px-6 lg:px-8">
                <div class="bg-white dark:bg-gray-800 overflow-hidden shadow-sm sm:rounded-lg">
                    <div class="p-6 md:p-8">
                        <CategoryForm
                            @cancel="handleCancel"
                            />
                    </div>
                </div>
            </div>
        </div>
    </AuthenticatedLayout>
</template> 